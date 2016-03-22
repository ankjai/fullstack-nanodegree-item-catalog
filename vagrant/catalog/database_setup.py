from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    image = Column(String(250))


class Restaurant(Base):
    __tablename__ = 'restaurant'
    # here we define columns for the table restaurant
    # these columns are also python instance attribute
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User, backref=backref('restaurant', cascade='all,delete'))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': str(self.id)
        }


class MenuItem(Base):
    __tablename__ = 'menu_item'
    # here we define columns for the table restaurant
    # these columns are also python instance attribute
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    restaurant = relationship(Restaurant, backref=backref("menu_item", cascade="all,delete"))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User, backref=backref('menu_item', cascade='all,delete'))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': str(self.id),
            'price': self.price,
            'course': self.course
        }


# Create an engine that stores data in the local directory's
# restaurantapp.db file.
engine = create_engine('sqlite:///restaurantapp.db')

# Create all tables in the engine. This is equivalent to 'Create Table'
# statement in SQL.
# bind engine obj to our base class
Base.metadata.create_all(engine)
