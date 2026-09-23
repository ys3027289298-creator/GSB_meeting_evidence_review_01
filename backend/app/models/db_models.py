from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
import uuid

from ..core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class DBPhenotypeData(Base):
    __tablename__ = "phenotype_data"

    id = Column(String, primary_key=True, default=generate_uuid)
    seed_id = Column(String, index=True)
    seed_name = Column(String, index=True)
    trait_name = Column(String)
    ground_control = Column(Float)
    space_flight = Column(Float)
    unit = Column(String)
    change_percentage = Column(Float)
    significant = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DBMeetingRecord(Base):
    __tablename__ = "meeting_records"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String)
    date = Column(String)
    participants = Column(JSON)
    transcript_count = Column(Integer, default=0)
    status = Column(String, default="processing")
    summary = Column(Text, nullable=True)
    mutagenesis_analysis = Column(Text, nullable=True)
    screening_strategy = Column(Text, nullable=True)
    audio_file_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DBMeetingTranscript(Base):
    __tablename__ = "meeting_transcripts"

    id = Column(String, primary_key=True, default=generate_uuid)
    meeting_id = Column(String, index=True)
    speaker = Column(String)
    speaker_role = Column(String)
    start_time = Column(Float)
    end_time = Column(Float)
    text = Column(Text)
    gene_terms = Column(JSON, default=list)
    trait_terms = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DBReportData(Base):
    __tablename__ = "report_data"

    id = Column(String, primary_key=True, default=generate_uuid)
    meeting_id = Column(String, index=True)
    markdown_content = Column(Text)
    sent_emails = Column(JSON, default=list)
    synced_to_germplasm = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
