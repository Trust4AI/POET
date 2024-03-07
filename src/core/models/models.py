from typing import Dict, List, Optional

import sqlalchemy as sa
from sqlalchemy import JSON
from sqlmodel import Column, Field, Relationship, SQLModel, String


class Template(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True, default=None)
    base: str = Field(sa_column=Column("name", String(255), index=True))
    description: str = Field(sa_column=Column("description", String(255), index=True))
    base_markers: List["BaseMarker"] = Relationship(back_populates="template")
    # composite_markers: List["CompositeMarker"] = Relationship(back_populates="template")

    def __repr__(self):
        return f"Template(id={self.id}, name={self.base}, description={self.description})"


class BaseMarker(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True, default=None)
    name: str = Field(sa_column=Column("name", String(255), index=True))
    description: str = Field(sa_column=Column("description", String(255), index=True))
    options: List[str] = Field(sa_column=Column("options", JSON))
    template_id: int = Field(sa_column=Column("template_id", sa.ForeignKey("template.id")))
    template: Template = Relationship(back_populates="base_markers")

    def __repr__(self):
        return f"BaseMarker(id={self.id}, name={self.name}, description={self.description})"
    
    class Config:
        arbriary_types_allowed = True


# class CompositeMarker (SQLModel, table=True):
#     id: Optional[int] = Field(primary_key=True, index=True, default=None)
#     options: Dict[str, List[str]] = Field(sa_column=Column("composite_options", JSON))
#     template_id: int = Field(sa_column=Column("template_id", sa.ForeignKey("template.id")))
#     template: Template = Relationship(back_populates="composite_markers")

#     def replace(self, base: str) -> str:
#         pass

#     def __repr__(self):
#         return f"CompositeMaker(id={self.id}, options={self.options})"
    
#     class Config:
#         arbriary_types_allowed = True
