from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database.db import get_db
from src.database.models import Image, Tag
from src.schemas import ImageResponse

router = APIRouter(prefix="/search_filtering", tags=["search_filtering"])


@router.get("/", response_model=List[ImageResponse])
# @has_role(allowed_get_comments)
async def search_images_by_tags(tags: List[str] = Query(...), db: Session = Depends(get_db)):
    try:
        images = db.query(Image).join(Image.tags).filter(Tag.name.in_(tags)).all()

        filtered_images = [image for image in images if set(tags).issubset({tag.name for tag in image.tags})]

        image_responses = []
        for image in filtered_images:
            image_responses.append(ImageResponse(
                id=image.id,
                image=image.image,
                description=image.description,
                tags=[tag.name for tag in image.tags],
            ))

        return image_responses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/by_description", response_model=List[ImageResponse])
async def search_images_by_description(description: str = Query(...), db: Session = Depends(get_db)):
    try:
        images = db.query(Image).filter(Image.description.ilike(f"%{description}%")).all()

        image_responses = []
        for image in images:
            image_responses.append(ImageResponse(
                id=image.id,
                image=image.image,
                description=image.description,
                tags=[tag.name for tag in image.tags],
            ))

        return image_responses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ___________________________________________________________

@router.post("/sorted-by-rating", response_model=List[ImageResponse])
def get_images_sorted_by_rating(
        images: List[ImageResponse],
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
):
    sorted_images = sorted(
        images,
        key=lambda img: img.rating if img.rating is not None else float('-inf'),
        reverse=True
    )
    return sorted_images[skip: skip + limit]


@router.post("/sorted-by-date", response_model=List[ImageResponse])
def get_images_sorted_by_date(
        images: List[ImageResponse],
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
):
    sorted_images = sorted(images, key=lambda img: img.created_at, reverse=True)
    return sorted_images[skip: skip + limit]
