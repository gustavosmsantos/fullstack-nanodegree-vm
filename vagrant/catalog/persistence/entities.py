
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class Category(Base):
     __tablename__ = 'categories'

     id = Column(Integer, primary_key=True)
     name = Column(String, unique=True)
     items = relationship('Item')

     @property
     def serialize(self):
        return {
                'id': self.id,
                'name': self.name,
                'items': [item.serialize for item in self.items]
        }

class Item(Base):
     __tablename__ = 'items'

     id = Column(Integer, primary_key=True)
     name = Column(String, nullable=False)
     description = Column(String, nullable=False)
     user_id = Column(String, nullable=False)
     category_id = Column(Integer, ForeignKey('categories.id'))
     category = relationship('Category')

     @property
     def serialize(self):
        return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'category_id': self.category.id
        }