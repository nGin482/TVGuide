from datetime import datetime
import pytz

class Validation:

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
