

class SearchItem:

    def __init__(self, show: str, image: str, conditions, search_active: bool):
        self.show = show
        self.image = image
        self.conditions = conditions
        self.search_active = search_active

    @classmethod
    def from_database(cls, search_item: dict[str]):
        return cls(search_item['show'], search_item['image'], search_item['conditions'], search_item['search_active'])


    def to_dict(self):
        return {
            'show': self.show,
            'image': self.image,
            'conditions': self.conditions,
            'search_active': self.search_active
        }