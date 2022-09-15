from turtle import title
from database.models.RecordedShow import RecordedShow
from data_validation.validation import Validation
import json
import os

def get_today_shows_data(list_of_shows: list[str]):
    all_recorded_shows = RecordedShow.get_all_recorded_shows()

    list_of_shows = [Validation.check_show_titles(title) for title in list_of_shows]
    today_shows: list[dict] = [recorded_show for recorded_show in all_recorded_shows if recorded_show['show'] in list_of_shows]
    
    list_of_recorded_shows = [RecordedShow.from_database(show_data) for show_data in today_shows]
    list_of_recorded_shows = list(set(list_of_recorded_shows))
    return list_of_recorded_shows

def tear_down():
    """
    Remove the JSON files created to read show data from the shows directory 
    """

    for show_file in os.listdir('shows'):
        os.remove(f'shows/{show_file}')
