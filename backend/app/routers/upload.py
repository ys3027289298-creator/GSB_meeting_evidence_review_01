from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
import logging
import uuid
from pathlib import Path
from datetime import datetime

from ..core.database import get_db
from ..core.config import settings
from ..models.db_models import DBMeetingRecord
from ..models.schemas import AudioUploadResponse, MeetingStatus
from ..services.meeting_processor import MeetingProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upload", tags=["文件上传"])

meeting_processor = MeetingProcessor()


@router.post("/audio", response_model=AudioUploadResponse)
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

        from ..models.db_models import DBMeetingTranscript
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
