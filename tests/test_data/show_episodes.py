from datetime import datetime

from database.models.ShowEpisodeModel import ShowEpisode

show_episodes = [
    ShowEpisode(
        'Doctor Who',
        2,
        5,
        'Rise of the Cybermen',
        'First appearance of the Cybermen',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 12, hour=20, minute=30)],
        None,
    ),
    ShowEpisode(
        'Endeavour',
        5,
        6,
        'Icarus',
        'Final episode of Season 5',
        [],
        ["ABC1", "ABCHD"],
        [],
        None
    )
]

dw_show_episodes = [
    ShowEpisode(
        'Doctor Who',
        2,
        1,
        'New Earth',
        'Lady Cassandra Part 2',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 12, hour=20, minute=30)],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        2,
        2,
        'Tooth and Claw',
        'Werewolf',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 13, hour=20, minute=30)],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        2,
        3,
        'School Reunion',
        'Anthony Head',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 14, hour=20, minute=30)],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        2,
        4,
        'Girl in the Fireplace',
        'Madame de Pompadour',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 15, hour=20, minute=30)],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        4,
        1,
        'Partners In Crime',
        'The Doctor meets Donna again',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 15, hour=20, minute=30)],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        4,
        2,
        'Fires of Pompeii',
        "Pompeii and it's Volcano Day",
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 15, hour=20, minute=30)],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        4,
        3,
        'Planet of the Ood',
        '',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 15, hour=20, minute=30)],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        4,
        4,
        'The Sontaran Strategem',
        'Sontarans return',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 15, hour=20, minute=30)],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        4,
        5,
        'The Poison Sky',
        'Sontarans return',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 15, hour=20, minute=30)],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        4,
        6,
        "The Doctor's Daughter",
        'Jenny',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 15, hour=20, minute=30)],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        4,
        7,
        'The Unicorn and the Wasp',
        'Agatha Christie',
        [],
        ["ABC1", "ABCHD", "ABC2"],
        [datetime(2023, 9, 15, hour=20, minute=30)],
        None
    ),
]

channel_check_show_episodes = [
    ShowEpisode(
        "Vera",
        1,
        1,
        "Hidden Depths",
        "Bird Watchers",
        [],
        ["ABC1"],
        [],
        None
    ),
    ShowEpisode(
        "Red Election",
        1,
        1,
        "Afsnit 1",
        "",
        [],
        ["SBS"],
        [],
        None
    ),
    ShowEpisode(
        "NCIS",
        6,
        25,
        "Aliyah",
        "The team goes to Israel as Tony faces questions about Michael Rivkin's death",
        [],
        ["10"],
        [],
        None
    ),
    ShowEpisode(
        "Vera",
        2,
        2,
        "Sandancers",
        "Military episode",
        [],
        ["ABC1", "ABCHD"],
        [],
        None
    )
]

add_channel_show_episodes = [
    ShowEpisode(
        "Vera",
        2,
        1,
        "Sandancers",
        "Military episode",
        [],
        [],
        [],
        None
    ),
    ShowEpisode(
        "Red Election",
        1,
        1,
        "Afsnit 1",
        "",
        [],
        ["SBS"],
        [],
        None
    ),
    ShowEpisode(
        "NCIS",
        6,
        25,
        "Aliyah",
        "The team goes to Israel as Tony faces questions about Michael Rivkin's death",
        [],
        [],
        [],
        None
    ),
    ShowEpisode(
        'Doctor Who',
        4,
        4,
        'The Sontaran Strategem',
        'The Doctor meets Martha again',
        [],
        [],
        [datetime(2023, 9, 15, hour=20, minute=30)],
        None
    )
]

def find_episode(show_episodes: list[ShowEpisode], show: str, season_number: int, episode_number: int, episode_title: str):
    if season_number == -1 and episode_number == 0 and episode_title == '':
        return None

    if season_number != -1 and episode_number != 0:
        return next(
            (episode
                for episode in show_episodes
                if episode.show == show
                and episode.season_number == season_number
                and episode.episode_number == episode_number
            ),
            None
        )
    else:
        return next(
            (episode
                for episode in show_episodes
                if episode.show == show
                and episode.episode_title == episode_title
            ),
            None
        )
    
def find_episodes_by_season(show_episodes: list[ShowEpisode], show: str, season_number: int):

    return [episode for episode in show_episodes if episode.show == show and episode.season_number == season_number]

def add_episodes(episodes: list[ShowEpisode]):

    store: list[ShowEpisode] = []
    for episode in episodes:
        store.append(episode)
    return store

def add_episode(episode: ShowEpisode):

    store: list[ShowEpisode] = []
    store.append(episode)
    return store