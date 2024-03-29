from datetime import datetime
import pytz

class Validation:

    @staticmethod
    def format_time(time: str):
        """
        Format a show's start time to 24 hour time
        :param time: show start_time to format that will be passed as string
        :return: the formatted time string

        May become deprecated - only used by `search_BBC_channels()`
        """

        idx = time.find(':')
        time = time.strip()

        if len(time) == 6:
            time = '0' + time
        if 'pm' in time:
            time = time[:-2]
            if time[:idx] != '12':
                hour = int(time[:idx]) + 12
                time = str(hour) + time[idx:]
        if 'am' in time:
            time = time[:-2]
            if time[:idx] == '12':
                hour = int(time[:idx]) - 12
                time = str(hour) + '0' + time[idx:]

        return time

    @staticmethod
    def format_episode_title(episode_title: str):
        """
        Format a show's episode title into a more reader-friendly appearance
        """

        if ', The' in episode_title:
            idx_the = episode_title.find(', The')
            episode_title = 'The ' + episode_title[0:idx_the]
        if ', A' in episode_title and episode_title != 'Kolcheck, A.':
            idx_a = episode_title.find(', A')
            episode_title = 'A ' + episode_title[0:idx_a]

        return episode_title

    @staticmethod
    def check_show_titles(show: str):
        if 'Maigret' in show:
            return 'Maigret'
        elif 'Death in Paradise' in show:
            return 'Death In Paradise'
        elif 'Grantchester Christmas Special' in show:
            return 'Grantchester'
        elif 'NCIS Encore' in show:
            return 'NCIS'
        return show

    @staticmethod
    def extract_information(description: str) -> tuple:
        """
        Given a description from an IMDB API result, search this string for information regarding season number and episode number
        """
        import re

        try:
            desc_break = description.split('|')
        
            season_index = desc_break[0].index('Season ')+7
            season = desc_break[0][season_index:len(desc_break[0])-1]
            episode:str = desc_break[1][9:desc_break[1].index('-')-1]
        except ValueError:
            numbers = re.findall(r'\d+', description)
            season = numbers[1]
            episode = numbers[2]
        
        return season, int(episode)


    @staticmethod
    def valid_reminder_fields():
        """
        Returns the fields only valid for a reminder document
        """
        return ['show', 'reminder_alert', 'warning_time', 'ocassions']

    @staticmethod
    def get_unknown_episode_number(show_list: list[dict], show_title: str, episode_title: str):
        
        show_titles_with_unknown_episodes = [
            show for show in show_list if show['title'] == show_title and show['season_number'] == 'Unknown'
        ]
        if episode_title != '':
            return next(
                (index +1 for (index, show) in enumerate(show_titles_with_unknown_episodes) if show['episode_title'] == episode_title),
                len(show_titles_with_unknown_episodes)
            )
        return len(show_titles_with_unknown_episodes)
        
    @staticmethod
    def get_current_date():
        return datetime.now(pytz.timezone('Australia/Sydney'))
