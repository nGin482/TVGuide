import axios from "axios";

import { validateTVMazeEpisodes, validateTVMazeSeasons } from "../utils";
import { TVMazeEpisode, TVMazeSeason, TVMazeShow } from "../utils/types/tvmaze";

const baseURL = 'https://api.tvmaze.com';

export const searchNewShow = async (searchTerm: string) => {
    const response = await axios.get<TVMazeShow[]>(`${baseURL}/search/shows?q=${searchTerm}`);
    if (response.status === 200) {
        return response.data;
    }
};
export const getShowSeasons = async (tvMazeId: number | string) => {
    const response = await axios.get<TVMazeSeason[]>(`${baseURL}/shows/${tvMazeId}/seasons`);
    if (response.status === 200) {
        const seasons = validateTVMazeSeasons(response.data);
        return seasons;
    }
};

export const getEpisodes = async (tvmazeId: number | string) => {
    const response = await axios.get<TVMazeEpisode[]>(
        `${baseURL}/shows/${tvmazeId}/episodes?specials=1`
    );

    if (response.status === 200) {
        const episodes = validateTVMazeEpisodes(response.data);
        return episodes;
    }
};
