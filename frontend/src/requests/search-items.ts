
import { deleteRequest, patchRequest, postRequest, putRequest } from "./api-client";
import { SearchItem, SearchItemPayload } from "../utils/types";

export const addSearchCriteria = async (searchCriteria: SearchItemPayload) => {
    const newSearchItem = await postRequest<SearchItemPayload, SearchItem>(
        `/search-item`,
        searchCriteria
    );
    return newSearchItem;
};

export const editSearchCriteria = async (searchCriteria: SearchItemPayload) => {
    const updatedSearchItem = await putRequest<SearchItemPayload, SearchItem>(
        `/search-item/${searchCriteria.show}`,
        searchCriteria,
    );
    return updatedSearchItem;
};

export const toggleStatus = async (searchId: number, status: boolean) => {
    const updatedSearchItem = await patchRequest<{ status: boolean }, SearchItem>(
        `/search-item/${searchId}/toggle-search`,
        { status },
    );
    
    return updatedSearchItem;
};

export const deleteSearchCriteria = async (show: string) => {
    await deleteRequest(`/search-item/${show}`);
};