from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid
from pathlib import Path
from datetime import datetime

from ..core.database import get_db
from ..core.config import settings
from ..models.db_models import DBMeetingRecord, DBMeetingTranscript, DBReportData
from ..models.schemas import (
    MeetingRecord, MeetingRecordCreate, MeetingTranscript,
    ReportData, AudioUploadResponse, MeetingStatus
)
from ..services.meeting_processor import MeetingProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/meetings", tags=["会议管理"])

meeting_processor = MeetingProcessor()


@router.get("", response_model=List[MeetingRecord])
def get_meetings(
    limit: int = 20,
    offset: int = 0,
    status: Optional[MeetingStatus] = None,
    db: Session = Depends(get_db),
):
    query = db.query(DBMeetingRecord)
    if status:
        query = query.filter(DBMeetingRecord.status == status.value)
    meetings = query.order_by(DBMeetingRecord.created_at.desc()).offset(offset).limit(limit).all()
    return meetings


@router.post("", response_model=MeetingRecord)
def create_meeting(
    meeting: MeetingRecordCreate,
    db: Session = Depends(get_db),
):
    db_meeting = DBMeetingRecord(
        **meeting.model_dump(exclude={'audio_file_path'}),
        audio_file_path=meeting.audio_file_path,
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    logger.info(f"Created meeting: {db_meeting.id}")
    return db_meeting


@router.get("/{meeting_id}", response_model=MeetingRecord)
def get_meeting(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.query(DBMeetingRecord).filter(DBMeetingRecord.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.get("/{meeting_id}/transcripts", response_model=List[MeetingTranscript])
def get_meeting_transcripts(meeting_id: str, db: Session = Depends(get_db)):
    transcripts = db.query(DBMeetingTranscript).filter(
        DBMeetingTranscript.meeting_id == meeting_id
    ).order_by(DBMeetingTranscript.start_time).all()
    if not transcripts:
        transcripts = _get_mock_transcripts(meeting_id, db)
    return transcripts


@router.post("/upload/audio", response_model=AudioUploadResponse)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    db: Session = Depends(get_db),
):
    meeting_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix if file.filename else '.mp3'
    upload_path = Path(settings.UPLOAD_DIR) / f"{meeting_id}{file_ext}"
    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)
    logger.info(f"Audio file saved to: {upload_path}")

    db_meeting = DBMeetingRecord(
        id=meeting_id,
        title=title,
        date=datetime.now().strftime('%Y-%m-%d'),
        participants=[],
        audio_file_path=str(upload_path),
        status=MeetingStatus.PROCESSING.value,
    )
    db.add(db_meeting)
    db.commit()

    background_tasks.add_task(
        _process_meeting_background,
        meeting_id,
        str(upload_path),
        title,
    )

    return AudioUploadResponse(
        meeting_id=meeting_id,
        status="processing",
        message="文件已上传，正在后台处理，请稍后查看结果",
    )


@router.post("/{meeting_id}/generate-report", response_model=ReportData)
def generate_meeting_report(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.query(DBMeetingRecord).filter(DBMeetingRecord.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    transcripts = db.query(DBMeetingTranscript).filter(
        DBMeetingTranscript.meeting_id == meeting_id
    ).all()

    transcript_dicts = [
        {
            'speaker': t.speaker,
            'speaker_role': t.speaker_role,
            'start_time': t.start_time,
            'end_time': t.end_time,
            'text': t.text,
            'gene_terms': t.gene_terms,
            'trait_terms': t.trait_terms,
        }
        for t in transcripts
    ]

    analysis = meeting_processor.generate_analysis(transcript_dicts)

    meeting.summary = analysis['summary']
    meeting.mutagenesis_analysis = analysis['mutagenesis_analysis']
    meeting.screening_strategy = analysis['screening_strategy']
    meeting.status = MeetingStatus.COMPLETED.value

    meeting_data = {
        'title': meeting.title,
        'date': meeting.date,
        'participants': meeting.participants,
        'transcripts': transcript_dicts,
    }
    markdown_content = meeting_processor.generate_report(meeting_data, analysis)

    db_report = DBReportData(
        meeting_id=meeting_id,
        markdown_content=markdown_content,
        sent_emails=[],
        synced_to_germplasm=False,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    db.refresh(meeting)

    logger.info(f"Report generated for meeting {meeting_id}: {db_report.id}")
    return db_report


def _process_meeting_background(meeting_id: str, audio_path: str, title: str):
    from ..core.database import SessionLocal
    db = SessionLocal()
    try:
        logger.info(f"Starting background processing for meeting {meeting_id}")
        processing_result = meeting_processor.process_meeting_audio(
            meeting_id=meeting_id,
            audio_path=audio_path,
            title=title,
        )

        participants = list(set([t['speaker'] for t in processing_result['transcripts']]))

        for t in processing_result['transcripts']:
            db_transcript = DBMeetingTranscript(
                meeting_id=meeting_id,
                speaker=t['speaker'],
                speaker_role=t['speaker_role'],
                start_time=t['start_time'],
                end_time=t['end_time'],
                text=t['text'],
                gene_terms=t['gene_terms'],
                trait_terms=t['trait_terms'],
            )
            db.add(db_transcript)

        meeting = db.query(DBMeetingRecord).filter(DBMeetingRecord.id == meeting_id).first()
        if meeting:
            meeting.participants = participants
            meeting.transcript_count = processing_result['transcript_count']

        db.commit()
        logger.info(f"Background processing completed for meeting {meeting_id}")

    except Exception as e:
        logger.error(f"Background processing failed for meeting {meeting_id}: {str(e)}", exc_info=True)
        meeting = db.query(DBMeetingRecord).filter(DBMeetingRecord.id == meeting_id).first()
        if meeting:
            meeting.status = MeetingStatus.FAILED.value
            db.commit()
    finally:
        db.close()


def _get_mock_transcripts(meeting_id: str, db: Session) -> List[DBMeetingTranscript]:
    mock_data = [
        DBMeetingTranscript(
            meeting_id=meeting_id,
            speaker="张博士",
            speaker_role="molecular_biologist",
            start_time=0,
            end_time=45,
            text="今天我们重点分析太空小麦-01号的测序结果。我在5号染色体上发现了一个非常有意思的突变，位于TaGA20ox基因的启动子区域，这个基因是赤霉素合成途径中的关键酶。",
            gene_terms=["TaGA20ox", "Chr5:128456789"],
            trait_terms=["株高", "赤霉素合成"],
        ),
        DBMeetingTranscript(
            meeting_id=meeting_id,
            speaker="王研究员",
            speaker_role="horticulturist",
            start_time=46,
            end_time=95,
            text="这正好解释了我们田间观测到的表型！太空小麦-01的株高比对照增加了22.7%，而且穗长也有显著增加。从育种角度看，这个突变很有应用价值，但需要注意抗倒伏性的问题。",
            gene_terms=[],
            trait_terms=["株高", "穗长", "抗倒伏性"],
        ),
        DBMeetingTranscript(
            meeting_id=meeting_id,
            speaker="李教授",
            speaker_role="molecular_biologist",
            start_time=96,
            end_time=150,
            text="同意王研究员的观点。我们还需要验证这个突变的遗传稳定性。目前M2代的数据显示分离比符合3:1的孟德尔遗传规律，说明这是一个显性单基因突变。建议下一步构建近等基因系来精确评估该基因的效应。",
            gene_terms=["Chr5:128456789"],
            trait_terms=["遗传稳定性", "近等基因系"],
        ),
    ]
    for item in mock_data:
        db.add(item)
    db.commit()
    return mock_data
