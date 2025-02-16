export interface TVMazeShow {
    score: number
    show: {
        id: number
        name: string
        image: {
            medium: string
            original: string
        }
        status: string
        premiered: string
        summary: string
    }
};

export interface TVMazeSeason {
    id: number
    url: string
    number: number
    episodeOrder: number
};

export interface TVMazeEpisode {
    id: number
    url: string
    name: string
    season: number
    number: number
    type: string
    airdate: string
    airtime: string
    airstamp: string
    runtime: number
    rating: {
        average: number
    },
    image: {
        medium: string
        original: string
    },
    summary: string
    _links: {
        self: {
            href: string
        },
        show: {
            href: string
            name: string
        }
    }
}