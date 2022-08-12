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
    def format_title(title):
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
    def check_show_titles(show):
        if type(show) is str:
            if 'Maigret' in show:
                return 'Maigret'
            if 'Death in Paradise' in show:
                return 'Death In Paradise'
            if 'Revenge Of The Fallen' in show or 'Dark Of The Moon' in show \
                    or 'Age of Extinction' in show or 'The Last Knight' in show:
                return 'Transformers'
            elif show == 'Transformers':
                return 'Transformers'
            else:
                title = show
                if ':' in title:
                    idx = title.rfind(':')
                    title = title[:idx] + title[idx+1:]
                return title
        else:
            if 'Maigret' in show['title']:
                return 'Maigret'
            if 'Death in Paradise' in show['title']:
                return 'Death In Paradise'
            if 'Revenge Of The Fallen' in show['title'] or 'Dark Of The Moon' in show['title'] \
                    or 'Age of Extinction' in show['title'] or 'The Last Knight' in show['title']:
                return 'Transformers'
            elif show['title'] == 'Transformers':
                return 'Transformers'
            else:
                title = show['title']
                if ':' in title:
                    idx = title.rfind(':')
                    title = title[:idx] + title[idx+1:]
                return title

    @staticmethod
    def valid_reminder_fields():
        """
        Returns the fields only valid for a reminder document
        """
        return ['show', 'reminder time', 'interval']