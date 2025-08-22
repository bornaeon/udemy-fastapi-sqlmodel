from sqlmodel import SQLModel, create_engine, Field, Session

# if we have a model in models.py that we want to create tables from
import models

# Creates a sqlite database
sqlite_url = f"sqlite:///database.db"

# echo=True is just for development
engine = create_engine(sqlite_url, echo=True)

# The database.db file wont be created until we actually execute database.py
if __name__ == '__main__':
    # Creates database.db, if it doesn't already exsit
    SQLModel.metadata.create_all(engine)