from abc import ABC, abstractmethod

class SpecialCases(ABC):

    @abstractmethod
    def handle():
        raise NotImplementedError

class TransformersGuideShow(SpecialCases):

    @staticmethod
    def handle(title: str):
        check_transformers = TransformersGuideShow.transformers_shows(title)
        if isinstance(check_transformers, tuple):
            if 'Bumblebee' in title:
                title = 'Transformers'
            return 'Transformers', str(check_transformers[0]), check_transformers[1], check_transformers[2]
        return ()

    @staticmethod
    def transformers_shows(transformers: str) -> tuple:
        if 'Fallen' in transformers:
            return '1', 2, 'Revenge of the Fallen'
        elif 'Dark' in transformers:
            return '1', 3, 'Dark of the Moon'
        elif 'Extinction' in transformers:
            return '1', 4, 'Age of Extinction'
        elif 'Knight' in transformers:
            return '1', 5, 'The Last Knight'
        elif 'Bumblebee' in transformers:
            return '1', 6, 'Bumblebee'
        elif transformers == 'Transformers':
            return '1', 1, 'Transformers'
        else:
            return transformers

class DoctorWho(SpecialCases):
    @staticmethod
    def handle(title: str) -> tuple[str, str, int, str] | tuple:
        if title != 'Doctor Who':
            from log import logging_app
            logging_app(title)
            
            check_dw_title: tuple = DoctorWho.doctor_who_episodes(title)
            return 'Doctor Who', str(check_dw_title[0]), check_dw_title[1], check_dw_title[2]
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
            return '2', 0, 'The Christmas Invasion'
        elif 'Runaway Bride' in title:
            return '3', 0, 'The Runaway Bride'
        elif 'Voyage Of The Damned' in title:
            return '4', 0, 'Voyage of the Damned'
        elif 'Christmas Carol' in title:
            return '6', 0, 'A Christmas Carol'
        elif 'Wardrobe' in title:
            return '7', 0, 'The Doctor, the Widow and the Wardrobe'
        elif 'Last Christmas' in title:
            return '9', 0, 'Last Christmas'
        elif 'Husbands Of River Song' in title:
            return '9', 13, 'The Husbands of River Song'
        elif 'Return Of Doctor Mysterio' in title:
            return '10', 0, 'The Return of Doctor Mysterio'
        elif 'Twice Upon A Time' in title:
            return '10', 13, 'Twice Upon a Time'
        elif 'Resolution' in title:
            return '11', 11, 'Resolution'
        elif 'Revolution Of The Daleks' in title:
            return '12', 11, 'Revolution of the Daleks'
        elif 'Eve of the Daleks' in title or 'Eve Of The Daleks' in title:
            return '13', 7, 'Eve of the Daleks'
        elif 'The Power Of The Doctor' in title:
            return '13', 9, 'Power of the Doctor'
        else:
            return title

class MorseGuideShow(SpecialCases):

    @staticmethod
    def handle(title: str):
        titles = title.split(': ')
        episode = MorseGuideShow.morse_episodes(titles[1])
        
        return 'Inspector Morse', str(episode[0]), episode[1], episode[2]

    @staticmethod
    def morse_episodes(guide_title: str):
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
            return '1', 3, 'Service Of All The Dead'
        if 'Infernal Spirit' in guide_title:
            return '4', 1, 'The Infernal Serpent'
        if 'In Australia' in guide_title:
            return '5', 4, 'Promised Land'
        if 'Death Is' in guide_title:
            return '8', 3, 'Death Is Now My Neighbour'
        else:
            season_number = ''
            episode_number = 0
            title = guide_title
            for season_idx, season in enumerate(morse_titles):
                for episode_idx, title in enumerate(season['Episodes']):
                    if 'The' in guide_title and 'The' not in title:
                        title = 'The ' + title
                    if guide_title in title:
                        season_number = str(season_idx+1)
                        episode_number = episode_idx+1
                        title = guide_title
            return season_number, episode_number, title

class RedElection(SpecialCases):

    def handle(title: str, season_number: str, episode_title: str):
        from log import logging_app
        logging_app(f'Logging Red Election Episode\nSeason Number: {season_number}\nEpisode title: {episode_title}')
        
        episode_details = episode_title[episode_title.find('Series'):]
        
        episode_detail_values = episode_details.split(' ')
        return 'Red Election', episode_detail_values[1], int(episode_detail_values[3]), ''

class SilentWitness(SpecialCases):
    
    @staticmethod
    def handle(season_number: str, episode_title: str):
        episode_data = SilentWitness.silent_witness(season_number, episode_title)
        return episode_data

    @staticmethod
    def silent_witness(season_number: str, episode_title: str):
        
        from log import logging_app
        try:
            check_episode = SilentWitness.check_silent_witness(episode_title)
            logging_app(f'Logging Silent Witness Episode\nSeason Number: {season_number}, Episode Title: {episode_title} Result: {check_episode}')
            return check_episode
        except ValueError:
            logging_app(f'Logging Silent Witness Episode\nSeason Number: {season_number}, Episode Title: {episode_title}')
            return None
        

    def check_silent_witness(episode_title: str):
        season_24_episodes = {
            'Redemption': ["Redemption Part 1", "Redemption Part 2"],
            'Bad Love': ["Bad Love Part 1", "Bad Love Part 2"],
            'Reputations': ["Reputations Part 1", "Reputations Part 2"],
            "Brother's Keeper": ["Brother's Keeper Part 1", "Brother's Keeper Part 2"],
            'Matters of Life and Death': ["Matters of Life and Death Part 1", "Matters of Life and Death Part 2"]
        }

        silent_witness_story = None
        index = -1

        for idx, key in enumerate(season_24_episodes.keys()):
            if key in episode_title:
                silent_witness_story = season_24_episodes[key]
                index = idx
                break

        if silent_witness_story:
            if 'Part' in episode_title:
                if 'One' in episode_title:
                    episode_title = episode_title.replace('One', '1')
                if 'Two' in episode_title:
                    episode_title = episode_title.replace('Two', '2')
                episode_part_num = [char for char in episode_title if char.isdigit()][0]
                episode_part_num = int(episode_part_num)
                episode_number = (index * 2) + episode_part_num
                return 'Silent Witness', '24', episode_number, episode_title
            else:
                raise ValueError('Unable to understand this Silent Witness episode')
        else:
            raise ValueError('This episode is not in Season 24')