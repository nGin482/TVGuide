import axios, { AxiosRequestConfig } from "axios";

const baseURL = process.env.VITE_BASE_URL;

const headers = (otherHeaders?: AxiosRequestConfig['headers']) => {
    const headersObj = {
        'Content-Type': 'application/json',
        Accept: 'application/json'
    };

    if (otherHeaders) {
        Object.assign(headersObj, otherHeaders);
    }

    return headersObj;
};

export const getRequest = async <DataType>(endpoint: string, otherHeaders?: AxiosRequestConfig['headers']) => {
    const response = await axios.get<DataType>(baseURL + endpoint, { headers: headers(otherHeaders) });

    return response.data;
};

export const postRequest = async <RequestType, ResponseType>(
    endpoint: string,
    data: RequestType,
    otherHeaders?: AxiosRequestConfig['headers']
) => {
    const response = await axios.post<ResponseType>(
        baseURL + endpoint,
        data,
        {
            headers: headers(otherHeaders)
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

export const deleteRequest = async (
    endpoint: string,
    otherHeaders?: AxiosRequestConfig['headers']
) => {
    await axios.delete<void>(baseURL + endpoint, { headers: headers(otherHeaders) });
};