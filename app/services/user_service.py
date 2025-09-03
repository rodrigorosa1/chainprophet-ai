from typing import List
from uuid import UUID
from app.constants.exceptions.messages import (
    UserEmailDocumentAlreadyExistsError,
    UserNotFoundError,
)
from app.repositories.protocols.iuser_repository import IUserRepository
from app.schemas.user_schema import UserIn, UserOut


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def create(self, user_data: UserIn) -> UserOut:
        email = self.user_repo.find_by_email(user_data.email)
        if email:
            raise ValueError(UserEmailDocumentAlreadyExistsError.MESSAGE)

        return self.user_repo.create(user_data)

    def find_by_id(self, id: UUID) -> UserOut:
        user = self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(UserNotFoundError.MESSAGE)

        return user

    def find_all(self) -> List[UserOut]:
        return self.user_repo.find_all()

    def register_password(self, id: UUID, password: str) -> UserOut:
        user = self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(UserNotFoundError.MESSAGE)

        return self.user_repo.register_password(user, password)

    def update(self, id: UUID, user_data: UserIn) -> UserOut:
        user = self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(UserNotFoundError.MESSAGE)

        return self.user_repo.update(user, user_data)
