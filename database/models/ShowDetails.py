from sqlalchemy import ARRAY, Column, Integer, select, Text
from sqlalchemy.orm import Mapped, relationship, Session

from database.database import engine, Base
from database.models import GuideEpisode, Reminder, SearchItem, ShowEpisode


class ShowDetails(Base):
    __tablename__ = "ShowDetails"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    title = Column('title', Text)
    description = Column('description', Text)
    tvmaze_id = Column('tvmaze_id', Text)
    genres = Column('genres', ARRAY(Text))
    image = Column('image', Text)
    guide_episodes: Mapped[list['GuideEpisode']] = relationship('GuideEpisode', back_populates="show_details")
    search: Mapped['SearchItem'] = relationship('SearchItem', back_populates="show_details", uselist=False)
    show_episodes: Mapped[list['ShowEpisode']] = relationship('ShowEpisode', back_populates="show_details")
    reminder: Mapped['Reminder'] = relationship('Reminder', back_populates='show_details')

    def __init__(self, title: str, description: str, tvmaze_id: str, genres: list[str], image: str):
        super().__init__()
        self.title = title
        self.description = description
        self.tvmaze_id = tvmaze_id
        self.genres = genres
        self.image = image

    @staticmethod
    def get_all_shows():
        session = Session(engine)
        query = select(ShowDetails)
        results = session.execute(query).scalars().all()

        return [show for show in results]
    
    @staticmethod
    def get_show_by_title(title: str):
        session = Session(engine)
        
        query = select(ShowDetails).where(ShowDetails.title == title)
        show = session.execute(query).scalars().first()
        
        return show
    
    def add_show(self):
        session = Session(engine)

        session.add(self)
        session.commit()

        session.close()

    def update_show(self, field, value):
        session = Session(engine)

        setattr(self, field, value)
        session.commit()

        session.close()

    def delete_show(self):
        session = Session(engine)

        session.delete(self)
        session.commit()

        session.close()

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'tvmaze_id': self.tvmaze_id,
            'genres': self.genres,
            'image': self.image
        }

    def __repr__(self) -> str:
        return f"ShowDetails (title={self.title}, description={self.description}, tvmaze_id={self.tvmaze_id}, genres={self.genres}, image={self.image})"

ShowDetails.metadata.create_all(engine)
