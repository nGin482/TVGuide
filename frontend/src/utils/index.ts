import { NewShowPayload, SearchItemFormValues, SearchItemPayload, ShowEpisode } from "./types";
import { TVMazeEpisode, TVMazeSeason } from "./types/tvmaze";

export const getSeasons = (showEpisodes: ShowEpisode[]) => {
    const seasonNumbers = showEpisodes.map(showEpisode => showEpisode.season_number);
    return [...new Set(seasonNumbers)];
};

export const createSearchItemPayload = (
    show: string,
    formValues: SearchItemFormValues,
    showSeasons: TVMazeSeason[]
) => {
    let seasons = formValues?.seasons;
    if (formValues.seasonChoice === "all") {
        seasons = showSeasons.map(season => season.number);
    }
    const conditions: SearchItemPayload['conditions'] = {
        exact_title_match: formValues?.exactSearch || false,
        min_season_number: Math.min(...seasons),
        max_season_number: Math.max(...seasons),
        ignore_episodes: formValues?.ignoreEpisodes || [],
    };
    if (formValues.seasonChoice === "some") {
        const ignored_seasons = showSeasons.filter(
            season => !formValues.seasons.includes(season.number)
        );
        conditions.ignore_seasons = ignored_seasons.map(season => season.number);
    }
    else {
        conditions.ignore_seasons = [];
    }

    return conditions;
};

export const validateTVMazeSeasons = (seasons: TVMazeSeason[]) => {
    return seasons.map((season, idx) => {
        if (season.number !== idx + 1) {
            season.number = idx + 1;
        }
        return season;
    });
};

export const validateTVMazeEpisodes = (episodes: TVMazeEpisode[]) => {
    const seasonNumbers = [...new Set(episodes.map(episode => episode.season))];
    
    const seasonMap = {};
    seasonNumbers.forEach((seasonNumber, idx) => {
        Object.assign(seasonMap, { [seasonNumber]: idx + 1 })
    });
    
    return episodes.map((episode, idx) => {
        if (episode.season !== seasonMap[episode.season]) {
            episode.season = seasonMap[episode.season];
        }
        return episode;
    });
};

export const sessionExpiryMessage = (action: string) => {
    return `You have been logged out. Please log in again to ${action}.`;
};
