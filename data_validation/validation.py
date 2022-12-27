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
    def format_episode_title(title: str):
        """
        Format a show's given title into a more reader-friendly appearance
        """

        if ', The' in title:
            idx_the = title.find(', The')
            title = 'The ' + title[0:idx_the]
        if ', A' in title:
            idx_a = title.find(', A')
            title = 'A ' + title[0:idx_a]

        return title

    @staticmethod
    def check_show_titles(show: str):
        if 'Doctor Who: ' in show:
            return 'Doctor Who'
        elif 'Maigret' in show:
            return 'Maigret'
        elif 'Death in Paradise' in show:
            return 'Death In Paradise'
        elif 'Revenge Of The Fallen' in show or 'Dark Of The Moon' in show or 'Age of Extinction' in show or 'The Last Knight' in show or show == 'Transformers':
            return 'Transformers'
        elif 'Grantchester Christmas Special' in show:
            return 'Grantchester'
        title = show
        if ':' in title:
            title = title.replace(':', '')
        return title

    @staticmethod
    def remove_unwanted_shows(guide_list: list[dict]):
        remove_idx = []
        for idx, show in enumerate(guide_list):
            if 'New Orleans' in show['title'] or 'Hawaii' in show['title']:
                remove_idx.append(idx)
            if 'Vera' in show['title']:
                if show['title'] != 'Vera':
                    remove_idx.append(idx)
            if 'Endeavour' in show['title']:
                if show['title'] != 'Endeavour':
                    remove_idx.append(idx)
            if 'Lewis' in show['title']:
                if show['title'] != 'Lewis':
                    remove_idx.append(idx)
            if 'Death In Paradise' in show['title'] or 'Death in Paradise' in show['title']:
                if show['title'].lower() != 'death in paradise':
                    remove_idx.append(idx)
        for idx in reversed(remove_idx):
            guide_list.pop(idx)

        return guide_list

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
        return ['show', 'reminder time', 'interval']

    @staticmethod
    def unknown_episodes_check(show_list: list[dict]):
        shows_with_unknown_episodes = {}
        show_titles_with_unknown_episodes = [show for show in show_list if show['season_number'] == 'Unknown']
        for show in show_titles_with_unknown_episodes:
            if show['title'] in shows_with_unknown_episodes.keys():
                shows_with_unknown_episodes[show['title']].append(show['episode_title'])
            else:
                shows_with_unknown_episodes[show['title']] = [show['episode_title']]
        return shows_with_unknown_episodes
    
    @staticmethod
    def get_unknown_episode_number(show_list: list[dict], show_title: str, episode_title: str):
        unknown_episodes_map = Validation.unknown_episodes_check(show_list)
        show = list(unknown_episodes_map[show_title])
        return show.index(episode_title)
