from persistence.config import engine
from persistence.entities import Base

Base.metadata.create_all(engine)