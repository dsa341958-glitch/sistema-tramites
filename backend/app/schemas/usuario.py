from pydantic import BaseModel, EmailStr, Field

class RegistroIn(BaseModel):
    dni: str = Field(pattern=r"^\d{8}$")
    nombres: str = Field(min_length=3, max_length=120)
    email: EmailStr | None = None
    telefono: str = Field(pattern=r"^9\d{8}$")
    password: str = Field(min_length=8, max_length=72)
    consentimiento: bool

class UsuarioOut(BaseModel):
    id: int
    dni: str
    nombres: str
    rol: str
    model_config = {"from_attributes": True}

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut

class StaffIn(BaseModel):
    dni: str = Field(pattern=r"^\d{8}$")
    nombres: str = Field(min_length=3, max_length=120)
    email: EmailStr | None = None
    telefono: str = Field(pattern=r"^9\d{8}$")
    password: str = Field(min_length=8, max_length=72)
    area_id: int    