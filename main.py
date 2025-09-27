from fastapi import FastAPI, Request, responses, HTTPException, status, Form
from sqlmodel import Session, select
from models import Category, CategoryBase, Video, VideoBase, CategorisedVideos
from database import engine
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# App
api = FastAPI()
session = Session(bind = engine) # binds to our DB engine

# Static files
api.mount("/static", StaticFiles(directory = "static"), name = "static")
# Templates
templates = Jinja2Templates(directory = "templates")

# Routes
# Home page
@api.get('/', response_class = responses.HTMLResponse)
async def home():
    return '''
        <h1>Hello Wold! From an HTML respons</h1>
        <p>Here is the <a href="/docs">docs</a>
        <p>Here is the <a href="/add_video_form">form_add_video</a>
        <p>Here is the <a href="/edit_video_form">form_edit_video</a>
        <p>Here is the <a href="/list_video_form">form_list_video</a>
    '''

# region Categories
# Get all categories
@api.get('/category', response_model = list[Category])
async def get_categories():
    with Session(engine) as session:
        return session.exec(select(Category)).all()

# Get all categories in order by name
# @api.get('/category', response_model = list[Category])
# async def get_categories():
#    with Session(engine) as session:
#        return session.exec(select(Category).order_by(Category.name.desc())).all()

# Get a category
@api.get('/category/{category_id}', response_model = Category)
async def find_category(category_id: int):
    with Session(engine) as session:
        category = session.get(Category, category_id)
        if not await is_category_exists(category_id):
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Category not found")
        return category

# Post a new categoy
@api.post('/category')
async def create_category(category: CategoryBase):
    # Check if the category already exists and reject it
    if await is_category_name_exists(category.name):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Category already exists")

    new_category = Category(name=category.name)
    
    # Using a width block ensures that the session closes when the transaction is done, 
    # or it'll even close the session if the transaction fails.
    with Session(engine) as session:
        # setting up new category object
        session.add(new_category)
        # adding it to the database
        session.commit()
        # Now the category has an ID in database, but our local copy of the object doesn't know it yet.
        # session refresh updates the new_category object here so it contains the correct ID from the table
        session.refresh(new_category)
        
        return new_category

# Update a category
@api.put('/category/{category_id}', response_model = Category)
async def update_category(category_id: int, category: CategoryBase):
    if not await is_category_exists(category_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Category not found")
    with Session(engine) as session:
        # Get the existing category from database
        current_category = session.get(Category, category_id)
        # Update the category name with new value
        current_category.name = category.name
        # Stage the modified object for database update
        session.add(current_category)
        # Execute the UPDATE and save changes to database
        session.commit()
        # Reload object with latest database data
        session.refresh(current_category)
        return current_category

# Delete a category
@api.delete('/category/{category_id}', response_model = Category)
async def delete_category(category_id: int):
    if not await is_category_exists(category_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Category not found")
    # Check if the category has videos, then don't delete it
    if await count_videos(category_id) > 0:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Category has videos")
    with Session(engine) as session:
        # Get the existing category from database
        current_category = session.get(Category, category_id)
        # Delete the category from database
        session.delete(current_category)
        # Execute the DELETE and save changes to database
        session.commit()
        return { 'Deleted' : category_id }
# endregion Categories

# region Videos
# Get all active videos
@api.get('/video', response_model = list[Video])
async def get_videos():
    with Session(engine) as session:
        return session.exec(select(Video).where(Video.is_active).order_by(Video.date_created)).all()

# Get a video
@api.get('/video/{video_id}', response_model = Video)
async def find_video(video_id: int):
    if not await is_active_video(video_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "video not found")
    with Session(engine) as session:
        video = session.get(Video, video_id)
        return video

# Post a new video
@api.post('/video', status_code = status.HTTP_201_CREATED)
async def post_video(video: VideoBase):
    # create a new video object from the data passed in
    new_video = Video.model_validate(video)
    # check if the video has a valid category id
    if not await is_category_exists(new_video.category_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Category not found")
    # post the video
    with Session(engine) as session:
        session.add(new_video)
        session.commit()
        session.refresh(new_video)
    return responses.RedirectResponse(url = "/list_video_form", status_code = status.HTTP_302_FOUND)

# Update a video
@api.put('/video/{video_id}', response_model = Video)
async def update_video(video_id: int, updated_video: VideoBase):
    if not await is_active_video(video_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "video not found")
    if not await is_category_exists(updated_video.category_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Category not found")
    with Session(engine) as session:
        # Get the existing video from database
        current_video = session.get(Video, video_id)
        # Define a dictionary to loop thorugh fields
        video_dict = updated_video.model_dump(exclude_unset = True)
        # Loop is an alternative to doing each field on sepated lines
        for key, value in video_dict.items():
            setattr(current_video, key, value)
        current_video.date_last_modified = datetime.now()
        # Execute the UPDATE and save changes to database
        session.commit()
        # Reload object with latest database data
        session.refresh(current_video)
    return current_video

# Delete a video by setting is_active to False
@api.delete('/video/{video_id}', response_model = Video)
async def delete_video(video_id: int):
    if not await is_active_video(video_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Video not found")
    with Session(engine) as session:
        # Get the existing video from database
        current_video = session.get(Video, video_id)
        # Delete the video from database
        current_video.is_active = False
        current_video.date_last_modified = datetime.now()
        # Execute the DELETE and save changes to database
        session.commit()
    return { 'Deleted': video_id }

# Undelete a video by setting is_active to True
@api.delete('/video/{video_id}/undelete', response_model = Video)
async def undelete_video(video_id: int):
    with Session(engine) as session:
        # Get the existing video from database
        current_video = session.get(Video, video_id)
        if not current_video:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Video not found")
        # Restore the video
        current_video.is_active = True
        current_video.date_last_modified = datetime.now()
        # Execute the DELETE and save changes to database
        session.commit()
    return { 'Restored': video_id }

# endregion Videos

# region Forms
# Send empty form to add a video
@api.get('/add_video_form', response_class = responses.HTMLResponse)
async def get_add_video_form(request: Request):
    return templates.TemplateResponse('form_add_video.html', { 'request': request, 'categories': await get_categories() })

# Accept data from the form data and post it to the database
@api.post('/submit_video', response_class = responses.HTMLResponse)
async def post_add_video_form(request: Request, title: str = Form(), youtube_code: str = Form(), category_id: str = Form()):
    new_video = Video(title = title, youtube_code = youtube_code, category_id = int(category_id))
    with Session(engine) as session:
        session.add(new_video)
        session.commit()
        session.refresh(new_video)
    return templates.TemplateResponse('form_add_video.html', { 'request': request, 'new_video': new_video, 'page_title': 'Add a Video'})

# Send for editing a video
@api.get('/edit_video_form/{video_id}', response_class = responses.HTMLResponse)
async def get_edit_video_form(request: Request, video_id: int):
    return templates.TemplateResponse(
        'form_edit_video.html', {
            'video': session.get(Video, video_id),
            'request': request,
            'categories': await get_categories(),
            'page_title': 'Edit a Video'
        })

# Save edited video
@api.post('/edit_video_form/{video_id}')
async def submit_edit_video_form(video_id: int, title: str = Form(), youtube_code: str = Form(), category_id: str = Form()):
    updated_video = Video(id = video_id, title = title, youtube_code = youtube_code, category_id = int(category_id))
    # Open a new database session using the engine
    with Session(engine) as session:
        # Retrieve the current video object from the database using the provided video_id
        current_video = session.get(Video, video_id)
        # Create a dictionary of the updated video fields, excluding any fields that were not set
        video_dict = updated_video.model_dump(exclude_unset = True)
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
    return responses.RedirectResponse(url = "/list_video_form", status_code = status.HTTP_302_FOUND)

# Delete a video by setting is_active to False
@api.get('/delete_video_form/{video_id}')
async def delete_video_form(video_id: int):
    if not await is_active_video(video_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Video not found")
    with Session(engine) as session:
        current_video = session.get(Video, video_id)
        current_video.is_active = False
        current_video.date_last_modified = datetime.now()
        session.commit()
    return responses.RedirectResponse(url = "/list_video_form", status_code = status.HTTP_302_FOUND)
# endregion Forms

# region Joins
@api.get('/categorised_videos', response_model = list[CategorisedVideos])
async def get_category_videos():
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
@api.get('/list_video_form', response_class = responses.HTMLResponse)
async def get_list_video_form(request: Request):
    active_videos = session.exec(
        select(Video.id, Video.title, Video.youtube_code, Category.name.label('category_name'))
        .join(Category).
        where(Video.is_active)
        .order_by(Video.title)
    ).all()
    return templates.TemplateResponse('form_list_video.html', { 'request': request, 'videos': active_videos, 'page_title': 'List Videos' })
# endregion Joins

# region Validation Functions
async def is_category_exists(category_id: int):
    if session.get(Category, category_id):
        return True
    return False

async def is_category_name_exists(name: str):
    if session.exec(select(Category).where(Category.name == name)).one_or_none():
        return True
    return False

async def is_active_video(video_id: int):
    if session.exec(select(Video).where(Video.id == video_id, Video.is_active)).one_or_none():
        return True
    return False

async def count_videos(category_id: int):
    rows = session.exec(
        select(Video.category_id).where(Video.category_id == category_id, Video.is_active)
    ).all()
    return len(rows)
# endregion Validation Functions

# For debugging with breakpoints
if __name__ == '__main__':
    uvicorn.run(api, host='0.0.0.0', port=8000)
