import axios, { AxiosRequestConfig } from "axios";

const baseURL = process.env.VITE_BASE_URL;

const headers = (otherHeaders?: AxiosRequestConfig['headers']) => {
    const headersObj = {
        'Content-Type': 'application/json',
        Accept: 'application/json',
    };

    if (otherHeaders) {
        Object.assign(headersObj, otherHeaders);
    }

    return headersObj;
};

const getCookie = (cookieName: string) => {
    const cookies = document.cookie.split(";");

    const cookieIdentifier = `${cookieName}=`
    const cookieData = cookies.find(cookie => cookie.includes(cookieIdentifier));
    if (!cookieData) {
        return;
    }
    const cookieValue = cookieData.replace(cookieIdentifier, "");

    return cookieValue;
};

export const getRequest = async <DataType>(
    endpoint: string,
    otherHeaders?: AxiosRequestConfig['headers']
) => {
    const response = await axios.get<DataType>(
        baseURL + endpoint,
        { headers: headers(otherHeaders) }
    );

    return response.data;
};

export const postRequest = async <RequestType, ResponseType>(
    endpoint: string,
    data: RequestType,
    csrfToken: "csrf_access_token" | "csrf_refresh_token" = "csrf_access_token",
    otherHeaders?: AxiosRequestConfig['headers']
) => {
    const response = await axios.post<ResponseType>(
        baseURL + endpoint,
        data,
        {
            headers: {
                ...headers(otherHeaders),
                "X-CSRF-Token": getCookie(csrfToken),
            },
            withCredentials: true,
        }
    );

    return response.data;
};

export const putRequest = async <RequestType, ResponseType>(
    endpoint: string,
    data: RequestType,
    otherHeaders?: AxiosRequestConfig['headers']
) => {
    const response = await axios.put<ResponseType>(
        baseURL + endpoint,
        data,
        {
            headers: headers(otherHeaders)
        }
    );

    return response.data;
};

export const patchRequest = async <RequestType, ResponseType>(
    endpoint: string,
    data: RequestType,
    otherHeaders?: AxiosRequestConfig['headers']
) => {
    const response = await axios.patch<ResponseType>(
        baseURL + endpoint,
        data,
        {
            headers: headers(otherHeaders)
        }
    );

    return response.data;
};

export const deleteRequest = async (
    endpoint: string,
    otherHeaders?: AxiosRequestConfig['headers']
) => {
    await axios.delete<void>(baseURL + endpoint, { headers: headers(otherHeaders) });
};