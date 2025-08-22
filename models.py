from sqlmodel import Field, SQLModel
from typing import Optional

class CategoryBase(SQLModel):
    name: str = Field(min_length = 3, max_length = 15, index = True)

# SQLModel tables (table = True) are primarily designed for database operations
class Category(CategoryBase, table = True):
    # Auto-generated database ID
    id: Optional[int] = Field(default = None, primary_key = True)