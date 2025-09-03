from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.constants.enums.type_active_enum import TypeActiveEnum
from app.models.active import Active
from app.repositories.protocols.iactive_repository import IActiveRepository
from app.schemas.active_schema import ActiveOut, ActiveIn


class ActiveRepository(IActiveRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, active_data: ActiveIn) -> ActiveOut:
        active = Active(
            ticker=active_data.ticker,
            name=active_data.name,
            type=active_data.type,
        )
        self.db.add(active)
        self.db.commit()

        return active

    def find_all(self) -> List[ActiveOut]:
        return self.db.query(Active).all()

    def find_by_id(self, id: UUID) -> ActiveOut:
        return self.db.query(Active).filter(Active.id == id).first()

    def find_by_ticker(self, ticker: str, type: TypeActiveEnum) -> ActiveOut:
        return (
            self.db.query(Active)
            .filter(Active.ticker == ticker, Active.type == type)
            .first()
        )
