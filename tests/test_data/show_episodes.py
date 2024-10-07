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
    )
]