

import { deleteRequest, getRequest, postRequest } from "./api-client";
import { NewShowPayload, ShowData } from "../utils/types";

export const getShows = () => {
    return getRequest<ShowData[]>("/shows");
}
export const addNewShow = async (newShowData: NewShowPayload, token: string): Promise<ShowData> => {
    const newShowDetails = await postRequest<NewShowPayload, ShowData>(
        "/shows",
        newShowData,
        { Authorization: `Bearer ${token}` }
    );
    return newShowDetails;
};
export const removeShowFromList = async (showToRemove: string, token: string) => {
    await deleteRequest(
        `/shows/${showToRemove}`,
        { Authorization: `Bearer ${token}` }
    );
};