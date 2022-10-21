import requests
import logging
import os

from data_validation.validation import Validation
from exceptions.service_error import IMDBAPIRequestFailedError
from log import log_imdb_api_results, logging_app


def imdb_api(path: str):

    request = requests.get(f'https://imdb-api.com/en/API/{path}')
            
    response_data = dict(request.json())
    if request.status_code != 200 or ('errorMessage' in response_data.keys() and response_data['errorMessage'] != ''):
        raise IMDBAPIRequestFailedError(f'Error: {request.status_code}: {response_data["errorMessage"]}')
    return response_data

def search_for_season_number(show_title: str, episode_title: str):

    episode_title_url = episode_title.replace(' ', '%20') if ' ' in episode_title else episode_title
    episode_req = imdb_api(f'SearchEpisode/{os.getenv("IMDB_API")}/{episode_title_url}')
        
    if 'results' in episode_req.keys():
        results: list[dict] = episode_req['results']
        if results:
            if len(results) > 0:
                title = 'Death in Paradise' if 'Death In Paradise' in show_title else show_title
                log_imdb_api_results({'title': show_title, 'episode_title': episode_title}, results)
                for result in results:
                    if title in result['description'] and episode_title.lower() == result['title'].lower():
                        print(result['description'])
                        return Validation.extract_information(result['description'])
            else:
                print('There are no matches for this search')
    else:
        raise IMDBAPIRequestFailedError(f"IMDB API did not return a results field for {show_title}'s {episode_title} episode")

def search_for_episode_title(show_title: str, season_number: str, episode_number: int, imdb_id: str):

    if imdb_id is None or imdb_id == '':
        raise IMDBAPIRequestFailedError(f'The IMDB ID has not been provided. Please provide the IMDB ID for {show_title} to perform the request')
    
    request = imdb_api(f'SeasonEpisodes/{os.getenv("IMDB_API")}/{imdb_id}/{season_number}')

    if request is not None:
        log_message = f"Searching IMDB API with {show_title}'s season number ({season_number}) to retrieve episode title"
        logging_app(log_message, logging.INFO)
        
        for episode in request['episodes']:
            if episode['episodeNumber'] == str(episode_number):
                episode_title = str(episode['title'])
                return episode_title
        return ''