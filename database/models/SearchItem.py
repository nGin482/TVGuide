

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
        print(bool(self.conditions))
        if not self.conditions:
            return True
        
        if 'min_season' in self.conditions and 'max_season' in self.conditions:
            if self.conditions['min_season'] <= guide_show['season_number'] <= self.conditions['max_season']:
                print(f"{self.conditions['min_season']} <= {guide_show['season_number']} <= {self.conditions['max_season']}")
                return True
            return False
        if 'min_season' in self.conditions and guide_show['season_number'] >= self.conditions['min_season']:
            print(f"{guide_show['season_number']} >= {self.conditions['min_season']}")
            return True
        if 'max_season' in self.conditions and guide_show['season_number'] <= self.conditions['max_season']:
            print(f"{guide_show['season_number']} <= {self.conditions['max_season']}")
            return True
        return False


    def to_dict(self):
        return {
            'show': self.show,
            'image': self.image,
            'conditions': self.conditions,
            'search_active': self.search_active
        }