from sqlalchemy import Column, Integer, select, Text
from sqlalchemy.orm import Mapped, relationship, Session
from typing import TYPE_CHECKING
import bcrypt

from database import Base
if TYPE_CHECKING:
    from database.models import UserSearchSubscription


class User(Base):
    __tablename__ = 'User'

    id: Mapped[int] = Column('id', Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = Column('username', Text)
    password: Mapped[str] = Column('password', Text)
    role: Mapped[str] = Column('role', Text, default='User')
    show_subscriptions: Mapped[list['UserSearchSubscription']] = relationship('UserSearchSubscription', back_populates='user')

    def __init__(self, username: str, password: str, role: str = 'User'):
        super().__init__()
        self.username = username
        self.password = self.encrypt_password(password)
        self.role = role

    @staticmethod
    def get_all_users(session: Session):

        query = select(User)
        users = session.scalars(query)

        return [user for user in users]
    
    @staticmethod
    def search_for_user(username: str, session: Session):

        query = select(User).where(User.username == username)
        user = session.scalar(query)

        return user
    
    def add_user(self, session: Session):

        session.add(self)
        session.commit()

    def delete_user(self, session: Session):

        session.delete(self)
        session.commit()

    def encrypt_password(self, password: str):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(4))

        return hashed_password.decode()
    
    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode(), self.password.encode())
    
    def change_password(self, new_password: str):
        self.password = self.encrypt_password(new_password)
    
    def promote_role(self):
        self.role = 'Admin'

    def to_dict(self):
        return {
            'username': self.username,
            'role': self.role,
            'show_subscriptions': [subscription.search_item.to_dict() for subscription in self.show_subscriptions]
        }
