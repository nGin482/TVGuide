import re
from database.models import GuideShow
from log import log_silent_witness_episode
import requests
import json
import os

def search_episode_information(show: GuideShow) -> dict:
    """
    Consult with IMDB API to gather more information about each episode, using any existing information
    """

    clear_imdb_api_results()

    imdb_api_key = os.getenv('IMDB_API')    
    # get season number and episode number from episode title
    if (show.season_number == '' or show.season_number == 'Unknown') and show.episode_title != '':
        episode_title = show.episode_title
        if ' ' in episode_title:
            episode_title = show.episode_title.replace(' ', '%20')
        
        episode_req = requests.get(f'https://imdb-api.com/en/API/SearchEpisode/{imdb_api_key}/{episode_title}')
        
        if episode_req.status_code == 200:
            results: list[dict] = episode_req.json()['results']
            title = show.title
            if 'Death In Paradise' in show.title:
                title = 'Death in Paradise'
            view_imdb_api_results(show, results)
            if results:
                for result in results:
                    if title in result['description'] and show.episode_title.lower() == result['title'].lower():
                        print(result['description'])
                        description = extract_information(result['description'])
                        show.season_number = description[0]
                        show.episode_number = description[1]
            else:
                print(f"IMDB API returned None when looking up {show.title}'s {show.episode_title} episode")
                return show
    
    # get episode title from season number and episode number
    if show.episode_title == '' and show.season_number != '':
        show_id:str = get_show_id(show.title)
        if show_id:
            season_req = requests.get(f'https://imdb-api.com/en/API/SeasonEpisodes/{imdb_api_key}/{show_id}/{show.season_number}')
            if season_req.status_code == 200:
                episodes = season_req.json()['episodes']
                view_imdb_api_results(show, episodes)
                for episode in episodes:
                    if episode['episodeNumber'] == str(show.episode_number):
                        show.episode_title = episode['title']
           
    return show

def extract_information(description: str) -> tuple:
    """
    Given a description from an IMDB API result, search this string for information regarding season number and episode number
    """

    desc_break = description.split('|')
    
    season_index = desc_break[0].index('Season ')+7
    season = desc_break[0][season_index:len(desc_break[0])-1]
    
    episode:str = desc_break[1][9:desc_break[1].index('-')-1]
    
    return season, episode

def get_show_id(show_title: str) -> str:
    """
    If available, find the `imdb_id` key from the given show's JSON file.\n
    This is available after the document has been retrieved from the MongoDB cluster and saved to a JSON file
    """

    with open('shows/' + show_title + '.json') as fd:
        show_data = json.load(fd)
    
    if 'imdb_id' in show_data.keys():
        return show_data['imdb_id']

def view_imdb_api_results(show: GuideShow, imdb_results: dict):
    """
    Write the results from the IMDB API request to a JSON file
    """

    with open('aux_methods/imdb_api_results.json') as fd:
        results:list = json.load(fd)

    results.append({'show': show.to_dict(), 'api_results': imdb_results})

    with open('aux_methods/imdb_api_results.json', 'w+') as fd:
        json.dump(results, fd, indent='\t')

def clear_imdb_api_results():
    """
    Remove existing results from IMDB API searches
    """

    with open('aux_methods/imdb_api_results.json', 'w+') as fd:
        json.dump([], fd)

def morse_episodes(guide_title: str) -> tuple:
    """
    Given an episode's title, return the `season number`, `episode number` and correct `episode title` of an Inspector Morse episode
    """

    morse_titles = [
        {'Episodes': ['The Dead Of Jericho', 'The Silent World Of Nicholas Quinn', 'Service Of All The Dead']},
        {'Episodes':
            ['The Wolvercote Tongue', 'Last Seen Wearing', 'The Settling Of The Sun', 'Last Bus To Woodstock']},
        {'Episodes': ['Ghost In The Machine', 'The Last Enemy', 'Deceived By Flight', 'The Secret Of Bay 5B']},
        {'Episodes': ['The Infernal Spirit', 'The Sins Of The Fathers', 'Driven To Distraction',
                      'The Masonic Mysteries']},
        {'Episodes':
            ['Second Time Around', 'Fat Chance', 'Who Killed Harry Field?', 'Greeks Bearing Gifts', 'Promised Land']},
        {'Episodes': ['Dead On Time', 'Happy Families', 'The Death Of The Self', 'Absolute Conviction',
                      'Cherubim And Seraphim']},
        {'Episodes': ['Deadly Slumber', 'The Day Of The Devil', 'Twilight Of The Gods']},
        {'Episodes': ['The Way Through The Woods', 'The Daughters Of Cain', 'Death Is Now My Neighbour',
                      'The Wench Is Dead', 'The Remorseful Day']}]

    if 'Service Of All' in guide_title:
        return 1, 3, 'Service Of All The Dead'
    if 'Infernal Spirit' in guide_title:
        return 4, 1, 'The Infernal Serpent'
    if 'In Australia' in guide_title:
        return 5, 4, 'Promised Land'
    if 'Death Is' in guide_title:
        return 8, 3, 'Death Is Now My Neighbour'
    else:
        for season_idx, season in enumerate(morse_titles):
            for episode_idx, title in enumerate(season['Episodes']):
                if 'The' in guide_title and 'The' not in title:
                    title = 'The ' + title
                if guide_title in title:
                    return season_idx+1, episode_idx+1, title

def doctor_who_episodes(show_title: str) -> tuple:
    """
    Given an episode's title, return the `season number`, `episode number` and correct `episode title` of a Doctor Who episode
    """
    
    if show_title == 'Doctor Who':
        return show_title
    
    tennant_specials = ['The Next Doctor', 'Planet of the Dead', 'The Waters of Mars', 'The End of Time - Part 1', 'The End of Time - Part 2']
    smith_specials = ['The Snowmen', 'The Day of the Doctor', 'The Time of the Doctor']

    if 'Doctor Who: ' in show_title:
        show_title = show_title.split(': ')[1]
    
    for idx, tennant_special in enumerate(tennant_specials):
        if show_title.lower() in tennant_special.lower():
            return 'Tennant Specials', idx+1, tennant_special
    for idx, smith_special in enumerate(smith_specials):
        if show_title.lower() in smith_special.lower():
            return 'Smith Specials', idx+1, smith_special
    
    if 'Christmas Invasion' in show_title:
        return 2, 0, 'The Christmas Invasion'
    elif 'Runaway Bride' in show_title:
        return 3, 0, 'The Runaway Bride'
    elif 'Voyage Of The Damned' in show_title:
        return 4, 0, 'Voyage of the Damned'
    elif 'Christmas Carol' in show_title:
        return 6, 0, 'A Christmas Carol'
    elif 'Wardrobe' in show_title:
        return 7, 0, 'The Doctor, the Widow and the Wardrobe'
    elif 'Last Christmas' in show_title:
        return 9, 0, 'Last Christmas'
    elif 'Husbands Of River Song' in show_title:
        return 9, 13, 'The Husbands of River Song'
    elif 'Return Of Doctor Mysterio' in show_title:
        return 10, 0, 'The Return of Doctor Mysterio'
    elif 'Twice Upon A Time' in show_title:
        return 10, 13, 'Twice Upon a Time'
    elif 'Resolution' in show_title:
        return 11, 11, 'Resolution'
    elif 'Revolution Of The Daleks' in show_title:
        return 12, 11, 'Revolution of the Daleks'
    elif 'Eve of the Daleks' in show_title or 'Eve Of The Daleks' in show_title:
        return 13, 7, 'Eve of the Daleks'
    else:
        return show_title

def transformers_shows(transformers: str) -> tuple:
    if 'Fallen' in transformers:
        return 1, 2, 'Revenge of the Fallen'
    elif 'Dark' in transformers:
        return 1, 3, 'Dark of the Moon'
    elif 'Extinction' in transformers:
        return 1, 4, 'Age of Extinction'
    elif 'Knight' in transformers:
        return 1, 5, 'The Last Knight'
    elif 'Bumblebee' in transformers:
        return 1, 6, 'Bumblebee'
    elif transformers == 'Transformers':
        return 1, 1, 'Transformers'
    else:
        return transformers

def red_election(show: dict):
    
    show['episode_title'] = show['episode_title'][show['episode_title'].find('Series'):]
    
    if 'series_num' not in show.keys() or show['series_num'] == 'Unknown':
        episode_details = show['episode_title'].split(' ')
        show['series_num'] = episode_details[1]
        show['episode_num'] = episode_details[3]
    
    return show

def check_silent_witness(episode_title: str):

    """
    213	"Redemption - Part 1"
    214	"Redemption - Part 2"
    215	"Bad Love - Part 1"
    216	"Bad Love - Part 2"
    217	"Reputations - Part 1"
    218	"Reputations - Part 2"
    219	"Brother's Keeper - Part 1"
    220	"Brother's Keeper - Part 2"
    221	"Matters of Life and Death - Part 1"
    222	"Matters of Life and Death - Part 2"
    """

    season_24_episodes = ["Redemption - Part 1", "Redemption - Part 2", "Bad Love - Part 1", "Bad Love - Part 2", 
        "Reputations - Part 1", "Reputations - Part 2", "Brother's Keeper - Part 1", "Brother's Keeper - Part 2",
        "Matters of Life and Death - Part 1", "Matters of Life and Death - Part 2"]

    """
    txt = "Brother's Keeper - Part 1"
    txt2 = "Brother's Keeper (Part 1)"
    txt3 = "Brother's Keeper Part 1"

    x = re.search("[-(]", txt)
    print(x)

    y = re.search("[-(]", txt2)
    print(y)

    z = re.search("[-(]", txt3)
    print(z)

    """

    # if re.search('[-(]', episode_title):
    #     pass
    # else:
    #     if 'Part ' in episode_title:
    #         episode_title_name = episode_title[:episode_title.find(' Part ')]
    #         for idx, episode in enumerate(season_24_episodes):
    #             if episode_title_name.lower() == episode.lower():
    #                 return True, idx
    #         return False, -1

    for idx, episode in enumerate(season_24_episodes):
        if episode_title == episode:
            return True, idx
    return False, -1


# above method may not be working for all cases ie. would return false here --> "One Of Our Own Part 2"
# https://www.w3schools.com/python/python_regex.asp
def silent_witness_episode(show: dict):
    """
    Confirm that the given Silent Witness episode is from Season 24
    """

    if 'series_num' in show.keys():
        if show['series_num'] == '24':
            return {'status': True, 'show': show}
    else:
        print('Episode title: {episode_title}'.format(**show))

    check_episode = check_silent_witness(show['episode_title'])
        
    log_silent_witness_episode(show)
    if check_episode[0]:
        show['series_num'] = 24
        show['episode_num'] = check_episode[1] + 1
        return {'status': True, 'show': show}
    else:
        return {'status': False}