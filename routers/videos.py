from fastapi import APIRouter, HTTPException, status, responses
from sqlmodel import Session, select
from models import Video, VideoBase
from database import engine
from datetime import datetime
from services.validation import is_category_exists, is_active_video

router = APIRouter()

# Get all active videos
@router.get('/video', response_model=list[Video])
async def get_videos():
    with Session(engine) as session:
        return session.exec(select(Video).where(Video.is_active).order_by(Video.date_created)).all()

# Get a video
@router.get('/video/{video_id}', response_model=Video)
async def find_video(video_id: int):
    if not await is_active_video(video_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="video not found")
    with Session(engine) as session:
        video = session.get(Video, video_id)
        return video

# Post a new video
@router.post('/video', status_code=status.HTTP_201_CREATED)
async def post_video(video: VideoBase):
    # create a new video object from the data passed in
    new_video = Video.model_validate(video)
    # check if the video has a valid category id
    if not await is_category_exists(new_video.category_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    # post the video
    with Session(engine) as session:
        session.add(new_video)
        session.commit()
        session.refresh(new_video)
    return responses.RedirectResponse(url="/list_video_form", status_code=status.HTTP_302_FOUND)

# Update a video
@router.put('/video/{video_id}', response_model=Video)
async def update_video(video_id: int, updated_video: VideoBase):
    if not await is_active_video(video_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="video not found")
    if not await is_category_exists(updated_video.category_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    with Session(engine) as session:
        # Get the existing video from database
        current_video = session.get(Video, video_id)
        # Define a dictionary to loop through fields
        video_dict = updated_video.model_dump(exclude_unset=True)
        # Loop is an alternative to doing each field on separated lines
        for key, value in video_dict.items():
            setattr(current_video, key, value)
        current_video.date_last_modified = datetime.now()
        # Execute the UPDATE and save changes to database
        session.commit()
        # Reload object with latest database data
        session.refresh(current_video)
    return current_video

# Delete a video by setting is_active to False
@router.delete('/video/{video_id}', response_model=Video)
async def delete_video(video_id: int):
    if not await is_active_video(video_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    with Session(engine) as session:
        # Get the existing video from database
        current_video = session.get(Video, video_id)
        # Delete the video from database
        current_video.is_active = False
        current_video.date_last_modified = datetime.now()
        # Execute the DELETE and save changes to database
        session.commit()
    return {'Deleted': video_id}

# Undelete a video by setting is_active to True
@router.delete('/video/{video_id}/undelete', response_model=Video)
async def undelete_video(video_id: int):
    with Session(engine) as session:
        # Get the existing video from database
        current_video = session.get(Video, video_id)
        if not current_video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        # Restore the video
        current_video.is_active = True
        current_video.date_last_modified = datetime.now()
        # Execute the DELETE and save changes to database
        session.commit()
    return {'Restored': video_id}
