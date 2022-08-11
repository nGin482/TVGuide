from datetime import datetime
from data_validation.validation import Validation


class GuideShow:
    title: str
    channel: str
    time: datetime
    episode_info: bool
    season_number: str
    episode_number: int
    episode_title: str
    repeat: bool

    def __init__(self, title: str, channel: str, time: datetime, episode_info: bool, season_number = '', episode_number = 0, episode_title = '', repeat = False) -> None:
        self.title = Validation.check_show_titles(title)
        self.channel = channel
        self.time = time
        self.episode_info = episode_info
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = Validation.format_title(episode_title)
        self.repeat = repeat

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


class TransformersGuideShow(GuideShow):

    def transformers_handle(self):
        check_transformers = self.transformers_shows(super().title)
        if isinstance(check_transformers, tuple):
            if 'Bumblebee' in self.title:
                self.title = 'Transformers'
            super().episode_info = True
            super().season_number = str(check_transformers[0])
            super().episode_number = check_transformers[1]
            super().episode_title = check_transformers[2]
        return super()

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

class DoctorWhoGuideShow(GuideShow):
    def doctor_who_handle(self):
        check_dw_title = DoctorWhoGuideShow(self.title, self.channel, self.time, self.episode_info).doctor_who_episodes(self.title)
        if self.title != check_dw_title:
            super().title = 'Doctor Who'
            super().season_number = str(check_dw_title[0])
            super().episode_number = str(check_dw_title[1])
            super().episode_title = check_dw_title[2]
            super().episode_info = True
        return self
    
    def doctor_who_episodes(self, show_title: str) -> tuple:
        """
        Given an episode's title, return the `season number`, `episode number` and correct `episode title` of a Doctor Who episode
        """
        
        if self.title == 'Doctor Who':
            return self.title
        
        tennant_specials = ['The Next Doctor', 'Planet of the Dead', 'The Waters of Mars', 'The End of Time - Part 1', 'The End of Time - Part 2']
        smith_specials = ['The Snowmen', 'The Day of the Doctor', 'The Time of the Doctor']

        if 'Doctor Who: ' in self.title:
            self.title = self.title.split(': ')[1]
        
        for idx, tennant_special in enumerate(tennant_specials):
            if self.title.lower() in tennant_special.lower():
                return 'Tennant Specials', idx+1, tennant_special
        for idx, smith_special in enumerate(smith_specials):
            if self.title.lower() in smith_special.lower():
                return 'Smith Specials', idx+1, smith_special
        
        if 'Christmas Invasion' in self.title:
            return 2, 0, 'The Christmas Invasion'
        elif 'Runaway Bride' in self.title:
            return 3, 0, 'The Runaway Bride'
        elif 'Voyage Of The Damned' in self.title:
            return 4, 0, 'Voyage of the Damned'
        elif 'Christmas Carol' in self.title:
            return 6, 0, 'A Christmas Carol'
        elif 'Wardrobe' in self.title:
            return 7, 0, 'The Doctor, the Widow and the Wardrobe'
        elif 'Last Christmas' in self.title:
            return 9, 0, 'Last Christmas'
        elif 'Husbands Of River Song' in self.title:
            return 9, 13, 'The Husbands of River Song'
        elif 'Return Of Doctor Mysterio' in self.title:
            return 10, 0, 'The Return of Doctor Mysterio'
        elif 'Twice Upon A Time' in self.title:
            return 10, 13, 'Twice Upon a Time'
        elif 'Resolution' in self.title:
            return 11, 11, 'Resolution'
        elif 'Revolution Of The Daleks' in self.title:
            return 12, 11, 'Revolution of the Daleks'
        elif 'Eve of the Daleks' in self.title or 'Eve Of The Daleks' in self.title:
            return 13, 7, 'Eve of the Daleks'
        else:
            return self.title
