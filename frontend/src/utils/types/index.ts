import type { AxiosResponse } from "axios";

export type { TVMazeSeason, TVMazeShow } from "./tvmaze";

interface Guide {
    fta: GuideShow[]
    bbc: GuideShow[]
};

interface GuideShow {
    title: string
    start_time: string
    end_time: string
    channel: string
    season_number: string
    episode_number: number
    episode_title: string
    repeat: boolean
    event: string
};

export interface ShowData {
    show_name: string
    show_details: ShowDetails
    show_episodes: ShowEpisode[]
    search_item: SearchItem
    reminder: Reminder
}

export interface ShowDetails {
    title: string
    description: string
    tvmaze_id: string
    genres: string[]
    image: string
}

export interface ShowEpisode {
    id: number
    show: string
    season_number: number
    episode_number: number
    episode_title: string
    summary: string
    alternative_titles: string[]
    channels: string[]
    air_dates: Date[]
}

interface Reminder {
    show: string
    alert: 'Before' | 'During' | 'After'
    warning_time: number
    occasions: 'All' | 'Latest'
};

interface SearchItem {
    show: string
    exact_title_match: boolean
    search_active: boolean
    conditions: {
        ignore_episodes: string[]
        ignore_seasons: number[]
        ignore_titles: string[]
        min_season_number: number
        max_season_number: number
    }
};

interface SearchItemPayload {
    show: string
    conditions: Partial<SearchItem['conditions']> & {
        exact_title_match: boolean
    }
}

interface SearchItemFormValues {
    searchTerm: string
    exactSearch: boolean
    seasons: number[]
    seasonChoice: "all" | "some"
    ignoreEpisodes: string[]
}

interface ReminderFormValues extends Partial<Reminder> {}

interface User {
    username: string
    show_subscriptions: UserSearchSubscription[]
    reminder_subscriptions: string[]
    role: 'Standard' | 'Admin'
};

interface CurrentUser extends User {
    token: string
};

interface UserSearchSubscription {
    id: number
    user_id: number
    search_id: number
    search_item: SearchItem
}

interface NewShowPayload {
    name: string,
    conditions: Partial<SearchItem['conditions']> & {
        exact_title_match: boolean
    }
}

interface LoginData {
    username: string
    password: string
}

interface NewUserDetails {
    username: string
    password: string
    show_subscriptions: string[]
    reminder_subscriptions: string[]
};

interface SubscriptionsPayload {
    subscribe?: {
        show_subscriptions: string[]
    }
    unsubscribe?: {
        subscriptionId: number
    }
};

export type SubscriptionsAction = "subscribe" | "unsubscribe";

interface AccountDetailsFormValues {
    username?: string
    password?: string
};

type FormMode = "add" | "edit";


// Contexts
interface ShowsContextModel {
    shows: ShowData[]
    setShows: React.Dispatch<React.SetStateAction<ShowData[]>>
};

interface UserContextModel {
    currentUser: CurrentUser
    setUser: React.Dispatch<React.SetStateAction<CurrentUser>>
};

export type {
    Guide,
    GuideShow,
    Reminder,
    SearchItem,
    User,
    UserContextModel,
    CurrentUser,
    SubscriptionsPayload,
    NewShowPayload,
    SearchItemPayload,
    SearchItemFormValues,
    ReminderFormValues,
    LoginData,
    NewUserDetails,
    AccountDetailsFormValues,
    FormMode,
    ShowsContextModel,
};