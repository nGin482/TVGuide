from tvguide_types.tvmaze import TVMazeShow, TVMazeEpisode, TVMazeSeason

mock_tvmaze_show: TVMazeShow = {
    "name": "Doctor Who",
}

mock_tvmaze_seasons: list[TVMazeSeason] = [
    {
        "id": 1,
        "name": "Doctor Who",
        "number": 1,
    },
    {
        "id": 2,
        "name": "Doctor Who",
        "number": 2,
    },
    {
        "id": 3,
        "name": "Doctor Who",
        "number": 3,
    },
]

mock_tvmaze_episodes: list[TVMazeEpisode] = [
    {
        "id": 1,
        "season": 1,
        "number": 1,
        "name": "Rose",
        "summary": "Season 1 Episode 1",
        "_links": {
            "show": {
                "name": "Doctor Who",
            },
        },
    },
    {
        "id": 2,
        "season": 1,
        "number": 2,
        "name": "The End of the World",
        "summary": "Season 1 Episode 2",
        "_links": {
            "show": {
                "name": "Doctor Who",
            },
        },
    },
    {
        "id": 3,
        "season": 1,
        "number": 3,
        "name": "The Unquiet Dead",
        "summary": "Season 1 Episode 3",
        "_links": {
            "show": {
                "name": "Doctor Who",
            },
        },
    },
    {
        "id": 14,
        "season": 2,
        "number": 0,
        "name": "The Christmas Invasion",
        "summary": "Season 2 Christmas Special",
        "_links": {
            "show": {
                "name": "Doctor Who",
            },
        },
    },
    {
        "id": 15,
        "season": 2,
        "number": 1,
        "name": "New Earth",
        "summary": "Season 2 Episode 1",
        "_links": {
            "show": {
                "name": "Doctor Who",
            },
        },
    },
    {
            "id": 58,
            "season": 5,
            "number": 1,
            "name": "The Eleventh Hour",
            "summary": "Season 5 Episode 1",
            "_links": {
                "show": {
                    "name": "Doctor Who",
                },
            },
        },
]