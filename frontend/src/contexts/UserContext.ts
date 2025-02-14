import { createContext } from "react";

import { UserContextModel } from '../utils/types';

export const UserContext = createContext<UserContextModel>(null);