import { useContext, useEffect, useState } from "react";
import { NavLink, useLocation, useParams } from "react-router-dom";
import { Alert, Button } from "antd";
import { Helmet } from "react-helmet";

import { ShowDetails } from "../components/ShowDetails";
import { ShowEpisodes } from "../components/ShowEpisode";
import { SearchItem } from "../components/SearchItem";
import { Reminder } from "../components/Reminders";
import { ShowsContext } from "../contexts";
import { ShowData } from "../utils/types";
import "./styles/ShowPage.css";

interface ShowParam {
    show: string
};

type DataView = "episodes" | "search" | "reminder";

const ShowPage = () => {
    const { show } = useParams<ShowParam>();
    const [showData, setshowData] = useState<ShowData>(null);
    const [dataView, setDataView] = useState<DataView>(null);

    const { shows } = useContext(ShowsContext);
    const location = useLocation();
    
    useEffect(() => {
        const view = findViewFromLocation();
        setDataView(view);
    }, []);

    useEffect(() => {
        const showDetail = shows.find(showData => showData.show_name === show);
        setshowData(showDetail);
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

    return (
        showData ? (
            <div id={showData.show_name} className="show-content">
                <Helmet>
                    <title>{showData.show_name} Details | TVGuide</title>
                </Helmet>
                <h1>{showData.show_name}</h1>
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