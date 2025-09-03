from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.repositories.protocols.iuser_repository import IUserRepository
from app.schemas.user_schema import UserIn, UserOut


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_data: UserIn) -> UserOut:
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hash_password(user_data.password),
            phone=user_data.phone,
            type_notification=user_data.type_notification,
        )
        self.db.add(user)
        self.db.commit()

        return user

    def find_by_id(self, id: UUID) -> UserOut:
        return self.db.query(User).filter(User.id == id).first()

    def register_password(self, user: User, password: str) -> UserOut:
        user.password = hash_password(password)

        self.db.add(user)
        self.db.commit()

        return user

    def find_by_email(self, email: str) -> UserOut:
        return self.db.query(User).filter(User.email == email).first()

    def find_all(self) -> List[UserOut]:
        return self.db.query(User).all()

    def update(self, user: User, user_data: UserIn) -> UserOut:
        user.name = user_data.name
        user.email = user_data.email
        user.phone = user_data.phone
        user.type_notification = user_data.type_notification
