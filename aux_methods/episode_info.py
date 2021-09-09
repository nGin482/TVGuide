import requests
import json
import os

def search_episode_information(show: dict) -> dict:
    """
    Consult with IMDB API to gather more information about each episode, using any existing information
    """

    # get season number and episode number from episode title
    if 'series_num' not in show.keys() and 'episode_title' in show.keys():
        title = show['title']
        if 'Death In Paradise' in show['title']:
            title = 'Death in Paradise'
        
        episode_req = requests.get('https://imdb-api.com/en/API/SearchEpisode/' + os.getenv('IMDB_API') + '/' + title)
        
        if episode_req.status_code == 200:
            results = episode_req.json()['results']
            # view_imdb_api_results(show, results)
            for result in results:
                if title in result['description'] and show['episode_title'] == result['title']:
                    print(result['description'])
                    description = extract_information(result['description'])
                    show['series_num'] = description[0]
                    show['episode_num'] = description[1]
    
    # get episode title from season number and episode number
    if ('episode_title' not in show.keys() or show['episode_title'] == '') and 'series_num' in show.keys():
        show_id:str = get_show_id(show['title'])
        if show_id:
            season_req = requests.get('https://imdb-api.com/en/API/SeasonEpisodes/' + os.getenv('IMDB_API') + '/' + show_id + '/' + show['series_num'])
            if season_req.status_code == 200:
                episodes = season_req.json()['episodes']
                # view_imdb_api_results(show, episodes)
                for episode in episodes:
                    if episode['episodeNumber'] == show['episode_num']:
                        show['episode_title'] = episode['title']
           
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

def view_imdb_api_results(show: dict, results: dict) -> None:
    """
    Write the results from the IMDB API request to a JSON file
    """

    with open('aux_methods/imdb_api_results.json') as fd:
        results:list = json.load(fd)

    if type(show['time']) is not str:
        show['time'] = show['time'].strftime('%H:%M')
    results.append({'show': show, 'api_results': results})

    with open('aux_methods/imdb_api_results.json', 'w+') as fd:
        json.dump(results, fd, indent='\t')

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
        if show_title in tennant_special:
            return 'Tennant Specials', idx+1, tennant_special
    for idx, smith_special in enumerate(smith_specials):
        if show_title in smith_special:
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
    else:
        return show_title