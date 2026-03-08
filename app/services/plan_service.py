from typing import List
from uuid import UUID
from app.constants.exceptions.messages import PlanNotFoundError
from app.repositories.protocols.iplan_repository import IPlanRepository
from app.schemas.plan_schema import PlanIn, PlanOut


class PlanService:
    def __init__(self, plan_repo: IPlanRepository):
        self.plan_repo = plan_repo

    def create(self, plan_in: PlanIn) -> PlanOut:
        return self.plan_repo.create(plan_in)

    def find_by_id(self, id: UUID) -> PlanOut:
        plan = self.plan_repo.find_by_id(id)
        if not plan:
            raise ValueError(PlanNotFoundError.MESSAGE)

        return plan

    def find_all(self) -> List[PlanOut]:
        return self.plan_repo.find_all()

    def update(self, id: UUID, plan_in: PlanIn) -> PlanOut:
        plan = self.plan_repo.find_by_id(id)
        if not plan:
            raise ValueError(PlanNotFoundError.MESSAGE)

        return self.plan_repo.update(plan, plan_in)

    def delete(self, id: UUID) -> bool:
        plan = self.plan_repo.find_by_id(id)
        if not plan:
            raise ValueError(PlanNotFoundError.MESSAGE)

        return self.plan_repo.delete(plan)
