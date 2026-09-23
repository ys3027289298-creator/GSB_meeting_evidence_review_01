from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class SpeakerRole(str, Enum):
    MOLECULAR_BIOLOGIST = "molecular_biologist"
    HORTICULTURIST = "horticulturist"


class MeetingStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PhenotypeDataBase(BaseModel):
    seed_id: str
    seed_name: str
    trait_name: str
    ground_control: float
    space_flight: float
    unit: str
    change_percentage: float
    significant: bool


class PhenotypeDataCreate(PhenotypeDataBase):
    pass


class PhenotypeData(PhenotypeDataBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingTranscriptBase(BaseModel):
    meeting_id: str
    speaker: str
    speaker_role: SpeakerRole
    start_time: float
    end_time: float
    text: str
    gene_terms: List[str] = Field(default_factory=list)
    trait_terms: List[str] = Field(default_factory=list)


class MeetingTranscriptCreate(MeetingTranscriptBase):
    pass


class MeetingTranscript(MeetingTranscriptBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingRecordBase(BaseModel):
    title: str
    date: str
    participants: List[str] = Field(default_factory=list)


class MeetingRecordCreate(MeetingRecordBase):
    audio_file_path: Optional[str] = None


class MeetingRecord(MeetingRecordBase):
    id: str
    transcript_count: int = 0
    status: MeetingStatus = MeetingStatus.PROCESSING
    summary: Optional[str] = None
    mutagenesis_analysis: Optional[str] = None
    screening_strategy: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReportDataBase(BaseModel):
    meeting_id: str
    markdown_content: str


class ReportDataCreate(ReportDataBase):
    pass


class ReportData(ReportDataBase):
    id: str
    sent_emails: List[str] = Field(default_factory=list)
    synced_to_germplasm: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class AudioUploadResponse(BaseModel):
    meeting_id: str
    status: str
    message: str


class GeneLocus(BaseModel):
    id: str
    name: str
    chromosome: str
    position: int
    mutation_type: str
    associated_trait: str
    effect: str
