from database.models.RecordedShow import RecordedShow
from aux_methods.helper_methods import check_show_titles
import json
import os

def get_today_shows_data(list_of_shows: str):
    all_recorded_shows = RecordedShow.get_all_recorded_shows()

    today_shows: list[dict] = [recorded_show for recorded_show in all_recorded_shows if recorded_show['show'] in list_of_shows]
    for show_data in today_shows:
        del show_data['_id']
        with open(f'shows/{check_show_titles(show_data["show"])}.json', 'w+') as file:
            json.dump(show_data, file, indent='\t')

def tear_down():
    """
    Remove the JSON files created to read show data from the shows directory 
    """

    for show_file in os.listdir('shows'):
        os.remove(f'shows/{show_file}')
