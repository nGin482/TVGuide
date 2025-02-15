import { createContext } from "react";

import { ShowsContextModel } from "../utils/types";

export const ShowsContext = createContext<ShowsContextModel>(null);