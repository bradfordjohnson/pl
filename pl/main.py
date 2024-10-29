from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from pl.database import get_db, engine, Base
from pl.models import MediaFileModel, MediaFileCreate
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


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
