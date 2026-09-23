import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GermplasmSyncer:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        logger.info(f"Initializing GermplasmSyncer with API URL: {api_url}")

    def sync_report(
        self,
        meeting_id: str,
        report_data: Dict[str, Any],
        markdown_content: str,
    ) -> bool:
        if self.api_url == "https://api.germplasm.example.com/upload":
            logger.info("Mock sync to germplasm database (example config)")
            logger.info(f"Meeting ID: {meeting_id}")
            logger.info(f"Report data keys: {list(report_data.keys())}")
            return True

        payload = {
            "meeting_id": meeting_id,
            "report_id": report_data.get("id"),
            "title": report_data.get("title", ""),
            "date": report_data.get("date", ""),
            "participants": report_data.get("participants", []),
            "summary": report_data.get("summary", ""),
            "mutagenesis_analysis": report_data.get("mutagenesis_analysis", ""),
            "screening_strategy": report_data.get("screening_strategy", ""),
            "markdown_content": markdown_content,
            "synced_at": datetime.now().isoformat(),
            "source_system": "space_breeding_gene_trajectory_system",
            "version": "1.0",
        }

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Successfully synced report to germplasm database: {result}")
                return True
        except httpx.HTTPError as e:
            logger.error(f"HTTP error syncing to germplasm database: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error syncing to germplasm database: {e}", exc_info=True)
            return False

    def sync_phenotype_data(
        self,
        phenotype_records: list,
        meeting_id: Optional[str] = None,
    ) -> bool:
        if self.api_url == "https://api.germplasm.example.com/upload":
            logger.info(f"Mock syncing {len(phenotype_records)} phenotype records (example config)")
            return True

        try:
            payload = {
                "phenotype_data": [
                    {
                        "seed_id": record.seed_id,
                        "seed_name": record.seed_name,
                        "trait_name": record.trait_name,
                        "ground_control": record.ground_control,
                        "space_flight": record.space_flight,
                        "unit": record.unit,
                        "change_percentage": record.change_percentage,
                        "significant": record.significant,
                        "meeting_id": meeting_id,
                    }
                    for record in phenotype_records
                ],
                "synced_at": datetime.now().isoformat(),
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    self.api_url.replace("/upload", "/phenotype"),
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                logger.info(f"Successfully synced {len(phenotype_records)} phenotype records")
                return True
        except Exception as e:
            logger.error(f"Error syncing phenotype data: {e}", exc_info=True)
            return False
