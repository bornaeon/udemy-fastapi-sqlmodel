from fastapi import APIRouter, Request, responses
from sqlmodel import Session, select
from models import Category, Video, CategorisedVideos
from database import engine
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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

# Send an HTML of videos with click-to-edit form
@router.get('/list_video_form', response_class=responses.HTMLResponse)
async def get_list_video_form(request: Request):
    with Session(engine) as session:
        active_videos = session.exec(
            select(Video.id, Video.title, Video.youtube_code, Category.name.label('category_name'))
            .join(Category)
            .where(Video.is_active)
            .order_by(Video.title)
        ).all()
    return templates.TemplateResponse('form_list_video.html', {'request': request, 'videos': active_videos, 'page_title': 'List Videos'})
