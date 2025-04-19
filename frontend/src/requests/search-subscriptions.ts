
import { deleteRequest, getRequest, postRequest } from "./api-client";
import { User } from "../utils/types";

export const getUserSubscriptions = async (user: string) => {
    const data = await getRequest(`/users/${user}/subscriptions`);
};

export const addSubscriptions = async (
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

export const unsubscribeFromSearch = async (subscriptionId: number, token: string) => {
    await deleteRequest(
        `/users/subscriptions/${subscriptionId}`,
        { Authorization: `Bearer ${token}` }
    );
};
