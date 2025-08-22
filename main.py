from fastapi import FastAPI, responses, HTTPException, status
from sqlmodel import Session, select
from models import Category, CategoryBase
from database import engine
import uvicorn

# App
api = FastAPI()
session = Session(bind = engine) # binds to our DB engine

# Routes
# Home page
@api.get('/', response_class = responses.HTMLResponse)
async def home():
    return '''
        <h1>Hello Wold! From an HTML respons</h1>
        <p>Here is the <a href="/docs">docs</a>
    '''

# Get all categories
@api.get('/category', response_model = list[Category])
async def get_categories():
    with Session(engine) as session:
        return session.exec(select(Category)).all()

# Get all categories in 
@api.get('/category', response_model = list[Category])
async def get_categories():
    with Session(engine) as session:
        return session.exec(select(Category).order_by(Category.name.desc())).all()

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

# Get a category
@api.get('/category/{category_id}', response_model = Category)
async def find_category(category_id: int):
    with Session(engine) as session:
        category = session.get(Category, category_id)
        if not await is_category_exists(category_id):
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Category not found")
        return category

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
    with Session(engine) as session:
        # Get the existing category from database
        current_category = session.get(Category, category_id)
        # Delete the category from database
        session.delete(current_category)
        # Execute the DELETE and save changes to database
        session.commit()
        return current_category


# VALIDATION FUNCTIONS
async def is_category_exists(category_id: int):
    if session.get(Category, category_id):
        return True
    return False

async def is_category_name_exists(name: str):
    if session.exec(select(Category).where(Category.name == name)).one_or_none():
        return True
    return False


# For debugging with breakpoints
if __name__ == '__main__':
    uvicorn.run(api, host='0.0.0.0', port=8000)
