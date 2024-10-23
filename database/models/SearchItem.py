

class SearchItem:

    def __init__(self, show: str, image: str, conditions, search_active: bool):
        self.show = show
        self.image = image
        self.conditions = conditions
        self.search_active = search_active

    @classmethod
    def from_database(cls, search_item: dict[str]):
        return cls(search_item['show'], search_item['image'], search_item['conditions'], search_item['search_active'])

    def check_search_conditions(self, guide_show: dict):
        if not self.search_active:
            return False

        if not self.conditions:
            return True

        if 'min_season' not in self.conditions and 'max_season' not in self.conditions:
            season_check = True
        elif guide_show['season_number'] != 'Unknown':
            if 'min_season' in self.conditions and 'max_season' in self.conditions:
                season_check = int(self.conditions['min_season']) <= int(guide_show['season_number']) <= int(self.conditions['max_season'])
            elif 'min_season' in self.conditions:
                season_check = int(guide_show['season_number']) >= int(self.conditions['min_season'])
            elif 'max_season' in self.conditions:
                season_check = int(guide_show['season_number']) <= int(self.conditions['max_season'])
        elif guide_show['season_number'] == 'Unknown':
            season_check = True
        else:
            season_check = False

        if 'only_season' in self.conditions:
            only_season_check = int(self.conditions['only_season']) == int(guide_show['season_number'])
        else:
            only_season_check = True

        if 'exact_search' in self.conditions:
            if self.conditions['exact_search']:
                show_title_check = self.show.lower() == str(guide_show['title']).lower()
            else:
                show_title_check = self.show.lower() in str(guide_show['title']).lower()
        else:
            show_title_check = True

        if 'exclude_titles' in self.conditions:
            show_title_exclusion_check = guide_show['title'] not in self.conditions['exclude_titles']
        else:
            show_title_exclusion_check = True

        return show_title_check and show_title_exclusion_check and season_check and only_season_check


    def to_dict(self):
        return {
            'show': self.show,
            'image': self.image,
            'conditions': self.conditions,
            'search_active': self.search_active
        }