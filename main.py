from fastapi import FastAPI, responses
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import categories, videos, forms, joins
import uvicorn

# App
api = FastAPI(
    title="Video Management API",
    description="A FastAPI application for managing videos and categories with SQLModel",
    version="1.0.0"
)

# Static files
api.mount("/static", StaticFiles(directory="static"), name="static")
# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
api.include_router(categories.router, prefix="/api", tags=["categories"])
api.include_router(videos.router, prefix="/api", tags=["videos"])
api.include_router(forms.router, tags=["forms"])
api.include_router(joins.router, prefix="/api", tags=["joins"])

# Home page
@api.get('/', response_class=responses.HTMLResponse)
async def home():
    return '''
        <h1>Hello World! From an HTML response</h1>
        <a href="/docs">Documentation</a> | <a href="/list_video_form">List of videos</a>
    '''

# For debugging with breakpoints
if __name__ == '__main__':
    uvicorn.run(api, host='0.0.0.0', port=8000)
