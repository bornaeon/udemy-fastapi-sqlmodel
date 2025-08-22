from fastapi import FastAPI, responses
from sqlmodel import SQLModel, Session
from models import Category
from database import engine

# App
api = FastAPI()
session = Session(bind=engine) # binds to our DB engine

# Routes
# Home page
@api.get('/', response_class=responses.HTMLResponse)
async def home():
    return '''
        <h1>Hello Wold! From an HTML respons</h1>
        <p>Here is the <a href="/docs">docs</a>
    '''

# Get all categories
@api.get('/category')
async def get_categories():
    pass

# Post a new categoy
@api.post('/category')
async def create_category(category:Category):
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
@api.get('/category/{category_id}')
async def find_category(category_id:int):
    pass

# Update a category
@api.put('/category/{category_id}')
async def update_category(category_id:int):
    pass

# Delete a category
@api.delete('/category/{category_id}')
async def delete_category(category_id:int):
    pass