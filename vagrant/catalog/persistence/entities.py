
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Category(Base):
     __tablename__ = 'categories'

     id = Column(Integer, primary_key=True)
     name = Column(String)

     def __repr__(self):
        return "<Category(name='%s')>" % (self.name)