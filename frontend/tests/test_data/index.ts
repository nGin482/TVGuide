import {
    CurrentUser,
    Guide,
    NewUserDetails,
    ShowData,
    Reminder,
    SearchItem,
    User,
    NewShowPayload,
} from "../../src/utils/types";
import { TVMazeShow } from "../../src/utils/types/tvmaze";

export const guide: Guide = {
    fta: [
        {
            title: 'Maigret',
            start_time: '20:30',
            end_time: "22:00",
            channel: 'ABC1',
            season_number: '2',
            episode_number: 1,
            episode_title: "Maigret's Dead Man",
            repeat: true,
            event: 'Maigret has aired today'
        },
        {
            title: 'Vera',
            start_time: '13:00',
            end_time: "14:30",
            channel: 'ABC1',
            season_number: '7',
            episode_number: 3,
            episode_title: 'Broken Promise',
            repeat: true,
            event: 'Vera has aired today'
        }
    ],
    bbc: [
        {
            title: 'Death in Paradise',
            start_time: '19:30',
            end_time: "20:30",
            channel: 'BBC First',
            season_number: '1',
            episode_number: 1,
            episode_title: 'Arriving in Paradise',
            repeat: true,
            event: 'Death in Paradise has aired today'
        },
        {
            title: 'Lewis',
            start_time: '15:00',
            end_time: "16:30",
            channel: 'BBC UKTV',
            season_number: '2',
            episode_number: 3,
            episode_title: 'Life Born of Fire',
            repeat: true,
            event: 'Lewis has aired today'
        }
    ]
};

export const searchList: SearchItem[] = [
    {
        show: "Doctor Who",
        conditions: null,
        search_active: true,
        exact_title_match: true,
    },
    {
        show: "Endeavour",
        conditions: null,
        search_active: true,
        exact_title_match: true,
    }
];

export const addSearchItem: SearchItem = {
    show: "Maigret",
    conditions: null,
    search_active: true,
    exact_title_match: true,
};

export const shows: ShowData[] = [
    {
        show_name: "Doctor Who",
        show_episodes: [
            {
                id: 1,
                show: "Doctor Who",
                season_number: 1,
                episode_number: 1,
                episode_title: "Rose",
                alternative_titles: [],
                summary: "",
                channels: [
                    "ABC1",
                    "ABCHD"
                ],
                air_dates: [
                    new Date("01/01/2024")
                ],
            },
            {
                id: 2,
                show: "Doctor Who",
                season_number: 1,
                episode_number: 2,
                episode_title: "The End of the World",
                alternative_titles: [],
                summary: "",
                channels: [
                    "ABC1",
                    "ABCHD"
                ],
                air_dates: [
                    new Date("08/01/2024")
                ]
            },
            {
                id: 3,
                show: "Doctor Who",
                season_number: 2,
                episode_number: 0,
                episode_title: 'A Christmas Invasion',
                alternative_titles: [],
                summary: '',
                channels: [
                    'ABC1',
                    'ABCHD',
                    'ABC2'
                ],
                air_dates: [
                    new Date('11/4/2024'),
                    new Date('12/4/2024'),
                ]
            },
        ],
        show_details: {
            title: "Doctor Who",
            description: "",
            genres: [],
            image: "",
            tvmaze_id: "1234"
        },
        search_item: {
            show: "Doctor Who",
            search_active: true,
            exact_title_match: true,
            conditions: null,
        },
        reminder: null
    },
    {
        show_name: "Maigret",
        show_episodes: [
            {
                id: 3,
                show: "Maigret",
                season_number: 1,
                episode_number: 1,
                episode_title: "Maigret Sets A Trap",
                alternative_titles: [],
                summary: "",
                channels: [
                    "ABC1",
                    "ABCHD"
                ],
                air_dates: [
                    new Date("01/01/2024")
                ]
            },
            {
                id: 4,
                show: "Maigret",
                season_number: 1,
                episode_number: 2,
                episode_title: "Maigret's Dead Man",
                alternative_titles: [],
                summary: "",
                channels: [
                    "ABC1", "ABCHD"
                ],
                air_dates: [
                    new Date("08/01/2024")
                ]
            },
        ],
        show_details: {
            title: "Maigret",
            description: "",
            genres: [],
            image: "",
            tvmaze_id: "1234"
        },
        search_item: {
            show: "Maigret",
            exact_title_match: true,
            search_active: true,
            conditions: null,
        },
        reminder: null
    }
];

export const reminders: Reminder[] = [
    {
        show: "Doctor Who",
        warning_time: 5,
        alert: "Before",
        occasions: "All"
    },
    {
        show: "Maigret",
        warning_time: 3,
        alert: "Before",
        occasions: "All"
    }
];

export const user: User = {
    username: "Test",
    show_subscriptions: [
        {
            id: 1,
            search_id: 1,
            user_id: 2,
            search_item: shows[1].search_item
        },
        {
            id: 2,
            search_id: 2,
            user_id: 2,
            search_item: shows[0].search_item
        },
    ],
    reminder_subscriptions: [
        "Maigret",
        "Endeavour"
    ],
    role: "Standard"
};

export const currentUser: CurrentUser = { ...user, token: "test-token" };

export const newUser: NewUserDetails = {
    username: "Random",
    password: "test-password",
    show_subscriptions: [],
    reminder_subscriptions: []
};

export const newUserRes: CurrentUser = {
    username: "Random",
    show_subscriptions: [],
    reminder_subscriptions: [],
    role: "Standard",
    token: "test-token"
};

export const updateSubscriptionsRes: CurrentUser = {
    username: "Random",
    show_subscriptions: [
        ...user.show_subscriptions, 
        {
            id: 3,
            search_id: 3,
            user_id: 2,
            search_item: {
                show: "Vera",
                search_active: true,
                exact_title_match: true,
                conditions: null
            }
        },
    ],
    reminder_subscriptions: [],
    role: "Standard",
    token: "test-token"
};

export const loginRes: CurrentUser = {
    username: "Test",
    show_subscriptions: [],
    reminder_subscriptions: [],
    role: "Standard",
    token: "test-token"
};

export const newShowPayload: NewShowPayload = {
    name: "Maigret",
    conditions: {
        exact_title_match: true,
        min_season_number: 1,
        max_season_number: 2,
        ignore_episodes: [],
        ignore_seasons: [],
        ignore_titles: [],
    }
}

export const tvMazeResult: TVMazeShow = {
    score: 0.9,
    show: {
        id: 1234,
        name: "Maigret",
        image: {
            medium: "https://image_url.com/maigret",
            original: "https://image_url.com/maigret"
        },
        summary: "Maigret Summary",
        status: "Ended",
        premiered: "01/01/2016"
    }
};