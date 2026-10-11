export interface Guide {
  id: string;
  date: Date;
}

export interface GuideEpisode {
  id: number;
  guideId: number;
  title: string;
  channel: string;
  startTime: Date;
  endTime: Date;
  seasonNumber: number;
  episodeNumber: number;
  episodeTitle: string;
  repeat: boolean;
  dbEvent: string | null;
  showId: number;
  episodeId: number;
  reminderId: number | null;
}

export interface ShowDetails {
  id: number;
  title: string;
  description: string;
  tvmazeId: string;
  genres: string[];
  image: string;
}

export interface ShowEpisode {
  id: number;
  show: string;
  seasonNumber: number;
  episodeNumber: number;
  episodeTitle: string;
  alternativeTitles: string[];
  summary: string;
  channels: string[];
  airDates: Date[];
  showId: number;
}

export interface SearchItem {
  id: number;
  show: string;
  searchActive: boolean;
  exactTitleMatch: boolean;
  minSeasonNumber: number;
  maxSeasonNumber: number;
  ignoreTitles: string[];
  ignoreSeasons: number[];
  ignoreEpisodes: string[];
  showId: number;
}

export interface Reminder {
  id: number;
  show: string;
  alert: "Before" | "During" | "After";
  warningTime: number;
  occasions: string;
  showId: number;
}

export interface User {
  id: number;
  username: string;
  password: string;
  role: string;
}

export interface UserSearchSubscription {
  id: number;
  userId: number;
  searchId: number;
}

export interface ABCGuide {
  region: "Sydney";
  date: string;
  schedule: GuideSchedule[];
}

interface GuideSchedule {
  channel: string;
  listing: ScheduleShow[];
}

export interface ScheduleShow {
  start_time: string;
  end_time: string;
  show_id: number;
  show_type: string;
  title: string;
  episode_num?: number;
  series_num?: number;
  episode_title?: string;
  description: string;
  length: number;
  rating: string;
  consumer_advice: string;
  repeat: boolean;
  captioning: boolean;
  live: boolean;
  genres: string[];
  crid: string;
  "series-crid": string;
  image_file: string;
}

export interface ShowData {
  title: string;
  channel: string;
  start_time: Date;
  end_time: Date;
  season_number: number;
  episode_number: number;
  episode_title: string;
  repeat?: boolean;
}
