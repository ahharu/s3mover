from sqlalchemy import Column, DateTime, String, Integer, func, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Avatar(Base):
    __tablename__ = 'avatars'
    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(128), nullable=False)

    def __repr__(self):
        return 'id: {}, path: {}'.format(
            self.id, self.path, self.instance_type)
