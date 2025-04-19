
import { getRequest, putRequest } from "./api-client";
import {
    Guide,
    ShowEpisode,
} from "../utils/types";

const getGuide = async () => {
    return await getRequest<Guide>(`/guide`);
};




const updateShowEpisode = async (episode: ShowEpisode, token: string) => {
    return await putRequest<ShowEpisode, ShowEpisode>(
        `/show-episode/${episode.id}`,
        episode,
        { Authorization: `Bearer ${token}` }
    );
};


export * from "./auth";
export * from "./reminders";
export * from "./shows";
export * from "./search-items";
export * from "./search-subscriptions";
export * from "./user";

export {
    getGuide,
    updateShowEpisode,
};

export * from './tvmaze';