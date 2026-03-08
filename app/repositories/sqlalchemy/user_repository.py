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

    def create(self, user_in: UserIn, key: str) -> UserOut:
        user = User(
            name=user_in.name,
            email=user_in.email,
            password=hash_password(user_in.password),
            phone=user_in.phone,
            api_key=key,
            active=True,
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

    def update(self, user: User, user_in: UserIn) -> UserOut:
        user.name = user_in.name
        user.email = user_in.email
        user.phone = user_in.phone
        user.active = user_in.active

        self.db.add(user)
        self.db.commit()

        return user

    def delete(self, user: User) -> bool:
        self.db.delete(user)
        self.db.commit()

        return True
