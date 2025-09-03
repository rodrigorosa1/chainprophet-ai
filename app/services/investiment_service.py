from typing import List
from app.repositories.protocols.i_investiment_repository import IInvestimentRepository
from app.schemas.investiment_schema import InvestimentIn, InvestimentOut


class InvestimentService:
    def __init__(self, investiment_repo: IInvestimentRepository):
        self.investiment_repo = investiment_repo

    def create(self, investiment_data: InvestimentIn) -> InvestimentOut:
        return self.investiment_repo.create(investiment_data)

    def find_by_active(self) -> List[InvestimentOut]:
        return self.investiment_repo.find_by_active()
