from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..core.database import get_db
from ..models.db_models import DBReportData, DBMeetingRecord
from ..models.schemas import ReportData
from ..services.meeting_processor import MeetingProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/reports", tags=["报告管理"])

meeting_processor = MeetingProcessor()


@router.get("", response_model=List[ReportData])
def get_reports(
    meeting_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(DBReportData)
    if meeting_id:
        query = query.filter(DBReportData.meeting_id == meeting_id)
    reports = query.order_by(DBReportData.created_at.desc()).offset(offset).limit(limit).all()
    return reports


@router.get("/{report_id}", response_model=ReportData)
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(DBReportData).filter(DBReportData.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/{report_id}/send-email", response_model=ReportData)
def send_report_email(
    report_id: str,
    db: Session = Depends(get_db),
):
    report = db.query(DBReportData).filter(DBReportData.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    meeting = db.query(DBMeetingRecord).filter(
        DBMeetingRecord.id == report.meeting_id
    ).first()
    meeting_title = meeting.title if meeting else "太空育种会议纪要"

    sent_emails = meeting_processor.send_report_email(
        markdown_content=report.markdown_content,
        meeting_title=meeting_title,
    )

    report.sent_emails = list(set(report.sent_emails + sent_emails))
    db.commit()
    db.refresh(report)

    logger.info(f"Report {report_id} sent to {len(sent_emails)} recipients")
    return report


@router.post("/{report_id}/sync-germplasm", response_model=ReportData)
def sync_report_to_germplasm(
    report_id: str,
    db: Session = Depends(get_db),
):
    report = db.query(DBReportData).filter(DBReportData.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    meeting = db.query(DBMeetingRecord).filter(
        DBMeetingRecord.id == report.meeting_id
    ).first()

    meeting_data = {
        'id': report.id,
        'title': meeting.title if meeting else '',
        'date': meeting.date if meeting else '',
        'participants': meeting.participants if meeting else [],
        'summary': meeting.summary if meeting else '',
        'mutagenesis_analysis': meeting.mutagenesis_analysis if meeting else '',
        'screening_strategy': meeting.screening_strategy if meeting else '',
    }

    success = meeting_processor.sync_to_germplasm(
        meeting_id=report.meeting_id,
        meeting_data=meeting_data,
        markdown_content=report.markdown_content,
    )

    if success:
        report.synced_to_germplasm = True
        db.commit()
        db.refresh(report)
        logger.info(f"Report {report_id} synced to germplasm database")
    else:
        raise HTTPException(status_code=500, detail="Failed to sync to germplasm database")

    return report
