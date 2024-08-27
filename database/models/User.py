from sqlalchemy import Column, Integer, select, Text
from sqlalchemy.orm import Mapped, Session
import bcrypt

from database.database import Base, engine


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = Column('id', Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = Column('username', Text)
    password: Mapped[str] = Column('password', Text)
    role: Mapped[str] = Column('role', Text, default='User')

    def __init__(self, username: str, password: str, role: str = 'User'):
        super().__init__()
        self.username = username
        self.password = self.encrypt_password(password)
        self.role = role

    def get_all_users():
        session = Session(engine)

        query = select(User)
        users = session.scalars(query).all()

        return [user for user in users]
    
    @staticmethod
    def search_for_user(username: str):
        session = Session(engine)

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

    def is_authorised(self, operation: str):
        if self.role == 'Admin':
            return True
        else:
            if 'delete' in operation:
                if 'own-account' in operation:
                    return True
                return False
            if 'recorded_shows' in operation:
                return False
            return True

