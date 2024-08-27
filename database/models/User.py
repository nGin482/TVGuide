from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import Mapped, Session

from database.database import Base


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = Column('id', Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = Column('username', Text)
    password: Mapped[str] = Column('password', Text)
    role: Mapped[str] = Column('role', Text, default='User')

    def __init__(self, username: str, password: str, role: str = 'User'):
        super().__init__()
        self.username = username
        self.password = password
        self.role = role

    def add_user(self, session: Session):

        session.add(self)
        session.commit()

    def delete_user(self, session: Session):

        session.delete(self)
        session.commit()

