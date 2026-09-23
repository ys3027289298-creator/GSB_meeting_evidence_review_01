import logging
from typing import List, Dict, Any, Optional
import torch

logger = logging.getLogger(__name__)


class SpeakerDiarizer:
    def __init__(self, auth_token: Optional[str] = None):
        self.auth_token = auth_token
        self._pipeline = None
        logger.info("Initializing speaker diarization service")

    @property
    def pipeline(self):
        if self._pipeline is None and self.auth_token and self.auth_token != "placeholder":
            try:
                from pyannote.audio import Pipeline
                logger.info("Loading pyannote speaker diarization pipeline")
                self._pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=self.auth_token
                )
                logger.info("Speaker diarization pipeline loaded")
            except Exception as e:
                logger.warning(f"Failed to load pyannote pipeline: {e}")
                self._pipeline = None
        return self._pipeline

    def diarize(self, audio_path: str) -> List[Dict[str, Any]]:
        if self.pipeline is None:
            logger.warning("Pyannote pipeline not available, using mock diarization")
            return self._mock_diarize(audio_path)

        logger.info(f"Running speaker diarization on: {audio_path}")
        diarization = self.pipeline(audio_path)
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                'speaker': speaker,
                'start_time': turn.start,
                'end_time': turn.end,
            })
        logger.info(f"Diarization completed, {len(segments)} segments")
        return segments

    def _mock_diarize(self, audio_path: str) -> List[Dict[str, Any]]:
        import librosa
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
        duration = len(y) / sr
        num_speakers = 2
        segments = []
        segment_duration = duration / (num_speakers * 3)
        current_time = 0
        speaker_idx = 0
        while current_time < duration:
            end_time = min(current_time + segment_duration, duration)
            segments.append({
                'speaker': f'SPEAKER_{speaker_idx:02d}',
                'start_time': current_time,
                'end_time': end_time,
            })
            current_time = end_time
            speaker_idx = (speaker_idx + 1) % num_speakers
        logger.info(f"Mock diarization generated {len(segments)} segments")
        return segments

    def assign_speaker_roles(self, segments: List[Dict[str, Any]], transcripts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        speaker_texts: Dict[str, List[str]] = {}
        for seg in segments:
            speaker = seg['speaker']
            matched_text = self._match_transcript_to_segment(seg, transcripts)
            if matched_text:
                speaker_texts.setdefault(speaker, []).append(matched_text['text'])
        speaker_roles: Dict[str, str] = {}
        role_keywords = {
            'molecular_biologist': [
                '基因', '染色体', '测序', 'SNP', '突变', '表达', 'PCR', '分子',
                'DNA', 'RNA', '基因组', '基因型', '标记', 'QTL', '克隆'
            ],
            'horticulturist': [
                '表型', '性状', '田间', '育种', '产量', '品质', '栽培', '种植',
                '杂交', '选择', '筛选', '品系', '品种', '抗逆', '抗病', '农艺'
            ],
        }
        for speaker, texts in speaker_texts.items():
            combined_text = ' '.join(texts)
            scores = {}
            for role, keywords in role_keywords.items():
                scores[role] = sum(1 for kw in keywords if kw in combined_text)
            if scores['molecular_biologist'] > scores['horticulturist']:
                speaker_roles[speaker] = 'molecular_biologist'
            elif scores['horticulturist'] > scores['molecular_biologist']:
                speaker_roles[speaker] = 'horticulturist'
            else:
                speaker_roles[speaker] = 'molecular_biologist'
        if len(speaker_roles) == 2 and len(set(speaker_roles.values())) == 1:
            speakers = list(speaker_roles.keys())
            speaker_roles[speakers[1]] = 'horticulturist'
        for seg in segments:
            seg['speaker_role'] = speaker_roles.get(seg['speaker'], 'molecular_biologist')
        logger.info(f"Speaker roles assigned: {speaker_roles}")
        return segments

    def _match_transcript_to_segment(self, seg: Dict[str, Any], transcripts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        seg_mid = (seg['start_time'] + seg['end_time']) / 2
        best_match = None
        best_dist = float('inf')
        for trans in transcripts:
            trans_mid = (trans['start_time'] + trans['end_time']) / 2
            dist = abs(seg_mid - trans_mid)
            if dist < best_dist:
                best_dist = dist
                best_match = trans
        return best_match if best_dist < 10.0 else None
