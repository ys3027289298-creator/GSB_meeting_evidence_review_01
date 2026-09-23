export interface PhenotypeData {
  id: string;
  seedId: string;
  seedName: string;
  traitName: string;
  groundControl: number;
  spaceFlight: number;
  unit: string;
  changePercentage: number;
  significant: boolean;
}

export interface GeneLocus {
  id: string;
  name: string;
  chromosome: string;
  position: number;
  mutationType: string;
  associatedTrait: string;
  effect: string;
}

export interface MeetingTranscript {
  id: string;
  meetingId: string;
  speaker: string;
  speakerRole: 'molecular_biologist' | 'horticulturist';
  startTime: number;
  endTime: number;
  text: string;
  geneTerms: string[];
  traitTerms: string[];
}

export interface MeetingRecord {
  id: string;
  title: string;
  date: string;
  participants: string[];
  transcriptCount: number;
  status: 'processing' | 'completed' | 'failed';
  summary?: string;
  mutagenesisAnalysis?: string;
  screeningStrategy?: string;
  createdAt: string;
}

export interface AudioUploadResponse {
  meetingId: string;
  status: string;
  message: string;
}

export interface ReportData {
  id: string;
  meetingId: string;
  markdownContent: string;
  sentEmails: string[];
  syncedToGermplasm: boolean;
  createdAt: string;
}
