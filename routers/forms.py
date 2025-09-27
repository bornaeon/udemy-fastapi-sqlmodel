from fastapi import APIRouter, Request, responses, HTTPException, status, Form
from sqlmodel import Session, select
from models import Video
from database import engine
from datetime import datetime
from fastapi.templating import Jinja2Templates
from services.validation import is_active_video, get_categories

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Send empty form to add a video
@router.get('/add_video_form', response_class=responses.HTMLResponse)
async def get_add_video_form(request: Request):
    return templates.TemplateResponse('form_add_video.html', {'request': request, 'categories': await get_categories()})

# Accept data from the form data and post it to the database
@router.post('/submit_video', response_class=responses.HTMLResponse)
async def post_add_video_form(request: Request, title: str = Form(), youtube_code: str = Form(), category_id: str = Form()):
    new_video = Video(title=title, youtube_code=youtube_code, category_id=int(category_id))
    with Session(engine) as session:
        session.add(new_video)
        session.commit()
        session.refresh(new_video)
    return templates.TemplateResponse('form_add_video.html', {'request': request, 'new_video': new_video, 'page_title': 'Add a Video'})

# Send for editing a video
@router.get('/edit_video_form/{video_id}', response_class=responses.HTMLResponse)
async def get_edit_video_form(request: Request, video_id: int):
    with Session(engine) as session:
        return templates.TemplateResponse(
            'form_edit_video.html', {
                'video': session.get(Video, video_id),
                'request': request,
                'categories': await get_categories(),
                'page_title': 'Edit a Video'
            })

# Save edited video
@router.post('/edit_video_form/{video_id}')
async def submit_edit_video_form(video_id: int, title: str = Form(), youtube_code: str = Form(), category_id: str = Form()):
    updated_video = Video(id=video_id, title=title, youtube_code=youtube_code, category_id=int(category_id))
    # Open a new database session using the engine
    with Session(engine) as session:
        # Retrieve the current video object from the database using the provided video_id
        current_video = session.get(Video, video_id)
        # Create a dictionary of the updated video fields, excluding any fields that were not set
        video_dict = updated_video.model_dump(exclude_unset=True)
        # Iterate over each key-value pair in the updated video dictionary
        for key, value in video_dict.items():
            # Set the corresponding attribute on the current video object to the new value
            setattr(current_video, key, value)
        # Update the last modified date of the video to the current datetime
        current_video.date_last_modified = datetime.now()
        # Commit the changes to the database
        session.commit()
        # Refresh the current_video object with the latest data from the database
        session.refresh(current_video)
    # return to video list page
    return responses.RedirectResponse(url="/list_video_form", status_code=status.HTTP_302_FOUND)

# Delete a video by setting is_active to False
@router.get('/delete_video_form/{video_id}')
async def delete_video_form(video_id: int):
    if not await is_active_video(video_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    with Session(engine) as session:
        current_video = session.get(Video, video_id)
        current_video.is_active = False
        current_video.date_last_modified = datetime.now()
        session.commit()
    return responses.RedirectResponse(url="/list_video_form", status_code=status.HTTP_302_FOUND)
