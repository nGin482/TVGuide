import { useState, useEffect, JSX } from "react";
import { App } from "antd";
import Cookies from "universal-cookie";

import { ShowsContext, UserContext } from "../contexts";
import { CurrentUser, ShowData } from "../utils/types";
import { getShows } from "../requests";

const ContextWrapper = ({ children }: { children: JSX.Element | JSX.Element[] }) => {
    const cookies = new Cookies('user', { path: '/' });
    const userCookie = cookies.get('user')
    
    const [currentUser, setUser] = useState<CurrentUser>(userCookie);
    const [shows, setShows] = useState<ShowData[]>([]);

    const { notification } = App.useApp();

    useEffect(() => {
        fetchShows();
    }, []);

    const fetchShows = async () => {
        try {
            const shows = await getShows();
            setShows(shows);
        }
        catch(error) {
            let message = error.message;
            if (error?.response) {
                message = error?.response?.data?.message;
            }
            notification.error({
                message: "An error occurred attempting to fetch the shows",
                description: message
            });
        }
    };

    return (
        <ShowsContext.Provider value={{ shows, setShows }}>
            <UserContext.Provider value={{ currentUser, setUser }}>
                {children}
            </UserContext.Provider>
        </ShowsContext.Provider>
    );
};

export default ContextWrapper;