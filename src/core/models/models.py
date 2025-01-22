from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy import JSON
from sqlmodel import Column, Field, Relationship, SQLModel, String


class Template(SQLModel, table=True):
    id: Optional[str] = Field(sa_column=Column(String(255), primary_key=True, nullable=False))
    base: str = Field(sa_column=Column("name", String(5000), index=True))
    description: str = Field(sa_column=Column("description", String(255), index=True))
    expected_result: str = Field(sa_column=Column("expected_result", String(255), index=True))
    placeholders: List["Placeholder"] = Relationship(back_populates="template")

    def __repr__(self):
        return f"Template(id={self.id}, name={self.base}, description={self.description})"


class Placeholder(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True, default=None)
    name: str = Field(sa_column=Column("name", String(500), index=True))
    description: str = Field(sa_column=Column("description", String(255), index=True))
    values: List[str] = Field(sa_column=Column("values", JSON))
    template_id: str = Field(sa_column=Column("template_id", sa.ForeignKey("template.id")))
    template: Template = Relationship(back_populates="placeholders")

    def __repr__(self):
        return (f"Placeholder(id={self.id}, name={self.name}, description={self.description}, "
                f"template_id={self.template_id})")

    class Config:
        arbitrary_types_allowed = True
