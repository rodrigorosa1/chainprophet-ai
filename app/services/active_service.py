from uuid import UUID
from typing import List
from app.constants.exceptions.messages import ActiveAlreadyExistsError
from app.repositories.protocols.iactive_repository import IActiveRepository
from app.schemas.active_schema import ActiveIn, ActiveOut


class ActiveService:
    def __init__(self, active_repo: IActiveRepository):
        self.active_repo = active_repo

    def create(self, active_data: ActiveIn) -> ActiveOut:
        active = self.active_repo.find_by_ticker(
            active_data.ticker, active_data.type
        )
        if active:
            raise ValueError(ActiveAlreadyExistsError.MESSAGE)

        return self.active_repo.create(active_data)

    def find_all(self) -> List[ActiveOut]:
        return self.active_repo.find_all()
