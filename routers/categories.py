from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session
from models import Category, CategoryBase
from database import engine
from services.validation import is_category_exists, is_category_name_exists, count_videos, get_categories

router = APIRouter()

# Get all categories
@router.get('/category', response_model=list[Category])
async def get_categories_endpoint():
    return await get_categories()

# Get all categories in order by name
# @router.get('/category', response_model = list[Category])
# async def get_categories():
#    with Session(engine) as session:
#        return session.exec(select(Category).order_by(Category.name.desc())).all()

# Get a category
@router.get('/category/{category_id}', response_model=Category)
async def find_category(category_id: int):
    with Session(engine) as session:
        category = session.get(Category, category_id)
        if not await is_category_exists(category_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category

# Post a new category
@router.post('/category')
async def create_category(category: CategoryBase):
    # Check if the category already exists and reject it
    if await is_category_name_exists(category.name):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Category already exists")

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
@router.put('/category/{category_id}', response_model=Category)
async def update_category(category_id: int, category: CategoryBase):
    if not await is_category_exists(category_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
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
@router.delete('/category/{category_id}', response_model=Category)
async def delete_category(category_id: int):
    if not await is_category_exists(category_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    # Check if the category has videos, then don't delete it
    if await count_videos(category_id) > 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Category has videos")
    with Session(engine) as session:
        # Get the existing category from database
        current_category = session.get(Category, category_id)
        # Delete the category from database
        session.delete(current_category)
        # Execute the DELETE and save changes to database
        session.commit()
        return {'Deleted': category_id}
