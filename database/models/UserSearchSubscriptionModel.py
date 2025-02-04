from sqlalchemy import Column, ForeignKey, Integer, select
from sqlalchemy.orm import Mapped, relationship, Session
from typing import TYPE_CHECKING

from database import Base, engine
if TYPE_CHECKING:
    from database.models import SearchItem, User


class UserSearchSubscription(Base):
    __tablename__ = "UserSearchSubscription"

    id: Mapped[int] = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = Column('user_id', Integer, ForeignKey('User.id'))
    search_id: Mapped[int] = Column('search_id', Integer, ForeignKey('SearchItem.id'))
    user: Mapped['User'] = relationship('User', back_populates='show_subscriptions')
    search_item: Mapped['SearchItem'] = relationship('SearchItem')

    def __init__(self, user_id: int, search_id: int):
        super().__init__()
        self.user_id = user_id
        self.search_id = search_id

    @staticmethod
    def get_user_subscriptions(session: Session, user_id: str):
        query = select(UserSearchSubscription).where(UserSearchSubscription.user_id == user_id)
        subscriptions = session.scalars(query)
        
        return subscriptions

    def add_subscription_list(subscription_list: list["UserSearchSubscription"], session: Session):
        session.add_all(subscription_list)
        session.commit()

    def add_subscription(self, session: Session):
        session.add(self)
        session.commit()
        print(f"User {self.user.username} has subscribed to {self.search_item.show}")

    def remove_subscription(self, session: Session):
        session.delete(self)
        session.commit()
        print(f"User {self.user.username} has unsubscribed from {self.search_item.show}")

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'search_item_id': self.search_id
        }

    def __repr__(self) -> str:
        return f"Search Subscription (user_id: {self.user_id}, search_id: {self.search_id})"

