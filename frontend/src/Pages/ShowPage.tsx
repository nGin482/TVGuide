import { useContext, useEffect, useState } from "react";
import { NavLink, useLocation, useParams } from "react-router-dom";
import { Alert, App, Button } from "antd";
import { Helmet } from "react-helmet";

import { ShowDetails } from "../components/ShowDetails";
import { ShowEpisodes } from "../components/ShowEpisode";
import { SearchItem } from "../components/SearchItem";
import { Reminder } from "../components/Reminders";
import { ShowsContext, UserContext } from "../contexts";
import { toggleStatus } from "../requests";
import { ShowData } from "../utils/types";
import "./styles/ShowPage.css";
import { handleErrorResponse } from "../utils";

interface ShowParam {
    show: string
};

type DataView = "episodes" | "search" | "reminder";

const ShowPage = () => {
    const { show } = useParams<ShowParam>();
    const [showData, setShowData] = useState<ShowData>(null);
    const [dataView, setDataView] = useState<DataView>(null);

    const { shows, setShows } = useContext(ShowsContext);
    const { currentUser } = useContext(UserContext);
    const { notification } = App.useApp();
    const location = useLocation();
    
    useEffect(() => {
        const view = findViewFromLocation();
        setDataView(view);
    }, []);

    useEffect(() => {
        const showDetail = shows.find(showData => showData.show_name === show);
        setShowData(showDetail);
    }, [show, shows]);

    const findViewFromLocation = () => {
        const paths = location.pathname.split("/");
        return paths[paths.length - 1] as DataView;
    };

    const dataButtonClass = (view: DataView) => {
        let className = "switch-view-button";
        if (location.pathname.includes(view)) {
            className += " active";
        }
        return className;
    };

    const toggleSearch = async () => {
        const newStatus = showData.search_item.search_active ? false : true;
        try {
            const response = await toggleStatus(showData.search_item.id, newStatus, currentUser.token);
            setShowData(current => ({ ...current, search_item: response }));
            setShows(current => {
                const showsList = [...current];
                return showsList.map(showData => {
                    if (showData.show_name === show) {
                        return { ...showData, search_item: response };
                    }
                    return showData;
                });
            });
            notification.success({
                message: "Success!",
                description: `The search status for ${show} has been updated.`,
            });
        }
        catch(error) {
            let message: string = error?.message;
            if (error?.response) {
                message = handleErrorResponse(error, "update the search status for this show");
            }
            notification.error({
                message: `There was a problem updating ${show}!`,
                description: message,
            });
        }
    };

    return (
        showData ? (
            <div id={showData.show_name} className="show-content">
                <Helmet>
                    <title>{showData.show_name} Details | TVGuide</title>
                </Helmet>
                <h1>{showData.show_name}</h1>
                {showData.search_item && (
                    <Button onClick={toggleSearch}>
                        {showData.search_item.search_active ? "Deactivate Search" : "Activate Search"}
                    </Button>
                )}
                <ShowDetails showDetails={showData.show_details} />
                <div className="show-data-switch">
                    <NavLink to={`/shows/${showData.show_name}/episodes`}>
                        <Button
                            size="large"
                            className={dataButtonClass("episodes")}
                            onClick={() => setDataView("episodes")}
                        >
                            Episodes
                        </Button>
                    </NavLink>
                    <NavLink to={`/shows/${showData.show_name}/search`}>
                        <Button
                            size="large"
                            className={dataButtonClass("search")}
                            onClick={() => setDataView("search")}
                        >
                            Search Criteria
                        </Button>
                    </NavLink>
                    <NavLink to={`/shows/${showData.show_name}/reminder`}>
                        <Button
                            size="large"
                            className={dataButtonClass("reminder")}
                            onClick={() => setDataView("reminder")}
                        >
                            Reminder
                        </Button>
                    </NavLink>
                </div>

                {dataView === "episodes" && (
                    <ShowEpisodes
                        episodes={showData.show_episodes}
                        showName={showData.show_name}
                    />
                )}
                {dataView === "search" && (
                    <SearchItem searchItem={showData.search_item} show={showData.show_name} />
                )}
                {dataView === "reminder" && (
                    <Reminder reminder={showData.reminder} show={showData.show_name} />
                )}
            </div>
        ) : (
            <>
                <h1>{show}</h1>
                <Alert type="error" message="A problem occurred retrieving the data for this show" />
            </>
        )
    )
};

export { ShowPage };