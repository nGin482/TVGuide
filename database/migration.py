from psycopg2.errors import Error, InvalidTextRepresentation
from sqlalchemy.exc import SQLAlchemyError, DataError
import os

from config import session
from database.DatabaseService import DatabaseService
from database.models.GuideModel import Guide
from database.models.GuideEpisode import GuideEpisode
from database.models.Reminder import Reminder
from database.models.SearchItemModel import SearchItem
from database.models.ShowDetailsModel import ShowDetails
from database.models.ShowEpisodeModel import ShowEpisode
from database.models.User import User
from database.models.UserSearchSubscriptionModel import UserSearchSubscription
from services.tvmaze import tvmaze_api

# migrate shows
# migrate guides
# migrate reminders
# migrate users

database_service = DatabaseService(os.getenv("TVGUIDE_DB"), os.getenv("DATABASE_NAME"))
search_items = database_service.get_search_list()
recorded_shows = database_service.get_all_recorded_shows()

ignore_shows = [
    "NCIS",
    "The Verandah",
    "Litvinenko",
    "NCIS: New Orleans",
    "NCIS: Los Angeles",
    "Transformers Prime Beast Hunters: Predacons Rising",
    "Transformers: Robots In Disguise"
]

def migrate():
    _migrate_shows()
    _migrate_guides()
    _migrate_reminders()
    _migrate_users()


def _migrate_shows():
    count = 0
    for recorded_show in recorded_shows:
        if recorded_show.title not in ignore_shows:
            search_item = next((item for item in search_items if item.show.lower() in recorded_show.title.lower()), None)
            print(recorded_show.title, search_item.show if search_item else search_item)
            tvmaze_data = tvmaze_api.get_show(recorded_show.title)
            if search_item and search_item.image != "":
                image = search_item.image
            else:
                if tvmaze_data is not None:
                    image = tvmaze_data['image']['original']
                else:
                    image = ""
            show_detail = ShowDetails(
                recorded_show.title,
                tvmaze_data['summary'] if tvmaze_data is not None else "",
                recorded_show.tvmaze_id,
                tvmaze_data['genres'] if tvmaze_data is not None else [],
                image
            )
            show_detail.add_show(session)
            print(show_detail, "\n")
            count += 1

            # create ShowEpisodes
            for season in recorded_show.seasons:
                season_number = season.season_number if season.season_number != "Unknown" else -1,
                for episode in season.episodes:
                    show_episode = ShowEpisode(
                        recorded_show.title,
                        season_number,
                        episode.episode_number,
                        episode.episode_title,
                        episode.summary,
                        episode.alternative_titles,
                        episode.channels,
                        episode.air_dates,
                        show_detail.id
                    )
                    show_episode.add_episode(session)
                    # print(show_episode, "\n")

            # create SearchItems
            if search_item:
                new_search_item = SearchItem(
                    recorded_show.title,
                    False,
                    recorded_show.find_latest_season().season_number,
                    search_item.conditions,
                    show_detail.id
                )
                new_search_item.add_search_item(session)
                # print(new_search_item, "\n")
    print(f"{count} of {len(recorded_shows)} shows added")

def _migrate_guides():
    guides = database_service.get_all_guides()
    count = 0

    for guide in guides:
        new_guide = Guide(guide.date)
        new_guide.add_guide(session)
        count += 1

        for fta_episode in guide.fta_shows:
            season_number = fta_episode.season_number if fta_episode.season_number != "Unknown" else -1,
            show_details = ShowDetails.get_show_by_title(fta_episode.title, session)
            show_episode = ShowEpisode.search_for_episode(
                fta_episode.title,
                season_number,
                fta_episode.episode_number,
                fta_episode.episode_title,
                session
            )
            try:
                guide_episode = GuideEpisode(
                    fta_episode.title,
                    fta_episode.channel,
                    fta_episode.time,
                    None,
                    season_number,
                    fta_episode.episode_number,
                    fta_episode.episode_title,
                    new_guide.id,
                    show_details.id if show_details is not None else None,
                    show_episode.id if show_episode is not None else None
                )
                guide_episode.add_episode(session)
            except (Exception, SQLAlchemyError, Error, DataError, InvalidTextRepresentation) as err:
                print(f"Could not create GuideEpisode: {fta_episode.title} Season {season_number} Episode {fta_episode.episode_number}")
                print(err)
    print(f"{count} of {len(guides)} guides added")

def _migrate_reminders():
    reminders = database_service.get_all_reminders()
    count = 0

    for old_reminder in reminders:
        show_details = ShowDetails.get_show_by_title(old_reminder.show, session)
        reminder = Reminder(
            old_reminder.show,
            old_reminder.reminder_alert,
            old_reminder.warning_time,
            old_reminder.occasions,
            show_details.id if show_details is not None else None
        )
        reminder.add_reminder(session)
        count += 1
    print(f"{count} of {len(reminders)} reminders added")
    

def _migrate_users():
    users = database_service.get_all_users()
    user_count = 0

    for user in users:
        new_user = User(
            f"{user.username}-{user_count}",
            user.password,
            user.role
        )
        new_user.add_user(session)
        subscription_count = 0
        for subscription in user.show_subscriptions:
            search_item = SearchItem.get_search_item(subscription, session)
            if search_item:
                user_sub = UserSearchSubscription(
                    new_user.id,
                    search_item.id if search_item is not None else None
                )
                user_sub.add_subscription(session)
                subscription_count += 1
            else:
                print(f"{subscription} not found in search items")
        print(f"{subscription_count} of {len(user.show_subscriptions)} subscriptions added")
        

        user_count += 1
    print(f"{user_count} of {len(users)} users added")