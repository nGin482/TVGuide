
import { getRequest, putRequest } from "./api-client";
import { AccountDetailsFormValues, User } from "../utils/types";

export const getUser = async (username: string) => {
    return await getRequest<User>(`/user/${username}`);
};

export const changePassword = async (
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
