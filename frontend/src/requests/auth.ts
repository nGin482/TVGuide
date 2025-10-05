
import { postRequest } from "./api-client";
import { CurrentUser, LoginData, NewUserDetails } from "../utils/types";

export const login = async (loginDetails: LoginData) => {
    const currentUser = await postRequest<LoginData, CurrentUser>(`/auth/login`, loginDetails);
    return currentUser;
};

export const registerNewUser = async (user: NewUserDetails) => {
    const newUser = await postRequest<NewUserDetails, CurrentUser>(`/auth/register`, user);
    return newUser;
};

export const refreshSession = async () => {
    const refreshedSession = await postRequest<null, CurrentUser>(
        `/auth/refresh`,
        null,
        "csrf_refresh_token"
    );
    return refreshedSession;
};

export const logoutSession = async () => {
    await postRequest(`/auth/logout`, null);
};