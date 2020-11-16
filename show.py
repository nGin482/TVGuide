from datetime import date


class Show:

    def __init__(self, obj):
        self.title = obj['title']
        self.seasons = []

        season = Season(obj)
        self.seasons.append(season)

    def check_seasons(self, obj):
        flag = True
        for season in self.seasons:
            if 'series_num' in obj.keys():
                if obj['series_num'] == season.season_num:
                    flag = False
            else:
                if 'Unknown' in season.season_num:
                    flag = False

        return flag

    def find_season(self, obj):
        idx = -1

        if 'series_num' not in obj.keys():
            i = 0
            while i < len(self.seasons):
                season = self.seasons[i]
                if 'Unknown' in season.season_num:
                    idx = i
                i += 1
        else:
            i = 0
            while i < len(self.seasons):
                season = self.seasons[i]
                if obj['series_num'] == season.season_num:
                    idx = i
                i += 1
        return idx

    def get_unknown_season(self):
        result = None
        for season in self.seasons:
            if season.season_num == 'Unknown':
                result = season

        return result

    def get_known_seasons(self):
        result = []

        for season in self.seasons:
            if 'Unknown' not in season.season_num:
                result.append(season)

        return result

    def find_episode(self, obj):
        season_idx = self.find_season(obj)
        episode_idx = -1

        if season_idx != -1:
            season = self.seasons[season_idx]
            i = 0
            while i < len(season.episodes):
                episode = season.episodes[i]
                if 'episode_num' in obj.keys():
                    if obj['episode_num'] == episode.episode_num:
                        episode_idx = i
                elif 'episode_title' in obj.keys():
                    if obj['episode_title'] in episode.episode_title:
                        episode_idx = i
                i += 1

        return [season_idx, episode_idx]

    def cleanup_unknowns(self):
        episode_list = []

        unknown_season = self.get_unknown_season()
        if unknown_season is not None:
            for episode in unknown_season.episodes:
                episode_list.append({'title': episode, 'copy exists': False})

            for season in self.get_known_seasons():
                for episode in season.episodes:
                    for episode_one in episode_list:
                        if episode_one['title'].episode_title in episode.episode_title:
                            episode.add_channel(episode_one['title'].channels[0])
                            episode_one['copy exists'] = True

            for episode in episode_list:
                if episode['copy exists']:
                    i = 0
                    while i < len(self.get_unknown_season().episodes):
                        self.get_unknown_season().episodes[i] = None
                        i += 1

    def to_string(self):
        string = self.title + '\n'
        for season in self.seasons:
            string = string + 'Season: ' + season.season_num
            season.cleanup()
            for episode in season.episodes:
                string = string + '\n\t' + episode.episode_num + ', ' + episode.episode_title + ', ' + \
                         str(episode.channels) + ', ' + episode.first_air_date + ', ' + str(episode.repeat)
            string = string + '\n'

        string = string[:-1]
        return string

    def to_dict(self):
        show_dict = {
            'title': self.title,
            'seasons': []
        }
        for season in self.seasons:
            season_dict = season.to_dict()
            show_dict['seasons'].append(season_dict)

        return show_dict


class Season:
    def __init__(self, obj):
        if 'series_num' in obj.keys():
                self.season_num = obj['series_num']
        else:
            self.season_num = 'Unknown'
        self.episodes = []

    def get_episode(self, obj):
        result = None
        if 'episode_num' in obj.keys():
            for episode in self.episodes:
                if episode.episode_num == obj['episode_num']:
                    result = episode
        if 'episode_title' in obj.keys():
            for episode in self.episodes:
                if episode.episode_title == obj['episode_title']:
                    result = episode

        return result

    def cleanup(self):
        removal_list = []
        i = 0
        while i < len(self.episodes):
            if self.episodes[i] is None:
                removal_list.append(i)
            i += 1

        for idx in reversed(removal_list):
            self.episodes.pop(idx)

    def to_dict(self):
        season_dict = {
            'season num': self.season_num,
            'episodes': []
        }
        for episode in self.episodes:
            if episode is not None:
                episode_dict = episode.to_dict()
                season_dict['episodes'].append(episode_dict)

        return season_dict

    def create_episode(self, obj):
        episode = Episode()
        episode.set_episode_num(obj)
        episode.set_episode_title(obj)
        episode.add_channel(obj['channel'])
        self.episodes.append(episode)


class Episode:
    def __init__(self):
        self.episode_num = ''
        self.episode_title = ''
        self.channels = []
        self.first_air_date = date.strftime(date.today(), '%d-%m-%Y')
        self.repeat = False

    def set_episode_num(self, ep_obj):
        if 'episode_num' in ep_obj.keys():
            self.episode_num = ep_obj['episode_num']
        if 'episode num' in ep_obj.keys():
            self.episode_num = ep_obj['episode num']

    def set_episode_title(self, ep_obj):
        if 'episode_title' in ep_obj.keys():
            self.episode_title = ep_obj['episode_title']
        if 'episode title' in ep_obj.keys():
            self.episode_title = ep_obj['episode title']
        if 'episode' in ep_obj.keys():
            self.episode_title = ep_obj['episode']

    def add_channel(self, channel):
        if isinstance(channel, list):
            for c in channel:
                if c not in self.channels:
                    self.channels.append(c)
        else:
            if channel not in self.channels:
                self.channels.append(channel)

    def set_repeat(self):
        self.__setattr__('repeat', True)

    def to_dict(self):
        episode_dict = {
            'episode num': self.episode_num,
            'episode title': self.episode_title,
            'channels': self.channels,
            'first air date': self.first_air_date,
            'repeat': self.repeat
        }

        return episode_dict


class GuideShow:
    def __init__(self):
        self.title = ''
        self.time = ''
        self.channels = []
        self.season_num = ''
        self.episode_num = ''
        self.episode_title = ''

    def set_title(self, title):
        self.__setattr__('title', title)

    def set_time(self, time):
        self.__setattr__('title', time)

    def set_channel(self, channel):
        self.channels.append(channel)

    def set_season_num(self, season_num):
        self.__setattr__('title', season_num)

    def set_episode_num(self, episode_num):
        self.__setattr__('title', episode_num)

    def set_episode_title(self, episode_title):
        self.__setattr__('title', episode_title)
