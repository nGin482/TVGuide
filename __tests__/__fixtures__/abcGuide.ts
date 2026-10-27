import { ABCGuide, ScheduleShow } from "../../types";

const baseScheduleShow: ScheduleShow = {
  "series-crid": "",
  captioning: true,
  consumer_advice: "",
  crid: "",
  description: "",
  end_time: "",
  genres: [],
  image_file: "",
  length: 0,
  live: false,
  rating: "",
  repeat: false,
  show_id: 0,
  show_type: "",
  start_time: "",
  title: "",
  series_num: 0,
  episode_num: 0,
  episode_title: "",
};

export const testABCGuide: ABCGuide = {
  date: "2026-10-2025",
  region: "Sydney",
  schedule: [
    {
      channel: "ABC1",
      listing: [
        {
          ...baseScheduleShow,
          end_time: "2026-10-25T22:00:00",
          length: 90,
          live: false,
          rating: "M",
          repeat: true,
          show_id: 1,
          start_time: "2026-10-25T20:30:00",
          title: "Endeavour",
          series_num: 1,
          episode_num: 1,
          episode_title: "Pilot",
        },
      ],
    },
    {
      channel: "ABC2",
      listing: [
        {
          ...baseScheduleShow,
          end_time: "2026-10-25T23:44:00",
          length: 90,
          live: false,
          rating: "M",
          repeat: true,
          show_id: 1,
          start_time: "2026-10-25T22:57:00",
          title: "Merlin",
          series_num: 1,
          episode_num: 1,
          episode_title: "The Dragon's Call",
        },
      ],
    },
    {
      channel: "ABCHD",
      listing: [
        {
          ...baseScheduleShow,
          end_time: "2026-10-25T22:00:00",
          length: 90,
          live: false,
          rating: "M",
          repeat: true,
          show_id: 1,
          start_time: "2026-10-25T20:30:00",
          title: "Endeavour",
          series_num: 1,
          episode_num: 1,
          episode_title: "Pilot",
        },
      ],
    },
  ],
};