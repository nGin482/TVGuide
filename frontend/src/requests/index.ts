
import { deleteRequest, getRequest, postRequest, putRequest } from "./api-client";
import {
    Guide,
    ShowEpisode,
    User,
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

const getUserSubscriptions = async (user: string) => {
    const data = await getRequest(`/users/${user}/subscriptions`);
};
const addSubscriptions = async (
    username: string,
    subscriptions: string[],
    token: string
) => {
    const updatedUser = await postRequest<string[], User>(
        `/users/${username}/subscriptions`,
        subscriptions,
        { Authorization: `Bearer ${token}` }
    );

    return updatedUser;
};

const unsubscribeFromSearch = async (subscriptionId: number, token: string) => {
    await deleteRequest(`/users/subscriptions/${subscriptionId}`, { Authorization: `Bearer ${token}` });
};

export * from "./auth";
export * from "./reminders";
export * from "./shows";
export * from "./search-items";
export * from "./user";

export {
    getGuide,
    updateShowEpisode,
    getUserSubscriptions,
    addSubscriptions,
    unsubscribeFromSearch,
};

export * from './tvmaze';