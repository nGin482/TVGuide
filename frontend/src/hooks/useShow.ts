import { useContext } from "react";

import { ShowsContext } from "../contexts";
import { Reminder, SearchItem, ShowData, ShowDetails, ShowEpisode } from "../utils/types";

const useShow = () => {

    const { shows, setShows } = useContext(ShowsContext);

    const addShowToContext = (newShow: ShowData) => {
        setShows(current => [...current, newShow]);
    };

    const updateShowContext = (
        showName: string,
        property: keyof ShowData,
        newData: SearchItem | ShowEpisode[] | Reminder | string | ShowDetails
    ) => {
        const updatedShows = shows.map(show => {
            if (show.show_name === showName) {
                const updatedShow = { ...show, [property]: newData };
                return updatedShow;
            }
            return show;
        });
        setShows(updatedShows);
    };

    const updateEpisodeContext = (showName: string, episodeId: number, updatedEpisode: ShowEpisode) => {
        const show = shows.find(show => show.show_name === showName);
        const updatedEpisodes = show.show_episodes.map(episode => {
            if (episode.id === episodeId) {
                return updatedEpisode;
            }
            return episode;
        });
        show.show_episodes = updatedEpisodes;
        const updatedShows = shows.map(currentShow => {
            if (currentShow.show_name === showName) {
                return show;
            }
            return currentShow;
        });
        setShows(updatedShows);
    };

    return {
        addShowToContext,
        updateShowContext,
        updateEpisodeContext,
    };
};

export { useShow };