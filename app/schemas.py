from sqlmodel import SQLModel


class ItemSchema(SQLModel):
    name: str
    description: str | None = None


class ItemUpdateSchema(SQLModel):
    name: str | None = None
    description: str | None = None
