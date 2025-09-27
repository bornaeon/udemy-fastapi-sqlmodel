from fastapi import APIRouter
from sqlmodel import Session, select
from models import Category, Video, CategorisedVideos
from database import engine

router = APIRouter()

@router.get('/categorised_videos', response_model=list[CategorisedVideos])
async def get_category_videos():
    with Session(engine) as session:
        return session.exec(
            select(
                Category.name.label('category_name'), 
                Video.title,
                Video.youtube_code
            )
            .join(Video)
            .where(Video.is_active)
            .order_by(Category.name, Video.title)
        ).all()
