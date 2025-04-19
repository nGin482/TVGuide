
import { putRequest } from "./api-client";
import {
    ShowEpisode,
} from "../utils/types";






const updateShowEpisode = async (episode: ShowEpisode, token: string) => {
    return await putRequest<ShowEpisode, ShowEpisode>(
        `/show-episode/${episode.id}`,
        episode,
        { Authorization: `Bearer ${token}` }
    );
};


export * from "./auth";
export * from "./guide";
export * from "./reminders";
export * from "./shows";
export * from "./search-items";
export * from "./search-subscriptions";
export * from "./user";

export {
    updateShowEpisode,
};

export * from './tvmaze';