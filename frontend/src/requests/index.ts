
import { deleteRequest, getRequest, postRequest, putRequest } from "./api-client";
import {
    AccountDetailsFormValues,
    CurrentUser,
    Guide,
    LoginData,
    NewShowPayload,
    NewUserDetails,
    Reminder,
    ReminderFormValues,
    SearchItemPayload,
    SearchItem,
    ShowData,
    ShowEpisode,
    User,
} from "../utils/types";

const getGuide = async () => {
    return await getRequest<Guide>(`/guide`);
};

export const getShows = () => {
    return getRequest<ShowData[]>("/shows");
}
const addNewShow = async (newShowData: NewShowPayload, token: string): Promise<ShowData> => {
    const newShowDetails = await postRequest<NewShowPayload, ShowData>(
        "/shows",
        newShowData,
        { Authorization: `Bearer ${token}` }
    );
    return newShowDetails;
};
const removeShowFromList = async (showToRemove: string, token: string) => {
    await deleteRequest(
        `/shows/${showToRemove}`,
        { Authorization: `Bearer ${token}` }
    );
};

export const addSearchCriteria = async (searchCriteria: SearchItemPayload, token: string) => {
    const newSearchItem = await postRequest<SearchItemPayload, SearchItem>(
        `/search-item`,
        searchCriteria,
        { Authorization: `Bearer ${token}` }
    );
    return newSearchItem;
};

export const editSearchCriteria = async (searchCriteria: SearchItemPayload, token: string) => {
    const updatedSearchItem = await putRequest<SearchItemPayload, SearchItem>(
        `/search-item/${searchCriteria.show}`,
        searchCriteria,
        { Authorization: `Bearer ${token}` }
    );
    return updatedSearchItem;
};

export const deleteSearchCriteria = async (show: string, token: string) => {
    await deleteRequest(`/search-item/${show}`, { Authorization: `Bearer ${token}` });
};

const getReminders = async () => {
    const reminders = await getRequest<Reminder[]>("/reminders");
    return reminders;
};
const addReminder = async (reminder: ReminderFormValues, token: string) => {
    return await postRequest<ReminderFormValues, Reminder>(
        `/reminders`,
        reminder,
        { Authorization: `Bearer ${token}` }
    );
};
const editReminder = async (reminderDetails: ReminderFormValues, token: string) => {
    return await putRequest<ReminderFormValues, Reminder>(
        `/reminder/${reminderDetails.show}`,
        reminderDetails,
        { Authorization: `Bearer ${token}` }
    );
}
const deleteReminder = async (show: string, token: string) => {
    return await deleteRequest(`/reminder/${show}`, { Authorization: `Bearer ${token}` });
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
const registerNewUser = async (user: NewUserDetails) => {
    const newUser = await postRequest<NewUserDetails, CurrentUser>(`/auth/register`, user);
    return newUser;
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
    console.log(data)
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

const login = async (loginDetails: LoginData) => {
    const currentUser = await postRequest<LoginData, CurrentUser>(`/auth/login`, loginDetails);
    return currentUser;
};

export {
    getGuide,
    addNewShow,
    removeShowFromList,
    getReminders,
    addReminder,
    editReminder,
    deleteReminder,
    updateShowEpisode,
    getUser,
    registerNewUser,
    changePassword,
    getUserSubscriptions,
    addSubscriptions,
    unsubscribeFromSearch,
    login
};

export * from './tvmaze';