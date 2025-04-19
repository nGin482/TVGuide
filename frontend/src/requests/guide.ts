
import { getRequest } from "./api-client";
import { Guide } from "../utils/types";

export const getGuide = async () => {
    return await getRequest<Guide>(`/guide`);
};
