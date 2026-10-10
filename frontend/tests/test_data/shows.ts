import { ShowData } from "../../src/utils/types";

import { testDoctorWhoEpisodes } from "./showEpisodes";

export const testShows: ShowData[] = [
  {
    show_name: "Doctor Who",
    show_details: {
      title: "Doctor Who",
      tvmaze_id: "1",
      description: "",
      genres: [
        "Science Fiction",
      ],
      image: "",
    },
    show_episodes: testDoctorWhoEpisodes,
    search_item: {
      id: 1,
      show: "Doctor Who",
      search_active: true,
      exact_title_match: true,
      conditions: {
        min_season_number: 1,
        max_season_number: 15,
        ignore_titles: [],
        ignore_seasons: [],
        ignore_episodes: [],
      },
    },
    reminder: {
      show: "Doctor Who",
      alert: "Before",
      occasions: "All",
      warning_time: 3,
    },
  },
];