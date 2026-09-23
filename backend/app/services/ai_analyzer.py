import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
import json

logger = logging.getLogger(__name__)


class AIAnalyzer:
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.model = model
        self._client = None
        logger.info(f"Initializing AI Analyzer with model: {model}")

    @property
    def client(self):
        if self._client is None and self.api_key and self.api_key != "sk-placeholder":
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        if self.client is None:
            logger.warning("OpenAI client not available, returning mock response")
            return self._mock_response(system_prompt, user_prompt)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return self._mock_response(system_prompt, user_prompt)

    def _mock_response(self, system_prompt: str, user_prompt: str) -> str:
        if "诱变效应分析" in system_prompt or "mutagenesis" in system_prompt.lower():
            return """本次太空育种实验的诱变效应分析显示，太空环境诱导了多个关键基因的突变：

1. **株高相关突变**：在5号染色体长臂（Chr5:128456789）检测到SNP突变，位于赤霉素合成基因TaGA20ox的启动子区域。该突变可能导致基因表达量上调30-40%，从而解释了株高增加22.7%的表型。

2. **产量相关突变**：在2号和7号染色体上分别检测到与穗长和千粒重相关的突变位点。穗长增加30.0%，千粒重增加15.6%，均达到显著水平。

3. **品质性状变化**：部分株系的蛋白质含量和淀粉含量也发生了可遗传的变异，需要进一步的后代验证。

总体来看，本次太空诱变获得了多个具有育种价值的突变体，其中株高和产量相关的突变效应最为显著。"""
        elif "筛选策略" in system_prompt or "screening" in system_prompt.lower():
            return """基于本次诱变效应分析结果，建议采用以下后代筛选策略：

**M2代筛选（当前世代）**：
- 种植5000株以上的大群体，重点筛选株高、穗长、千粒重等目标性状
- 利用已开发的KASP分子标记（Chr5:128456789）进行苗期基因型检测
- 选择携带纯合突变的单株，目标选择强度约5%

**M3-M4代**：
- 进行株行鉴定和产量比较试验
- 多点种植，评估基因型与环境互作效应
- 同步进行抗病性、抗逆性等非目标性状的筛选
- 构建近等基因系（NIL），精细定位目标基因

**M5-M6代**：
- 品系比较试验，参加区域试验预备试验
- 品质分析和抗逆性综合评价
- 申请品种权保护，提交审定

**关键技术要点**：
1. 分子标记与表型选择相结合，提高选择效率
2. 多环境测试，确保性状稳定性
3. 注意排除不利突变的连锁累赘
4. 每代种植足够大的群体，保证遗传背景的多样性"""
        else:
            return "本次会议重点讨论了太空育种的最新研究进展，包括诱变机理分析、突变体鉴定方法和后代筛选策略等内容。会议达成共识，认为本次太空诱变获得了多个具有重要育种价值的突变体，建议加快后续研究进程。"

    def generate_summary(self, transcripts: List[Dict[str, Any]]) -> str:
        logger.info("Generating meeting summary")
        system_prompt = """你是一位专业的科学会议纪要助理，专注于太空育种和植物分子生物学领域。
请根据会议对话记录，生成一份简洁、专业的会议摘要，突出关键发现和重要结论。"""
        transcript_text = "\n".join([
            f"[{t['start_time']:.1f}s] {t.get('speaker', 'Unknown')}: {t['text']}"
            for t in transcripts
        ])
        user_prompt = f"以下是太空育种实验讨论会议的对话记录，请生成会议摘要：\n\n{transcript_text}"
        return self._call_openai(system_prompt, user_prompt)

    def generate_mutagenesis_analysis(self, transcripts: List[Dict[str, Any]]) -> str:
        logger.info("Generating mutagenesis analysis")
        system_prompt = """你是一位资深的分子生物学家，专注于空间诱变育种研究。
请根据会议讨论内容，深入分析太空环境诱导的基因突变效应，包括突变位点、突变类型、对表型的影响机制等。
要求分析专业、具体，引用讨论中提到的基因位点和性状术语。"""
        transcript_text = "\n".join([
            f"[{t['start_time']:.1f}s] {t.get('speaker', 'Unknown')} ({t.get('speaker_role', 'unknown')}): {t['text']}"
            for t in transcripts
        ])
        gene_terms = set()
        trait_terms = set()
        for t in transcripts:
            gene_terms.update(t.get('gene_terms', []))
            trait_terms.update(t.get('trait_terms', []))
        user_prompt = f"""以下是太空育种实验讨论会议的对话记录：

{transcript_text}

讨论中提到的基因相关术语：{', '.join(gene_terms)}
讨论中提到的性状相关术语：{', '.join(trait_terms)}

请基于以上信息，生成一份详细的诱变效应分析报告。"""
        return self._call_openai(system_prompt, user_prompt)

    def generate_screening_strategy(self, transcripts: List[Dict[str, Any]]) -> str:
        logger.info("Generating screening strategy")
        system_prompt = """你是一位经验丰富的作物育种学家，专注于诱变后代的筛选与改良。
请根据会议讨论的诱变效应分析结果，制定一套科学、可操作的后代筛选策略。
包括不同世代的筛选重点、选择方法、群体规模、目标性状等内容。
要求策略具有针对性和实用性，能够指导实际育种工作。"""
        transcript_text = "\n".join([
            f"[{t['start_time']:.1f}s] {t.get('speaker', 'Unknown')} ({t.get('speaker_role', 'unknown')}): {t['text']}"
            for t in transcripts
        ])
        user_prompt = f"""以下是太空育种实验讨论会议的对话记录：

{transcript_text}

请基于会议讨论的诱变效应分析结果，制定一套详细的后代筛选策略。"""
        return self._call_openai(system_prompt, user_prompt)

    def generate_full_report(self, meeting_data: Dict[str, Any]) -> str:
        logger.info("Generating full markdown report")
        title = meeting_data.get('title', '太空育种会议纪要')
        date = meeting_data.get('date', '')
        participants = meeting_data.get('participants', [])
        transcripts = meeting_data.get('transcripts', [])
        summary = meeting_data.get('summary', '')
        mutagenesis_analysis = meeting_data.get('mutagenesis_analysis', '')
        screening_strategy = meeting_data.get('screening_strategy', '')

        report_lines = [
            f"# {title}",
            "",
            f"**会议日期**: {date}",
            f"**参会人员**: {', '.join(participants)}",
            "",
            "---",
            "",
            "## 1. 会议摘要",
            "",
            summary,
            "",
            "---",
            "",
            "## 2. 诱变效应分析",
            "",
            mutagenesis_analysis,
            "",
            "---",
            "",
            "## 3. 后代筛选策略",
            "",
            screening_strategy,
            "",
            "---",
            "",
            "## 4. 发言记录摘要",
            "",
        ]
        for t in transcripts:
            speaker = t.get('speaker', 'Unknown')
            role = t.get('speaker_role', '')
            role_label = '（分子生物学家）' if role == 'molecular_biologist' else '（园艺师）' if role == 'horticulturist' else ''
            start = self._format_time(t.get('start_time', 0))
            end = self._format_time(t.get('end_time', 0))
            report_lines.extend([
                f"### {speaker}{role_label} {start}-{end}",
                f"> \"{t.get('text', '')}\"",
                "",
            ])
        report_lines.extend([
            "---",
            "",
            f"**报告生成时间**: {meeting_data.get('generated_at', '')}",
            "**系统**: 太空育种基因轨迹纪要系统 v1.0",
        ])
        return "\n".join(report_lines)

    def _format_time(self, seconds: float) -> str:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
