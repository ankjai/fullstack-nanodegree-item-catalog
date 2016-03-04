from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant

# Create an engine that stores data in the local directory's
# restaurantmenu.db file.
engine = create_engine('sqlite:///restaurantmenu.db')

# Create all tables in the engine. This is equivalent to 'Create Table'
# statement in SQL.
# bind engine obj to our base class
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

restaurants = session.query(Restaurant).all()

print restaurants

for i in restaurants:
    print i.name
