from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, Session, SQLModel

from core.settings import settings

SQLALCHEMY_DATABASE_URL = f"mariadb+aiomysql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine_async = create_async_engine(SQLALCHEMY_DATABASE_URL)
