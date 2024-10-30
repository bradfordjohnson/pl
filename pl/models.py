from sqlalchemy import Column, String, BigInteger, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from pl.database import Base
from pydantic import BaseModel
import uuid


class MediaFileModel(Base):
    __tablename__ = "media"

    id = Column(Text, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    path = Column(Text, nullable=False)
    extension = Column(String(10), nullable=False)
    source_name = Column(Text, nullable=False)
    source_path = Column(Text, nullable=False)
    source_extension = Column(String(10), nullable=False)
    size = Column(BigInteger, nullable=False)
    sha256 = Column(Text, nullable=True)
    file_metadata = Column(JSON, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "extension": self.extension,
            "source_name": self.source_name,
            "source_path": self.source_path,
            "source_extension": self.source_extension,
            "size": self.size,
            "sha256": self.sha256,
            "file_metadata": self.file_metadata,
        }


class MediaFileCreate(BaseModel):
    id: str
    name: str
    path: str
    extension: str
    source_name: str
    source_path: str
    source_extension: str
    size: int
    sha256: str = None
    file_metadata: dict = None

    class Config:
        orm_mode = True


class SidecarFileModel(Base):
    __tablename__ = "sidecar"

    id = Column(Text, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    source_path = Column(Text, nullable=False)
    source_extension = Column(String(10), nullable=False)
    file_metadata = Column(JSON, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "source_path": self.source_path,
            "source_extension": self.source_extension,
            "file_metadata": self.file_metadata,
        }


class SidecarFileCreate(BaseModel):
    id: str
    name: str
    source_path: str
    source_extension: str
    file_metadata: dict = None

    class Config:
        orm_mode = True
