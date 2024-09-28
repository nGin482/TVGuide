from sqlalchemy.exc import NoReferencedTableError, ProgrammingError

from database import Base, engine
from database.models.GuideModel import Guide
from database.models.GuideEpisode import GuideEpisode
from database.models.Reminder import Reminder
from database.models.SearchItemModel import SearchItem
from database.models.ShowDetailsModel import ShowDetails
from database.models.ShowEpisodeModel import ShowEpisode
from database.models.User import User
from database.models.UserSearchSubscriptionModel import UserSearchSubscription


def create_tables(tables_to_create: str | list[str] = None):
    tables = Base.metadata.tables.values()
    
    if not tables_to_create or len(tables_to_create) == 0:
        tables = [table for table in tables]
    else:
        tables = [table for table in tables if table.fullname in tables_to_create]

    for table in tables:
        print(f"Creating table {table.fullname}")
        try:
            table.create(engine)
        except (ProgrammingError, NoReferencedTableError) as error:
            print(f"Error creating table {table.fullname}: {error.orig}")

def drop_tables(tables_to_drop: str | list[str] = None):
    tables = Base.metadata.tables.values()

    if not tables_to_drop or len(tables_to_drop) == 0:
        tables = [table for table in tables]
    else:
        tables = [table for table in tables if table.fullname in tables_to_drop]

    for table in tables:
        print(f"Dropping table {table.fullname}")
        table.drop(engine)
