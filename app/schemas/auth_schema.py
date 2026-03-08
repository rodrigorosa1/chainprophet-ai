from pydantic import BaseModel, ConfigDict


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

    model_config = ConfigDict(from_attributes=True)
