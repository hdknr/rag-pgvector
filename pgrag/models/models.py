from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy import String, JSON, Text
from sqlalchemy.sql.schema import Column


class Base(DeclarativeBase):
    pass


class BaseDocument(Base):

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        UUID, primary_key=True, comment="primary_key_field"
    )
    embedding: Mapped[Vector] = mapped_column(Vector(1536), comment="vector_field")
    meta_data: Mapped[JSON] = mapped_column(JSON, comment="metadata_field")
    text: Mapped[str] = mapped_column(Text, comment="text_field")

    @classmethod
    def get_vector_field(cls) -> Column:
        return next(
            filter(lambda i: i.comment == "vector_field", cls.__table__.columns)
        )

    @classmethod
    def get_field_mapping(cls) -> Column:
        return dict((i.comment, i.name) for i in cls.__table__.columns if i.comment)


class Document(BaseDocument):
    __tablename__ = "document"
    __table_args__ = {"schema": "rag"}

    categories: Mapped[str] = mapped_column(String(256), nullable=True)
