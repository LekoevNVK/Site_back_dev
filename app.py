from methods import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response, status, Depends, Query, File, UploadFile
from typing import Optional, List
from model import OCR
from starlette.responses import FileResponse
import cv2
import os
import db_models
from db_connect import engine, SessionLocal
from sqlalchemy.orm import Session

# Database
db_models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# End of Database


app = FastAPI()

# "*" for any origins
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/get", tags=["Get files"], status_code=status.HTTP_200_OK)
async def root(
        response: Response,
        id: Optional[List[int]] = Query(None),
        name: Optional[List[str]] = Query(None),
        tag: Optional[List[str]] = Query(None),
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        db: Session = Depends(get_db)
):
    query = db.query(db_models.Image).all()
    files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    if id and not name and not tag:
        query = db.query(db_models.Image).filter(db_models.Image.file_id.in_(id)).all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and name and not tag:
        query = db.query(db_models.Image).filter(db_models.Image.file_id.in_(id)) \
            .filter(db_models.Image.name.in_(name)) \
            .all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and name and tag:
        query = db.query(db_models.Image).filter(db_models.Image.file_id.in_(id)) \
            .filter(db_models.Image.name.in_(name)) \
            .filter(db_models.Image.tag.in_(tag)) \
            .all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif id and not name and tag:
        query = db.query(db_models.Image).filter(db_models.Image.file_id.in_(id)) \
            .filter(db_models.Image.tag.in_(tag)) \
            .all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and name and tag:
        query = db.query(db_models.Image).filter(db_models.Image.name.in_(name)) \
            .filter(db_models.Image.tag.in_(tag)) \
            .all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and not name and tag:
        query = db.query(db_models.Image).filter(db_models.Image.tag.in_(tag)).all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    elif not id and name and not tag:
        query = db.query(db_models.Image).filter(db_models.Image.name.in_(name)).all()
        files_in_db = get_files_from_db_limit_offset(db, query, limit, offset)

    if len(files_in_db) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'message': 'No results :('}

    response.status_code = status.HTTP_200_OK
    return files_in_db


@app.post("/api/upload", tags=["Upload"], status_code=status.HTTP_200_OK)
async def upload_file(
        response: Response,
        file_id: int,
        name: Optional[str] = None,
        tag: Optional[str] = None,
        text: Optional[str] = None,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # Format new filename
    full_name = format_filename(file, file_id, name)

    # Save file
    await save_file_to_uploads(file, full_name)

    # Get file size
    file_size = get_file_size(full_name)

    # Get info from DB
    file_info_from_db = get_file_from_db(db, file_id)

    # Add to DB
    if not file_info_from_db:
        response.status_code = status.HTTP_201_CREATED
        return add_file_to_db(
            db,
            file_id=file_id,
            full_name=full_name,
            tag=tag,
            text=text,
            file_size=file_size,
            file=file
        )

    # Update in DB
    if file_info_from_db:
        response.status_code = status.HTTP_201_CREATED
        if file_info_from_db.name == full_name:
            return update_file_in_db(
                db,
                file_id=file_id,
                full_name=full_name,
                tag=tag,
                text=text,
                file_size=file_size,
                file=file
            )
        else:
            delete_file_from_uploads(file_info_from_db.name)
            return update_file_in_db(
                db,
                file_id=file_id,
                full_name=full_name,
                tag=tag,
                text=text,
                file_size=file_size,
                file=file
            )


@app.post('/api/predict', tags=["Make predict"])
async def make_predict(
        file_id,
        db: Session = Depends(get_db)
):
    file_info_from_db = get_file_from_db(db, file_id)
    return update_file_text_in_db(db,
                                  file_id=file_id,
                                  text=OCR.predict(f'/home/api_new/Site_back_dev/uploaded_files/{file_info_from_db.name}')
                                  )


@app.delete("/api/delete", tags=["Delete"])
async def delete_file(
        response: Response,
        file_id: int,
        db: Session = Depends(get_db)
):
    file_info_from_db = get_file_from_db(db, file_id)

    if file_info_from_db:
        # Delete file from DB
        delete_file_from_db(db, file_info_from_db)

        # Delete file from uploads
        delete_file_from_uploads(file_info_from_db.name)

        response.status_code = status.HTTP_200_OK
        return {'msg': f'File {file_info_from_db.name} deleted'}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'msg': f'File does not exist'}


@app.get('/api/photo', tags=['Get Photo'])
async def get_photo(
        response: Response,
        file_id: int,
        db: Session = Depends(get_db)
):
    file_info_from_db = get_file_from_db(db, file_id)

    if file_info_from_db:
        photo_from_db = FileResponse(f'/home/api_new/Site_back_dev/uploaded_files/{file_info_from_db.name}',
                                     media_type=file_info_from_db.mime_type,
                                     filename=file_info_from_db.name)
        response.status_code = status.HTTP_200_OK
        return photo_from_db
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'msg': 'File not found'}


@app.get('/api/photos', tags=['Get Photos'])
async def get_photo(
        response: Response,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        db: Session = Depends(get_db)
):
    photos = []
    for file_id in range(limit, offset + 1):
        file_info_from_db = get_file_from_db(db, file_id)

        if file_info_from_db:
            photo_from_db = FileResponse(f'/home/api_new/Site_back_dev/uploaded_files/{file_info_from_db.name}',
                                         media_type=file_info_from_db.mime_type,
                                         filename=file_info_from_db.name)
            response.status_code = status.HTTP_200_OK
            photos.append(photo_from_db)
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'msg': 'File not found'}
    return photos
