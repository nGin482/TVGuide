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
            return 'Transformers', check_transformers[0], check_transformers[1], check_transformers[2]
        if 'Predacons Rising' in title:
            return 'Transformers: Prime', 4, 1, 'Beast Hunters: Predacons Rising'
        return check_transformers

    @staticmethod
    def transformers_shows(transformers: str):
        if 'Fallen' in transformers:
            return 1, 2, 'Revenge of the Fallen'
        elif 'Dark' in transformers:
            return 1, 3, 'Dark of the Moon'
        elif 'Extinction' in transformers:
            return 1, 4, 'Age of Extinction'
        elif 'Knight' in transformers:
            return 1, 5, 'The Last Knight'
        elif 'Bumblebee' in transformers and 'Cyberverse' not in transformers:
            return 1, 6, 'Bumblebee'
        elif transformers == 'Transformers':
            return 1, 1, 'Transformers'
        elif 'Cyberverse' in transformers:
            return 'Transformers: Cyberverse'
        else:
            return transformers
