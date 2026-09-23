from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from ..core.database import get_db
from ..models.db_models import DBPhenotypeData
from ..models.schemas import PhenotypeData, PhenotypeDataCreate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/phenotype", tags=["表型数据"])


@router.get("", response_model=List[PhenotypeData])
def get_phenotype_data(
    seed_id: str = None,
    seed_name: str = None,
    significant_only: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(DBPhenotypeData)
    if seed_id:
        query = query.filter(DBPhenotypeData.seed_id == seed_id)
    if seed_name:
        query = query.filter(DBPhenotypeData.seed_name.contains(seed_name))
    if significant_only:
        query = query.filter(DBPhenotypeData.significant == True)
    data = query.order_by(DBPhenotypeData.change_percentage.desc()).all()
    if not data:
        data = _get_mock_data(db)
    return data


@router.post("", response_model=PhenotypeData)
def create_phenotype_data(
    phenotype: PhenotypeDataCreate,
    db: Session = Depends(get_db),
):
    db_phenotype = DBPhenotypeData(**phenotype.model_dump())
    db.add(db_phenotype)
    db.commit()
    db.refresh(db_phenotype)
    logger.info(f"Created phenotype data: {db_phenotype.id}")
    return db_phenotype


@router.get("/{phenotype_id}", response_model=PhenotypeData)
def get_phenotype_by_id(phenotype_id: str, db: Session = Depends(get_db)):
    phenotype = db.query(DBPhenotypeData).filter(DBPhenotypeData.id == phenotype_id).first()
    if not phenotype:
        raise HTTPException(status_code=404, detail="Phenotype data not found")
    return phenotype


def _get_mock_data(db: Session) -> List[DBPhenotypeData]:
    mock_data = [
        DBPhenotypeData(seed_id="S001", seed_name="太空小麦-01", trait_name="株高", ground_control=75, space_flight=92, unit="cm", change_percentage=22.7, significant=True),
        DBPhenotypeData(seed_id="S001", seed_name="太空小麦-01", trait_name="穗长", ground_control=10, space_flight=13, unit="cm", change_percentage=30.0, significant=True),
        DBPhenotypeData(seed_id="S001", seed_name="太空小麦-01", trait_name="千粒重", ground_control=45, space_flight=52, unit="g", change_percentage=15.6, significant=True),
        DBPhenotypeData(seed_id="S002", seed_name="太空水稻-03", trait_name="株高", ground_control=95, space_flight=88, unit="cm", change_percentage=-7.4, significant=False),
        DBPhenotypeData(seed_id="S002", seed_name="太空水稻-03", trait_name="千粒重", ground_control=28, space_flight=35, unit="g", change_percentage=25.0, significant=True),
        DBPhenotypeData(seed_id="S002", seed_name="太空水稻-03", trait_name="结实率", ground_control=85, space_flight=91, unit="%", change_percentage=7.1, significant=True),
        DBPhenotypeData(seed_id="S003", seed_name="太空番茄-07", trait_name="单果重", ground_control=150, space_flight=210, unit="g", change_percentage=40.0, significant=True),
        DBPhenotypeData(seed_id="S003", seed_name="太空番茄-07", trait_name="维生素C含量", ground_control=15, space_flight=22, unit="mg/100g", change_percentage=46.7, significant=True),
        DBPhenotypeData(seed_id="S004", seed_name="太空辣椒-02", trait_name="单株结果数", ground_control=25, space_flight=32, unit="个", change_percentage=28.0, significant=True),
        DBPhenotypeData(seed_id="S004", seed_name="太空辣椒-02", trait_name="辣度", ground_control=3000, space_flight=4500, unit="SHU", change_percentage=50.0, significant=True),
    ]
    for item in mock_data:
        db.add(item)
    db.commit()
    return mock_data
