import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from ..core.config import settings
from .audio_processor import AudioNoiseReducer
from .transcriber import WhisperTranscriber
from .speaker_diarization import SpeakerDiarizer
from .ai_analyzer import AIAnalyzer
from .email_sender import EmailSender
from .germplasm_syncer import GermplasmSyncer

logger = logging.getLogger(__name__)


class MeetingProcessor:
    def __init__(self):
        self.noise_reducer = AudioNoiseReducer()
        self.transcriber = WhisperTranscriber(model_name=settings.WHISPER_MODEL)
        self.diarizer = SpeakerDiarizer(auth_token=settings.PYANNOTE_AUTH_TOKEN)
        self.ai_analyzer = AIAnalyzer(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
        self.email_sender = EmailSender(
            smtp_host=settings.SMTP_HOST,
            smtp_port=settings.SMTP_PORT,
            smtp_user=settings.SMTP_USER,
            smtp_password=settings.SMTP_PASSWORD,
            smtp_from=settings.SMTP_FROM,
        )
        self.germplasm_syncer = GermplasmSyncer(
            api_url=settings.GERMPLASM_API_URL,
            api_key=settings.GERMPLASM_API_KEY,
        )
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.PROCESSED_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
        logger.info("MeetingProcessor initialized")

    def process_meeting_audio(
        self,
        meeting_id: str,
        audio_path: str,
        title: str = "",
    ) -> Dict[str, Any]:
        logger.info(f"Starting audio processing for meeting: {meeting_id}")
        try:
            processed_audio_path = str(
                Path(settings.PROCESSED_DIR) / f"{meeting_id}_cleaned.wav"
            )
            self.noise_reducer.process_audio(audio_path, processed_audio_path)
            logger.info("Step 1: Noise reduction completed")

            transcription_result = self.transcriber.transcribe(processed_audio_path)
            transcript_segments = self.transcriber.get_segments_with_terms(transcription_result)
            logger.info(f"Step 2: Transcription completed, {len(transcript_segments)} segments")

            diarization_segments = self.diarizer.diarize(processed_audio_path)
            logger.info(f"Step 3: Speaker diarization completed, {len(diarization_segments)} segments")

            diarization_segments = self.diarizer.assign_speaker_roles(
                diarization_segments, transcript_segments
            )
            logger.info("Step 4: Speaker roles assigned")

            merged_transcripts = self._merge_diarization_and_transcripts(
                diarization_segments, transcript_segments
            )
            logger.info(f"Step 5: Merged {len(merged_transcripts)} transcripts")

            result = {
                'meeting_id': meeting_id,
                'title': title,
                'processed_audio_path': processed_audio_path,
                'transcripts': merged_transcripts,
                'transcript_count': len(merged_transcripts),
            }
            logger.info("Audio processing pipeline completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error processing meeting audio: {str(e)}", exc_info=True)
            raise

    def _merge_diarization_and_transcripts(
        self,
        diarization_segments: List[Dict[str, Any]],
        transcript_segments: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        merged = []
        speaker_names = {}
        role_name_map = {
            'molecular_biologist': '张博士',
            'horticulturist': '王研究员',
        }
        for seg in diarization_segments:
            speaker = seg['speaker']
            if speaker not in speaker_names:
                role = seg.get('speaker_role', 'molecular_biologist')
                speaker_names[speaker] = role_name_map.get(role, f'未知人员{len(speaker_names)+1}')
        for t_seg in transcript_segments:
            t_mid = (t_seg['start_time'] + t_seg['end_time']) / 2
            best_d_seg = None
            best_dist = float('inf')
            for d_seg in diarization_segments:
                if d_seg['start_time'] <= t_mid <= d_seg['end_time']:
                    best_d_seg = d_seg
                    break
                d_mid = (d_seg['start_time'] + d_seg['end_time']) / 2
                dist = abs(t_mid - d_mid)
                if dist < best_dist:
                    best_dist = dist
                    best_d_seg = d_seg
            if best_d_seg:
                speaker = best_d_seg.get('speaker', 'Unknown')
                speaker_name = speaker_names.get(speaker, speaker)
                t_seg['speaker'] = speaker_name
                t_seg['speaker_role'] = best_d_seg.get('speaker_role', 'molecular_biologist')
            else:
                t_seg['speaker'] = '未知人员'
                t_seg['speaker_role'] = 'molecular_biologist'
            merged.append(t_seg)
        return merged

    def generate_analysis(self, transcripts: List[Dict[str, Any]]) -> Dict[str, str]:
        logger.info("Generating AI analysis")
        summary = self.ai_analyzer.generate_summary(transcripts)
        mutagenesis_analysis = self.ai_analyzer.generate_mutagenesis_analysis(transcripts)
        screening_strategy = self.ai_analyzer.generate_screening_strategy(transcripts)
        return {
            'summary': summary,
            'mutagenesis_analysis': mutagenesis_analysis,
            'screening_strategy': screening_strategy,
        }

    def generate_report(
        self,
        meeting_data: Dict[str, Any],
        analysis: Dict[str, str],
    ) -> str:
        logger.info("Generating markdown report")
        full_data = {
            **meeting_data,
            **analysis,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        markdown_content = self.ai_analyzer.generate_full_report(full_data)
        report_id = str(uuid.uuid4())
        report_path = Path(settings.REPORTS_DIR) / f"{report_id}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        logger.info(f"Report saved to: {report_path}")
        return markdown_content

    def send_report_email(
        self,
        markdown_content: str,
        meeting_title: str,
        to_emails: Optional[List[str]] = None,
    ) -> List[str]:
        if to_emails is None:
            to_emails = settings.project_email_list
        subject = f"【太空育种会议纪要】{meeting_title}"
        timestamp = datetime.now().strftime('%Y%m%d')
        attachment_filename = f"太空育种会议纪要_{timestamp}.md"
        success = self.email_sender.send_report(
            to_emails=to_emails,
            subject=subject,
            markdown_content=markdown_content,
            meeting_title=meeting_title,
            attachment_filename=attachment_filename,
        )
        if success:
            logger.info(f"Report email sent to {len(to_emails)} recipients")
            return to_emails
        logger.warning("Failed to send report email")
        return []

    def sync_to_germplasm(
        self,
        meeting_id: str,
        meeting_data: Dict[str, Any],
        markdown_content: str,
    ) -> bool:
        logger.info(f"Syncing meeting {meeting_id} to germplasm database")
        return self.germplasm_syncer.sync_report(
            meeting_id=meeting_id,
            report_data=meeting_data,
            markdown_content=markdown_content,
        )
