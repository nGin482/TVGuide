from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow


class Validation:

    @staticmethod
    def format_time(time: str):
        """
        Format a show's start time to 24 hour time
        :param time: show start_time to format that will be passed as string
        :return: the formatted time string

        May become deprecated
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
    def format_title(title: str):
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
        elif 'Revenge Of The Fallen' in show or 'Dark Of The Moon' in show \
                or 'Age of Extinction' in show or 'The Last Knight' in show:
            return 'Transformers'
        elif show == 'Transformers':
            return 'Transformers'
        title = show
        if ':' in title:
            idx = title.rfind(':')
            title = title[:idx] + title[idx+1:]
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
    def valid_reminder_fields():
        """
        Returns the fields only valid for a reminder document
        """
        return ['show', 'reminder time', 'interval']