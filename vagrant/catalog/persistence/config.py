from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///catalog.db', echo=True)
DbSession = sessionmaker(bind=engine)