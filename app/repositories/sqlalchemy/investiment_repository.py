from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.investiment import Investiment
from app.repositories.protocols.i_investiment_repository import IInvestimentRepository
from app.schemas.investiment_schema import InvestimentIn, InvestimentOut


class InvestimentRepository(IInvestimentRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, investiment_data: InvestimentIn) -> InvestimentOut:
        investiment = Investiment(
            active_id=investiment_data.active_id,
            user_id=investiment_data.user_id,
            amount_invested=investiment_data.amount_invested,
            gain_target_percentain=investiment_data.gain_target_percentain,
            loss_limit_percent=investiment_data.type,
        )
        self.db.add(investiment)
        self.db.commit()

        return investiment

    def find_by_user(self, user_id: UUID) -> List[InvestimentOut]:
        return self.db.query(Investiment).filter(Investiment.user_id == user_id).all()

    def find_by_active(self) -> List[InvestimentOut]:
        return self.db.query(Investiment).all()
