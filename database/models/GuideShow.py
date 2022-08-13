from datetime import datetime
from typing import Union
from data_validation.validation import Validation
from .RecordedShow import Episode, RecordedShow, Season


class GuideShow:
    title: str
    channel: str
    time: datetime
    episode_info: bool
    season_number: str
    episode_number: int
    episode_title: str
    repeat: bool

    def __init__(self, title: str, channel: str, time: datetime, episode_info: bool, season_number, episode_number, episode_title) -> None:
        episode_data = GuideShow.get_show(title, season_number, episode_title)
        if len(episode_data) > 0:
            title = episode_data[0]
            episode_info = episode_data[1]
            season_number = episode_data[2]
            episode_number = episode_data[3]
            episode_title = episode_data[4]
        
        self.title = Validation.check_show_titles(title)
        self.channel = channel
        self.time = time
        self.episode_info = episode_info
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = Validation.format_title(episode_title)
        self.repeat = self.search_for_repeats()

    @staticmethod
    def get_show(title: str, season_number, episode_title) -> tuple:
        if 'Transformers' in title:
            return TransformersGuideShow.handle(title)
        elif 'Doctor Who' in title:
            return DoctorWho.handle(title)
        elif 'Morse' in title:
            return MorseGuideShow.handle(title)
        elif 'Red Election' in title:
            return RedElection.handle(title, season_number, episode_title)
        else:
            return ()

    def search_for_repeats(self) -> bool:

        if self.episode_info:
            return self.find_recorded_episode()['status']

    def find_recorded_episode(self) -> dict['str', Union[Episode, Season, RecordedShow]]:
        """
        Checks the local files in the `shows` directory for information about a `GuideShow`'s information\n
        Returns a `dict` containting:\n
        `status: bool` (if information exists in the file)\n
        and either\n
        `episode: Episode` (the episode from the file); or
        `level: str` (what object needs to be created and added if `status` is False)
        """
        from repeat_handler import read_show_data
        check_show = read_show_data(self.title)
        # check_show = get_one_recorded_show(show['title'])
        if check_show:
            season_number = self.season_number
            if season_number == '':
                season_number = 'Unknown'
            season = check_show.find_season(season_number)
            if season:
                episode = season.find_episode(self.episode_number, self.episode_title)
                if episode:
                    # if show.season_number != '' and show.episode_number != 0 and season.season_number == 'Unknown':
                        # document_updated = update_recorded_episode(show)['status']
                        # if document_updated:
                        #     print(f"The document for {show['title']} was updated") # TODO: most likely will log this
                    return {'status': True, 'episode': episode}
                else:
                    return {'status': False, 'level': 'Episode', 'show': check_show}
            else:
                return {'status': False, 'level': 'Season', 'show': check_show}
        else:
            return {'status': False, 'level': 'Show', 'show': check_show}
    
    def message_string(self):
        """
        String that is displayed in the Guide's notification message
        """
        time = self.time.strftime('%H:%M')
        message = f'{time}: {self.title} is on {self.channel}'
        if self.season_number != '' and self.episode_number != '':
            message += f' (Season {self.season_number}, Episode {self.episode_number}'
            if self.episode_title != '':
                message += f': {self.episode_title}'
            message += ')\n'
        else:
            message += f' ({self.episode_title})\n'
        if self.repeat:
            message = message[:-1] + ' (Repeat)\n'

        return message

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'channel': self.channel,
            'time': self.time.strftime('%H:%M'),
            'episode_info': self.episode_info,
            'season_number': self.season_number,
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'repeat': self.repeat
        }

    def __repr__(self) -> str:
        return self.message_string()


class TransformersGuideShow:

    @staticmethod
    def handle(title: str):
        check_transformers = TransformersGuideShow.transformers_shows(title)
        if isinstance(check_transformers, tuple):
            if 'Bumblebee' in title:
                title = 'Transformers'
            return 'Transformers', True, str(check_transformers[0]), check_transformers[1], check_transformers[2]
        return ()

    @staticmethod
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

class DoctorWho:
    @staticmethod
    def handle(title: str) -> tuple[str, bool, str, int, str] | tuple:
        if title != 'Doctor Who':
            from log import logging_app
            logging_app(title)
            
            check_dw_title: tuple = DoctorWho.doctor_who_episodes(title)
            return 'Doctor Who', True, str(check_dw_title[0]), check_dw_title[1], check_dw_title[2]
        return ()
    
    @staticmethod
    def doctor_who_episodes(title: str) -> tuple:
        """
        Given an episode's title, return the `season number`, `episode number` and correct `episode title` of a Doctor Who episode
        """
        tennant_specials = ['The Next Doctor', 'Planet of the Dead', 'The Waters of Mars', 'The End of Time - Part 1', 'The End of Time - Part 2']
        smith_specials = ['The Snowmen', 'The Day of the Doctor', 'The Time of the Doctor']

        if 'Doctor Who: ' in title:
            title = title.split(': ')[1]
        
        for idx, tennant_special in enumerate(tennant_specials):
            if title.lower() in tennant_special.lower():
                return 'Tennant Specials', idx+1, tennant_special
        for idx, smith_special in enumerate(smith_specials):
            if title.lower() in smith_special.lower():
                return 'Smith Specials', idx+1, smith_special
        
        if 'Christmas Invasion' in title:
            return 2, 0, 'The Christmas Invasion'
        elif 'Runaway Bride' in title:
            return 3, 0, 'The Runaway Bride'
        elif 'Voyage Of The Damned' in title:
            return 4, 0, 'Voyage of the Damned'
        elif 'Christmas Carol' in title:
            return 6, 0, 'A Christmas Carol'
        elif 'Wardrobe' in title:
            return 7, 0, 'The Doctor, the Widow and the Wardrobe'
        elif 'Last Christmas' in title:
            return 9, 0, 'Last Christmas'
        elif 'Husbands Of River Song' in title:
            return 9, 13, 'The Husbands of River Song'
        elif 'Return Of Doctor Mysterio' in title:
            return 10, 0, 'The Return of Doctor Mysterio'
        elif 'Twice Upon A Time' in title:
            return 10, 13, 'Twice Upon a Time'
        elif 'Resolution' in title:
            return 11, 11, 'Resolution'
        elif 'Revolution Of The Daleks' in title:
            return 12, 11, 'Revolution of the Daleks'
        elif 'Eve of the Daleks' in title or 'Eve Of The Daleks' in title:
            return 13, 7, 'Eve of the Daleks'
        else:
            return title

class MorseGuideShow:

    @staticmethod
    def handle(title: str):
        titles = title.split(': ')
        episode = MorseGuideShow.morse_episodes(titles[1])
        
        return 'Inspector Morse', True, str(episode[0]), episode[1], episode[2]

    @staticmethod
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

class RedElection:

    def handle(title: str, season_number: str, episode_title: str):
        from log import logging_app
        logging_app(f'Logging Red Election Episode\nSeason Number: {season_number}\nEpisode title: {episode_title}')
        
        episode_details = title[title.find('Series'):]
        
        episode_detail_values = episode_details.split(' ')
        return 'Red Election', True, episode_detail_values[1], episode_detail_values[3], ''