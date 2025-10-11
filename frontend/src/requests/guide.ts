
import { getRequest } from "./api-client";
import { Guide } from "../utils/types";

export const getGuide = async (date?: string) => {
    return await getRequest<Guide>(date ? `/guide?date=${date}` : "/guide");
};
