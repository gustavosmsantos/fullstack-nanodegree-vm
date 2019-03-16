from persistence.config import engine, DbSession
from persistence.entities import Base, Category

Base.metadata.create_all(engine)

dbsession = DbSession()
dbsession.add(Category(name='Soccer'))
dbsession.add(Category(name='Basketball'))
dbsession.add(Category(name='Baseball'))
dbsession.add(Category(name='Frisbee'))
dbsession.add(Category(name='Snowboarding'))
dbsession.add(Category(name='Rock Climbing'))
dbsession.add(Category(name='Foosball'))
dbsession.add(Category(name='Skating'))
dbsession.add(Category(name='Hockey'))

dbsession.commit()
dbsession.close()