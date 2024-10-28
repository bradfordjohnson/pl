from sqlalchemy import Column, String, BigInteger, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pl.database import Base
import uuid

class MediaFileModel:
    __tablename__ = "media"
    
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    path = Column(Text, nullable=False)
    extension = Column(String(10), nullable=False)
    source_path = Column(Text, nullable=False)
    source_extension = Column(String(10), nullable=False)
    size = Column(BigInteger, nullable=False)
    sha256 = Column(Text)
    metadata = Column(JSONB, nullable=True)
    
class SidecarFileModel:
    __tablename__ = "metadata"
    
    # need to make an id
    name = Column(Text, nullable=False)
    source_path = Column(Text, nullable=False)
    source_extension = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)