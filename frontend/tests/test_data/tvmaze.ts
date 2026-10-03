import { TVMazeSeason } from "../../src/utils/types";
import { TVMazeEpisode } from "../../src/utils/types/tvmaze";

export const testDoctorWhoTVMazeSeasons: TVMazeSeason[] = [
  {
    id: 1,
    number: 1,
    episodeOrder: 13,
    url: "",
  },
  {
    id: 2,
    number: 2,
    episodeOrder: 13,
    url: "",
  },
  {
    id: 3,
    number: 3,
    episodeOrder: 13,
    url: "",
  },
  {
    id: 4,
    number: 4,
    episodeOrder: 13,
    url: "",
  },
  {
    id: 5,
    number: 5,
    episodeOrder: 13,
    url: "",
  },
  {
    id: 6,
    number: 6,
    episodeOrder: 13,
    url: "",
  },
];

const baseTVMazeEpisode: TVMazeEpisode = {
  _links: {
    self: {
      href: "",
    },
    show: {
      href: "",
      name: "",
    },
  },
  airdate: "",
  airstamp: "",
  airtime: "",
  id: 1,
  image: {
    medium: "",
    original: "",
  },
  name: "",
  number: 1,
  rating: {
    average: 1,
  },
  runtime: 46,
  season: 1,
  summary: "",
  type: "",
  url: "",
};

export const testDoctorWhoTVMazeEpisodes: TVMazeEpisode[] = [
  {
    ...baseTVMazeEpisode,
    id: 1,
    season: 1,
    number: 1,
    name: "Rose",
  },
  {
    ...baseTVMazeEpisode,
    id: 2,
    season: 1,
    number: 2,
    name: "The End of the World",
  },
  {
    ...baseTVMazeEpisode,
    id: 3,
    season: 1,
    number: 3,
    name: "The Unquiet Dead",
  },
  {
    ...baseTVMazeEpisode,
    id: 4,
    season: 1,
    number: 4,
    name: "Aliens of London",
  },
];
