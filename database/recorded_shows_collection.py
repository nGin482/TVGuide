from pymongo import errors, ReturnDocument
from database.mongo import database
from aux_methods.helper_methods import get_today_date

# Handlers for all recorded data for each show

def recorded_shows_collection():
    db = database()
    if db is not None:
        recorded_shows = db.get_collection('RecordedShows')
        return recorded_shows
    else:
        return []

def get_all_recorded_shows():
    all_recored_shows = []
    for recorded_show in recorded_shows_collection().find():
        all_recored_shows.append(recorded_show)
    return all_recored_shows

def get_one_recorded_show(show):
    recorded_shows = get_all_recorded_shows()
    for recorded_show in recorded_shows:
        if show == recorded_show['show']:
            return {'status': True, 'show': recorded_show}
    return {'status': False, 'message': 'It does not look like this show has been recorded. Are you sure the show given is correct and is being recorded?'}

def insert_new_recorded_show(new_show):

    # check if insert is successful
    
    check_show = get_one_recorded_show(new_show['title'])
    if check_show['status']:
        return {'status': False, 'message': 'This show is already being recorded.'}
    else:
        recorded_show_document = {
            'show': new_show['title'],
            'seasons': []
        }
        season_object = {
            'season number': 'Unknown',
            'episodes': [
                {
                    'episode number': '',
                    'episode title': '',
                    'channels': [new_show['channel']],
                    'first air date': get_today_date('string'),
                    'repeat': False
                }
            ]
        }
        if 'series_num' in new_show.keys():
            season_object['season number'] = new_show['series_num']
            season_object['episodes'][0]['episode number'] = new_show['episode_num']
        if 'episode_title' in new_show.keys():
            season_object['episodes'][0]['episode title'] = new_show['episode_title']

        recorded_show_document['seasons'].append(season_object)
        print(recorded_show_document)
        inserted_show = recorded_shows_collection().insert_one(recorded_show_document)
        if inserted_show.inserted_id:
            return {'status': True, 'message': 'The show is now being recorded.', 'show': recorded_show_document}
        else:
            return {'status': False, 'message': 'The show was not able to be recorded.', 'show': recorded_show_document}

def insert_new_season(show):
    season_check = check_season(show)
    
    if season_check['status']:
        return season_check
    else:
        season_object = {
            'season number': 'Unknown',
            'episodes': [
                {
                    'episode number': '',
                    'episode title': '',
                    'channels': [show['channel']],
                    'first air date': get_today_date('string'),
                    'repeat': False
                }
            ]
        }
        if 'series_num' in show.keys():
            season_object['season number'] = show['series_num']
            season_object['episodes'][0]['episode number'] = show['episode_num']
        if 'episode_title' in show.keys():
            season_object['episodes'][0]['episode title'] = show['episode_title']

    inserted_season = recorded_shows_collection().find_one_and_update(
        {'show': show['title']},
        {'$push': {'seasons': season_object}},
        return_document=ReturnDocument.AFTER
    )
    if 'series_num' in show.keys():
        new_season = list(filter(lambda season: season['season number'] == show['series_num'], inserted_season['seasons']))
    else:
        new_season = list(filter(lambda season: season['season number'] == 'Unknown', inserted_season['seasons']))
        
    if len(new_season) > 0:
        return {'status': True, 'message': 'The season was added to ' + show['title'] + '.', 'season': inserted_season['seasons'][-1]}
    else:
        return {'status': False, 'message': 'The season was not added to ' + show['title'] + '.', 'season': inserted_season}

def insert_new_episode(show):
    episode_check = check_episode(show)
    
    if episode_check['status']:
        return episode_check
    else:
        episode_object = {
            'episode number': '',
            'episode title': '',
            'channels': [show['channel']],
            'first air date': get_today_date('string'),
            'repeat': False
        }

        if 'episode_num' in show.keys():
            episode_object['episode number'] = show['episode_num']
        if 'episode_title' in show.keys():
            episode_object['episode title'] = show['episode_title']

        try:
            if 'series_num' in show.keys():
                inserted_episode = recorded_shows_collection().find_one_and_update(
                    {'show': show['title'], 'seasons.season number': show['series_num']},
                    {'$push': {'seasons.$.episodes': episode_object}},
                    return_document=ReturnDocument.AFTER
                )

                season = list(filter(lambda season: season['season number'] == show['series_num'], inserted_episode['seasons']))
                new_episode = list(filter(lambda episode: episode['episode number'] == show['episode_num'], season[0]['episodes']))

                if len(new_episode) > 0:
                    result = {
                        'season': season[0]['season number'],
                        'episode': new_episode
                    }
                    return {'status': True, 'message': 'The episode was added to ' + show['title'] + '.', 'insert_episode_result': result}
                else:
                    return {'status': False, 'message': 'The episode was not added to ' + show['title'] + '.', 'episode': episode_object}
            else:
                inserted_episode = recorded_shows_collection().find_one_and_update(
                    {'show': show['title'], 'seasons.season number': 'Unknown'},
                    {'$push': {'seasons.$.episodes': episode_object}},
                    return_document=ReturnDocument.AFTER    
                )

                seasons = list(filter(lambda season: season['season number'] == 'Unknown', inserted_episode['seasons']))
                episode = list(filter(lambda episode: episode['episode title'] == show['episode_title'], seasons[0]['episodes']))

                if len(episode) > 0:
                    result = {
                        'season': season['season number'],
                        'episode': episode
                    }
                    return {'status': True, 'message': 'The episode was added to ' + show['title'] + '.', 'insert_episode_result': result}
                else:
                    return {'status': False, 'message': 'The episode was not added to ' + show['title'] + '.', 'episode': episode_object}
        except (errors.WriteError, KeyError) as err:
            return {'status': False, 'message': 'An error occurred when trying to add this episode.', 'error': err}

def mark_as_repeat(show):
    
    repeat_check = check_repeat(show)
    if repeat_check:
        return {'status': False, 'message': 'This episode is already marked as a repeat.'}
    try:
        if 'series_num' in show.keys():
            updated_show = recorded_shows_collection().find_one_and_update(
                {'show': show['title']},
                {'$set': {'seasons.$[season].episodes.$[episode].repeat': True}},
                upsert = False,
                array_filters = [
                    {'season.season number': show['series_num']},
                    {'episode.episode number': show['episode_num']}
                ],
                return_document = ReturnDocument.AFTER
            )
            
            updated_season = list(filter(lambda season: season['season number'] == show['series_num'], updated_show['seasons']))[0]
            updated_episode = list(filter(lambda episode: episode['episode number'] == show['episode_num'], updated_season['episodes']))[0]
            
            if updated_episode['repeat']:
                result = {
                    'show': show['title'],
                    'season': updated_season['season number'],
                    'episode': updated_episode
                }
                return {'status': True, 'message': 'The episode has been marked as a repeat.', 'episode': result}
            else:
                return {'status': False, 'message': 'The episode has not been marked as a repeat.', 'episode': show}
        else:
            updated_show = recorded_shows_collection().find_one_and_update(
                {'show': show['title']},
                {'$set': {'seasons.$[season].episodes.$[episode].repeat': True}},
                upsert = False,
                array_filters = [
                    {'season.season number': 'Unknown'},
                    {'episode.episode title': show['episode_title']}
                ],
                return_document = ReturnDocument.AFTER
            )
            updated_season = list(filter(lambda season: season['season number'] == 'Unknown', updated_show['seasons']))[0]
            updated_episode = list(filter(lambda episode: episode['episode title'] == show['episode_title'], updated_season['episodes']))[0]
            
            if updated_episode['repeat']:
                result = {
                    'show': show['title'],
                    'season': updated_season['season number'],
                    'episode': updated_episode
                }
                return {'status': True, 'message': 'The episode has been marked as a repeat.', 'episode': result}
            else:
                return {'status': False, 'message': 'The episode has not been marked as a repeat.', 'episode': show}
    except (errors.WriteError, TypeError, KeyError) as err:
        return {'status': False, 'message': 'An error occurred when trying to mark this episode as a repeat.', 'error': err, 'episode': show}

def add_channel(show):

    if not check_channel(show):
        try:
            if 'series_num' in show.keys():
                updated_show = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$push': {'seasons.$[season].episodes.$[episode].channels': show['channel']}},
                    upsert = True,
                    array_filters = [
                        {'season.season number': show['series_num']},
                        {'episode.episode number': show['episode_num']}
                    ],
                    return_document = ReturnDocument.AFTER
                )
                message = 'The channel has been added to the list for this episode.'
                if 'ABC1' in show['channel']:
                    updated_show = recorded_shows_collection().find_one_and_update(
                        {'show': show['title']},
                        {'$push': {'seasons.$[season].episodes.$[episode].channels': 'ABCHD'}},
                        upsert = True,
                        array_filters = [
                            {'season.season number': show['series_num']},
                            {'episode.episode number': show['episode_num']}
                        ],
                        return_document = ReturnDocument.AFTER
                    )
                    message = message + ' ABCHD has also been added to the list.'
                
                updated_season = list(filter(lambda season: season['season number'] == show['series_num'], updated_show['seasons']))[0]
                updated_episode = list(filter(lambda episode: episode['episode number'] == show['episode_num'], updated_season['episodes']))[0]
                
                if show['channel'] in updated_episode['channels']:
                    return {'status': True, 'message': message, 'episode': updated_episode}
                else:
                    return {'status': False, 'message': 'The channel has not been added.', 'episode': show}
            else:
                updated_show = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$push': {'seasons.$[season].episodes.$[episode].channels': show['channel']}},
                    upsert = True,
                    array_filters = [
                        {'season.season number': 'Unknown'},
                        {'episode.episode title': show['episode_title']}
                    ],
                    return_document = ReturnDocument.AFTER
                )
                updated_season = list(filter(lambda season: season['season number'] == 'Unknown', updated_show['seasons']))[0]
                updated_episode = list(filter(lambda episode: episode['episode title'] == show['episode_title'], updated_season['episodes']))[0]
                
                if show['channel'] in updated_episode['channels']:
                    return {'status': True, 'message': 'The channel has been added to the list for this episode.', 'episode': updated_episode}
                else:
                    return {'status': False, 'message': 'The channel has not been added.', 'episode': show}
        except errors.WriteError as err:
            return {'status': False, 'message': 'An error occurred when trying to mark this episode as a repeat.', 'error': err, 'episode': show}
        except errors.OperationFailure as err:
            return {'status': False, 'message': 'An error occurred when trying to mark this episode as a repeat.', 'error': err, 'episode': show}
        except TypeError as err:
            return {'status': False, 'message': 'An error occurred when trying to mark this episode as a repeat.', 'error': err, 'episode': show}
    else:
        return {'status': False, 'message': 'The channel given is already listed.'}

def delete_recorded_show(show):
    check_show = get_one_recorded_show(show)

    if not check_show['status']:
        return {'status': False, 'message': show + ' can not be found in the database.'}
    else:
        deleted_show = recorded_shows_collection().find_one_and_delete(
            {'show': show},
        )
        check_again = get_one_recorded_show(show)
        if check_again['status'] is False:
            return {'status': True, 'message': show + ' is no longer in the database.', 'show': deleted_show}
        else:
            return {'status': False, 'message': show + ' has not been removed from the database.', 'show': deleted_show}

def remove_recorded_season(show):
    check_for_season = check_season(show)
    if check_for_season['status']:
        if 'series_num' in show.keys():
            try:
                removed_season = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$pull': {'seasons': {'season number': show['series_num']}}},
                    return_document = ReturnDocument.AFTER
                )
            except errors.OperationFailure as err:
                return {'status': False, 'message': 'An error occurred when trying to remove this season.', 'error': err}
        elif 'season number' in show.keys():
            try:
                removed_season = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$pull': {'seasons': {'season number': show['season number']}}},
                    return_document = ReturnDocument.AFTER
                )
            except errors.OperationFailure as err:
                return {'status': False, 'message': 'An error occurred when trying to remove this season.', 'error': err}            
        else:
            try:
                removed_season = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$pull': {'seasons': {'season number': 'Unknown'}}},
                    return_document = ReturnDocument.AFTER
                )
            except errors.OperationFailure as err:
                return {'status': False, 'message': 'An error occurred when trying to remove this season.', 'error': err}
        
        check_again = check_season(show)
        if check_again['status'] is False:
            return {'status': True, 'message': 'The season has been removed from the database.', 'season': removed_season}
        else:
            return {'status': False, 'message': 'The season has not been removed from the database.', 'season': removed_season}
    else:
        return check_for_season

def remove_recorded_episode(show):
    check_for_episode = check_episode(show)
    if check_for_episode['status']:
        if 'episode_num' in show.keys():
            try:
                removed_episode = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$pull': {'seasons.$[season].episodes': {'episode number': show['episode_num']}}},
                    array_filters = [
                        {'season.season number': show['series_num']}
                    ],
                    return_document = ReturnDocument.AFTER
                )
            except errors.OperationFailure as err:
                return {'status': False, 'message': 'An error occurred when trying to remove this episode.', 'error': err}
        elif 'episode number' in show.keys():
            try:
                removed_episode = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$pull': {'seasons.$[season].episodes': {'episode number': show['episode number']}}},
                    array_filters = [
                        {'season.season number': show['series_num']}
                    ],
                    return_document = ReturnDocument.AFTER
                )
            except errors.OperationFailure as err:
                return {'status': False, 'message': 'An error occurred when trying to remove this episode.', 'error': err}
        else:
            try:
                removed_episode = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$pull': {'seasons.$[season].episodes': {'episode title': show['episode_title']}}},
                    array_filters = [
                        {'season.season number': 'Unknown'}
                    ],
                    return_document = ReturnDocument.AFTER
                )
            except errors.OperationFailure as err:
                return {'status': False, 'message': 'An error occurred when trying to remove this episode.', 'error': err}
        
        check_again = check_episode(show)
        if check_again['status'] is False:
            return {'status': True, 'message': 'The episode has been removed from the database.', 'episode': removed_episode}
        else:
            return {'status': False, 'message': 'The episode has not been removed from the database.', 'episode': removed_episode}
    else:
        return check_for_episode

def remove_recorded_channel(show):
    check_for_channel = check_channel(show)
    if check_for_channel:
        if 'series_num' in show.keys():
            try:
                removed_channel = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$pull': {'seasons.$[season].episodes.$[episode].channels': show['channel']}},
                    array_filters = [
                        {'season.season number': show['series_num']},
                        {'episode.episode number': show['episode_num']},
                    ],
                    return_document = ReturnDocument.AFTER
                )
                updated_season = list(filter(lambda season: season['season number'] == show['series_num'], removed_channel['seasons']))[0]
                updated_episode = list(filter(lambda episode: episode['episode number'] == show['episode_num'], updated_season['episodes']))[0]
            except errors.OperationFailure as err:
                return {'status': False, 'message': 'An error occurred when trying to remove this channel.', 'error': err}
        elif 'season number' in show.keys():
            try:
                removed_channel = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$pull': {'seasons.$[season].episodes.$[episode].channels': show['channel']}},
                    array_filters = [
                        {'season.season number': show['series number']},
                        {'episode.episode number': show['episode number']},
                    ],
                    return_document = ReturnDocument.AFTER
                )
                updated_season = list(filter(lambda season: season['season number'] == show['season number'], removed_channel['seasons']))[0]
                updated_episode = list(filter(lambda episode: episode['episode number'] == show['episode number'], updated_season['episodes']))[0]
            except errors.OperationFailure as err:
                return {'status': False, 'message': 'An error occurred when trying to remove this channel.', 'error': err}
        else:
            try:
                removed_channel = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$pull': {'seasons.$[season].episodes.$[episode].channels': show['channel']}},
                    array_filters = [
                        {'season.season number': 'Unknown'},
                        {'episode.episode title': show['episode_title']},
                    ],
                    return_document = ReturnDocument.AFTER
                )
                updated_season = list(filter(lambda season: season['season number'] == 'Unknown', removed_channel['seasons']))[0]
                updated_episode = list(filter(lambda episode: episode['episode title'] == show['episode_title'], updated_season['episodes']))[0]
            except errors.OperationFailure as err:
                return {'status': False, 'message': 'An error occurred when trying to remove this channel.', 'error': err}
        
        check_again = check_channel(show)
        if check_again is False:
            return {'status': True, 'message': 'The channel has been removed from the database.', 'channel': updated_episode}
        else:
            return {'status': False, 'message': 'The channel has not been removed from the database.', 'channel': updated_episode}
    else:
        return check_for_channel

def check_season(show):
    recorded_show = get_one_recorded_show(show['title'])
    if recorded_show['status']:
        seasons = recorded_show['show']['seasons']

        if 'series_num' in show.keys():
            season_to_check = show['series_num']
            season_check = list(filter(lambda season: season['season number'] == show['series_num'], seasons))
        else:
            season_to_check = 'Unknown'
            season_check = list(filter(lambda season: season['season number'] == 'Unknown', seasons))
        
        if len(season_check) > 0:
            return {'status': True, 'message': 'This season has already been listed.', 'season': season_to_check}
        else:
            return {'status': False}

def check_episode(show):
    recorded_show_check = get_one_recorded_show(show['title'])
    if recorded_show_check['status']:
        seasons = recorded_show_check['show']['seasons']

        if 'episode_num' in show.keys():
            episode_to_check = show['episode_num']

            season_check = list(filter(lambda season: season['season number'] == show['series_num'], seasons))[0]
            episode_check = list(filter(lambda episode: episode['episode number'] == episode_to_check, season_check['episodes']))
        else:
            episode_to_check = show['episode_title']

            season_check = list(filter(lambda season: season['season number'] == 'Unknown', seasons))[0]
            episode_check = list(filter(lambda episode: episode['episode title'] == episode_to_check, season_check['episodes']))
        
        if len(episode_check) > 0:
            if 'episode_num' in show.keys():
                episode_for_message = 'Season ' + show['series_num'] + ', Episode ' + show['episode_num']
            else:
                episode_for_message = show['episode_title']
            return {'status': True, 'message': 'This episode has already been listed.', 'episode': episode_for_message}
        else:
            return {'status': False}
    else:
        return recorded_show_check
            

def check_channel(show):
    recorded_show = get_one_recorded_show(show['title'])
    if recorded_show['status']:
        result = recorded_show['show']['seasons']
    
    if 'series_num' in show.keys():
        season = list(filter(lambda season: season['season number'] == show['series_num'], result))[0]
        episode = list(filter(lambda episode: episode['episode number'] == show['episode_num'], season['episodes']))[0]
    else:
        season = list(filter(lambda season: season['season number'] == 'Unknown', result))[0]
        episode = list(filter(lambda episode: episode['episode title'] == show['episode_title'], season['episodes']))[0]
    
    if show['channel'] in episode['channels']:
        return True
    else:
        return False

def check_repeat(show):
    """
    Checks if the given episode is a repeat
    """
    recorded_show = get_one_recorded_show(show['title'])
    if recorded_show['status']:
        result = recorded_show['show']['seasons']
    
    if 'series_num' in show.keys():
        season = list(filter(lambda season: season['season number'] == show['series_num'], result))[0]
        episode = list(filter(lambda episode: episode['episode number'] == show['episode_num'], season['episodes']))[0]
    else:
        season = list(filter(lambda season: season['season number'] == 'Unknown', result))[0]
        episode = list(filter(lambda episode: episode['episode title'] == show['episode_title'], season['episodes']))[0]
    
    if episode['repeat']:
        return True
    else:
        return False