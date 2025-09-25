from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

class CategoryBase(SQLModel):
    name: str = Field(min_length = 3, max_length = 15, index = True)

# SQLModel tables (table = True) are primarily designed for database operations
class Category(CategoryBase, table = True):
    # Auto-generated database ID
    id: Optional[int] = Field(default = None, primary_key = True)

class VideoBase(SQLModel):
    title: str = Field(min_length = 3, max_length = 128, index = True)
    # TODO: Fix regex validation for youtube code
    youtube_code: str = Field(regex = "[^ ]{11}$")
    category_id: int = Field(foreign_key = "category.id")

class Video(VideoBase, table = True):
    id: Optional[int] = Field(default = None, primary_key = True)
    is_active: bool = Field(default = True)
    date_created: datetime = Field(default_factory = datetime.now, nullable = False)
    date_last_modified: Optional[datetime] = Field(default = None, nullable = True)

# CategorisedVideos class for reading join tables
class CategorisedVideos(SQLModel):
    category_name: str
    title: str
    youtube_code: str