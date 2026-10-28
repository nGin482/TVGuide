import SearchItem from "../../database/models/SearchItem";
import { SearchItem as TSearchItem } from "../../types";

const testSearchItemData: TSearchItem[] = [
  {
    id: 1,
    show: "Merlin",
    exactTitleMatch: true,
    searchActive: true,
    minSeasonNumber: 1,
    maxSeasonNumber: 5,
    ignoreTitles: [],
    ignoreSeasons: [],
    ignoreEpisodes: [],
    showId: 1,
  },
  {
    id: 2,
    show: "Endeavour",
    exactTitleMatch: true,
    searchActive: true,
    minSeasonNumber: 1,
    maxSeasonNumber: 9,
    ignoreTitles: [],
    ignoreSeasons: [],
    ignoreEpisodes: [],
    showId: 2,
  },
];


export const testSearchItems = (searchItems = testSearchItemData) => {
  return searchItems.map(searchItem => SearchItem.build({
    show: searchItem.show,
    exactTitleMatch: searchItem.exactTitleMatch,
    searchActive: searchItem.searchActive,
    minSeasonNumber: searchItem.minSeasonNumber,
    maxSeasonNumber: searchItem.maxSeasonNumber,
    ignoreTitles: searchItem.ignoreTitles,
    ignoreSeasons: searchItem.ignoreSeasons,
    ignoreEpisodes: searchItem.ignoreEpisodes,
    showId: searchItem.showId,
  }));
};
