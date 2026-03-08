from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.plan import Plan
from app.repositories.protocols.iplan_repository import IPlanRepository
from app.schemas.plan_schema import PlanIn, PlanOut


class PlanRepository(IPlanRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, plan_in: PlanIn) -> PlanOut:
        plan = Plan(
            name=plan_in.name,
            daily_amount=plan_in.daily_amount,
            no_limit=plan_in.no_limit,
            value=plan_in.value,
        )
        self.db.add(plan)
        self.db.commit()

        return plan

    def find_by_id(self, id: UUID) -> PlanOut:
        return self.db.query(Plan).filter(Plan.id == id).first()

    def find_all(self) -> List[PlanOut]:
        return self.db.query(Plan).all()

    def update(self, plan: Plan, plan_in: PlanIn) -> PlanOut:
        plan.name = plan_in.name
        plan.daily_amount = plan_in.daily_amount
        plan.no_limit = plan_in.no_limit
        plan.value = plan_in.value

        self.db.add(plan)
        self.db.commit()

        return plan

    def delete(self, plan: Plan) -> bool:
        self.db.delete(plan)
        self.db.commit()

        return True
