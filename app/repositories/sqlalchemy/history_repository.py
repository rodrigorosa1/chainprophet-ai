from datetime import date, datetime
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.history import History
from app.repositories.protocols.ihistory_repository import IHistoryRepository
from app.schemas.history_schema import HistoryOut


class HistoryRepository(IHistoryRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: UUID) -> HistoryOut:
        history = History(
            user_id=user_id,
        )
        self.db.add(history)
        self.db.commit()

        return history

    def find_by_user(self, user_id: UUID) -> List[HistoryOut]:
        return self.db.query(History).filter(History.user_id == user_id).all()

    def today_count(self, user_id: UUID) -> int:
        return (
            self.db.query(History)
            .filter(History.user_id == user_id, History.created_at == date.today())
            .count()
        )
