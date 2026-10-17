import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";

import { ParsedShowData, ShowData } from "../types";

dayjs.extend(duration);

export const convertDate = (date: Date) => {
  const localTime = dayjs.tz(date, "Australia/Sydney");

  return dayjs.utc(localTime.format('YYYY-MM-DD HH:mm:ss')).toDate();
};

/**
 * Format a show's episode title into a more reader-friendly appearance
 * @param episode_title 
 * @returns 
 */
export const formatEpisodeTitle = (episode_title: string) => {
  if (episode_title.includes(", The")) {
    return `The ${episode_title.replace(", The", "")}`;
  }
  else if (episode_title.includes(", A") && episode_title !== "Kolcheck, A.") {
    return `A ${episode_title.replace(", A", "")}`;
  }
  return episode_title
};

const checkShowTitles = (title: string) => {
  if (title.includes("Maigret")) {
    return "Maigret";
  }
  else if (title.includes("Death in Paradise")) {
    return "Death In Paradise";
  }
  else if (title.includes("Grantchester Christmas Special")) {
    return "Grantchester";
  }
  else if (title.includes("NCIS Encore")) {
    return "NCIS";
  }
  return title;
};

export const formatSBSEpisode = (
  showTitle: string,
  episode: string
) => {
  const regex = new RegExp(`${showTitle} Series (\d+) Ep (\d+/)`);
  const match = regex.exec(episode);
  if (match) {
    return {
      title: showTitle,
      seasonNumber: parseInt(match[1]),
      episodeNumber: parseInt(match[2]),
      episodeTitle: episode,
    };
  }
  return {
    title: showTitle,
    episodeTitle: episode,
  };
};

export const parseShow = (show: ShowData): ParsedShowData => {
  let { episode_number, episode_title, season_number, title } = show;
  if (show.title.includes(": ") && show.episode_title === "") {
    [title, episode_title] = title.split(": ");
  }
  else if (show.title.includes(" - ") && show.episode_title === "") {
    [title, episode_title] = title.split(" - ");
  }
  else if (show.episode_title.includes(`${title} - `)) {
    episode_title = show.episode_title.split(" - ")[1];
  }

  if (show.channel.includes("SBS")) {
    const sbsShow = formatSBSEpisode(show.title, show.episode_title);
    if (sbsShow.seasonNumber && sbsShow.episodeNumber) {
      season_number = sbsShow.seasonNumber;
      episode_number = sbsShow.episodeNumber;
    }
  }

  return {
    title: checkShowTitles(title),
    seasonNumber: show.season_number,
    episodeNumber: show.season_number,
    episodeTitle: episode_title,
  };
};
