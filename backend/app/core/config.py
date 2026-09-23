from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    OPENAI_API_KEY: str = "sk-placeholder"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    WHISPER_MODEL: str = "large-v3"
    PYANNOTE_AUTH_TOKEN: str = "placeholder"

    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "noreply@example.com"
    SMTP_PASSWORD: str = "password"
    SMTP_FROM: str = "noreply@example.com"
    PROJECT_EMAILS: str = "scientist1@example.com,scientist2@example.com"

    GERMPLASM_API_URL: str = "https://api.germplasm.example.com/upload"
    GERMPLASM_API_KEY: str = "germplasm-key"

    DATABASE_URL: str = "sqlite:///./data/gene_trajectory.db"

    UPLOAD_DIR: str = "./data/uploads"
    PROCESSED_DIR: str = "./data/processed"
    REPORTS_DIR: str = "./data/reports"

    @property
    def project_email_list(self) -> List[str]:
        return [email.strip() for email in self.PROJECT_EMAILS.split(",") if email.strip()]


settings = Settings()
