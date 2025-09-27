from sqlmodel import Session, select
from models import Category, Video
from database import engine

async def get_categories():
    with Session(engine) as session:
        return session.exec(select(Category)).all()

async def is_category_exists(category_id: int):
    with Session(engine) as session:
        if session.get(Category, category_id):
            return True
    return False

async def is_category_name_exists(name: str):
    with Session(engine) as session:
        if session.exec(select(Category).where(Category.name == name)).one_or_none():
            return True
    return False

async def is_active_video(video_id: int):
    with Session(engine) as session:
        if session.exec(select(Video).where(Video.id == video_id, Video.is_active)).one_or_none():
            return True
    return False

async def count_videos(category_id: int):
    with Session(engine) as session:
        rows = session.exec(
            select(Video.category_id).where(Video.category_id == category_id, Video.is_active)
        ).all()
    return len(rows)
