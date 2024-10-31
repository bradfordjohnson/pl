from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from sqlalchemy import Column, String, BigInteger, Text, JSON
from pydantic import BaseModel

app = FastAPI()


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session


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


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/media", response_model=MediaFileCreate, status_code=201)
async def create_media_file(
    media_file: MediaFileCreate, db: AsyncSession = Depends(get_db)
):
    db_media_file = MediaFileModel(
        id=media_file.id,
        name=media_file.name,
        path=media_file.path,
        extension=media_file.extension,
        source_name=media_file.source_name,
        source_path=media_file.source_path,
        source_extension=media_file.source_extension,
        size=media_file.size,
        sha256=media_file.sha256,
        file_metadata=media_file.file_metadata,
    )

    db.add(db_media_file)
    await db.commit()
    await db.refresh(db_media_file)

    return JSONResponse(content=db_media_file.to_dict(), status_code=201)


@app.post("/sidecar", response_model=SidecarFileCreate, status_code=201)
async def create_sidecar_file(
    sidecar_file: SidecarFileCreate, db: AsyncSession = Depends(get_db)
):
    db_sidecar_file = SidecarFileModel(
        id=sidecar_file.id,
        name=sidecar_file.name,
        source_path=sidecar_file.source_path,
        source_extension=sidecar_file.source_extension,
        file_metadata=sidecar_file.file_metadata,
    )

    db.add(db_sidecar_file)
    await db.commit()
    await db.refresh(db_sidecar_file)

    return JSONResponse(content=db_sidecar_file.to_dict(), status_code=201)


# uvicorn pl.main:app --reload --env-file .env.prod

# uvicorn pl.main:app --reload --env-file .env.dev
