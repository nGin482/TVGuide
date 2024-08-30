from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship, Session
from typing import TYPE_CHECKING

from database.database import Base, engine
if TYPE_CHECKING:
    from database.models import SearchItem, User


class UserSearchSubscription(Base):
    __tablename__ = "UserSearchSubscription"

    id: Mapped[int] = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = Column('user_id', Integer, ForeignKey('User.id'))
    search_id: Mapped[int] = Column('search_id', Integer, ForeignKey('SearchItem.id'))
    user: Mapped['User'] = relationship('User', back_populates='show_subscriptions')
    show_details: Mapped['SearchItem'] = relationship('SearchItem')

    def __init__(self, user_id: int, search_id: int):
        super().__init__()
        self.user_id = user_id
        self.search_id = search_id

    def __repr__(self) -> str:
        return f"Search Subscription (user: {self.user.username}, show: {self.show_details.show})"


UserSearchSubscription.metadata.create_all(engine, tables=[UserSearchSubscription.__table__])

