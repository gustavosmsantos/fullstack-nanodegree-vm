
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class Category(Base):
     __tablename__ = 'categories'

     id = Column(Integer, primary_key=True)
     name = Column(String, unique=True)

     def __repr__(self):
        return "<Category(name='%s')>" % (self.name)

class Item(Base):
     __tablename__ = 'items'

     id = Column(Integer, primary_key=True)
     name = Column(String, nullable=False, unique=True)
     description = Column(String, nullable=False)
     category_id = Column(Integer, ForeignKey('categories.id'))

     def __repr__(self):
        return "<Item(name='%s', description='%s')>" % (self.name, self.description)