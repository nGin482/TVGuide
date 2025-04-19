
import { deleteRequest, getRequest, postRequest, putRequest } from "./api-client";
import {
    AccountDetailsFormValues,
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

const getUser = async (username: string) => {
    return await getRequest<User>(`/user/${username}`);
};

const changePassword = async (
    username: string,
    details: AccountDetailsFormValues,
    token: string
) => {
    const response = await putRequest<{ password: string }, User>(
        `/user/${username}/change_password`,
        { password: details.password },
        { Authorization: `Bearer ${token}` }
    );

    return response;
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

export {
    getGuide,
    updateShowEpisode,
    getUser,
    changePassword,
    getUserSubscriptions,
    addSubscriptions,
    unsubscribeFromSearch,
};

export * from './tvmaze';