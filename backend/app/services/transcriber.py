import whisper
import logging
from typing import List, Dict, Any, Tuple
import re

logger = logging.getLogger(__name__)

GENE_PATTERNS = [
    r'\b(?:chr|Chr|CHR)\s*\d+\s*[::]\s*\d+\b',
    r'\b[A-Za-z]{2,8}\d{1,4}[A-Za-z]?\b',
    r'\b(?:SNP|Indel|INDEL|snp|indel)\s*\w+\b',
    r'\b(?:Chr|chr)[0-9XY]{1,2}[:\s]\d+\b',
]

TRAIT_TERMS = [
    '株高', '穗长', '千粒重', '结实率', '单株产量', '生育期',
    '抗倒伏性', '抗病性', '抗旱性', '抗逆性', '品质', '蛋白质含量',
    '淀粉含量', '脂肪含量', '维生素', '含糖量', '酸度', '辣度',
    '果重', '单果重', '座果率', '开花期', '成熟期', '有效分蘖',
    '分子标记', 'QTL', '全基因组', '测序', '基因型', '表型',
    '近等基因系', '回交', '自交', '杂种优势', '配合力',
    '赤霉素', '生长素', '细胞分裂素', '脱落酸', '乙烯',
]


class WhisperTranscriber:
    def __init__(self, model_name: str = "large-v3"):
        self.model_name = model_name
        self._model = None
        logger.info(f"Initializing Whisper transcriber with model: {model_name}")

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self._model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        return self._model

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        logger.info(f"Transcribing audio: {audio_path}")
        result = self.model.transcribe(
            audio_path,
            language="zh",
            task="transcribe",
            verbose=True,
            initial_prompt="这是一场关于太空育种、基因诱变、作物育种的科学讨论会。讨论内容涉及分子生物学、遗传学、园艺学等领域。",
        )
        logger.info(f"Transcription completed, {len(result['segments'])} segments")
        return result

    def extract_gene_terms(self, text: str) -> List[str]:
        terms = set()
        for pattern in GENE_PATTERNS:
            matches = re.findall(pattern, text)
            terms.update(matches)
        return sorted(list(terms))

    def extract_trait_terms(self, text: str) -> List[str]:
        terms = []
        for trait in TRAIT_TERMS:
            if trait in text:
                terms.append(trait)
        return terms

    def get_segments_with_terms(self, transcription_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        segments = []
        for seg in transcription_result['segments']:
            gene_terms = self.extract_gene_terms(seg['text'])
            trait_terms = self.extract_trait_terms(seg['text'])
            segments.append({
                'start_time': seg['start'],
                'end_time': seg['end'],
                'text': seg['text'].strip(),
                'gene_terms': gene_terms,
                'trait_terms': trait_terms,
            })
        return segments
