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
  dbEvent: string;
  showId: number;
  episodeId: number;
  reminderId: string;
}

export interface ShowDetails {
  id: number;
  title: string;
  description: string;
  tvmazeId: string;
  genres: string[];
  image: string;
}