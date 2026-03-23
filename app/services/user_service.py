from typing import List
from uuid import UUID
from app.constants.exceptions.messages import (
    UserEmailDocumentAlreadyExistsError,
    UserNotFoundError,
)
from app.repositories.protocols.iuser_asset_repository import IUserAssetRepository
from app.repositories.protocols.iuser_repository import IUserRepository
from app.schemas.user_asset_schema import UserAssetOut
from app.schemas.user_schema import UserIn, UserOut
import secrets
import string


class UserService:
    def __init__(
        self, user_repo: IUserRepository, user_asset_repo: IUserAssetRepository
    ):
        self.user_repo = user_repo
        self.user_asset_repo = user_asset_repo

    def create(self, user_in: UserIn) -> UserOut:
        email = self.user_repo.find_by_email(user_in.email)
        if email:
            raise ValueError(UserEmailDocumentAlreadyExistsError.MESSAGE)

        return self.user_repo.create(user_in, self.generate_api_key())

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

    def update(self, id: UUID, user_in: UserIn) -> UserOut:
        user = self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(UserNotFoundError.MESSAGE)

        return self.user_repo.update(user, user_in)

    def delete(self, id: UUID) -> bool:
        user = self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(UserNotFoundError.MESSAGE)

        return self.user_repo.delete(user)

    def generate_api_key(self, length: int = 32) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def associate_assets(self, user_id: UUID, asset_ids: List[UUID]) -> bool:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(UserNotFoundError.MESSAGE)

        self.user_asset_repo.delete_user_assets(user_id)

        return self.user_asset_repo.associate_assets(user_id, asset_ids)

    def delete_user_assets(self, user_id: UUID) -> bool:
        return self.user_asset_repo.delete_user_assets(user_id)

    def find_assets_by_user_id(self, user_id: UUID) -> List[UserAssetOut]:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(UserNotFoundError.MESSAGE)

        return self.user_asset_repo.find_assets_by_user_id(user_id)
