
import { deleteRequest, postRequest, putRequest } from "./api-client";
import { SearchItem, SearchItemPayload } from "../utils/types";

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