import axios from "axios";
import dayjs, { Dayjs } from "dayjs";

import Guide from "../database/models/Guide";
import GuideEpisode from "../database/models/GuideEpisode";
import Reminder from "../database/models/Reminder";
import SearchItem from "../database/models/SearchItem";
import ShowDetails from "../database/models/ShowDetails";
import ShowEpisode from "../database/models/ShowEpisode";
import { formatEpisodeTitle, parseShow } from "../utils";
import { ABCGuide, ShowData, UpcomingReminders } from "../types";

class GuideService {


  async createNewGuide(date: Dayjs) {
    const guide = await Guide.create({
      date: date.toDate(),
    });
    await this.searchFTAGuide(guide.id, date);

    await guide.reload({
      include: [
        {
          model: GuideEpisode,
          as: "shows",
          include: [
            {
              model: Reminder, 
              as: "reminder", 
            }
          ]
        },
      ],
    });
    console.log(this.findUpcomingReminders(guide));

    const guideMessage = guide.composeMessage();
    const eventsMessage = guide.composeEventsMessage();
    console.log(guideMessage)
    console.log(eventsMessage)
  }
  
  async searchFTAGuide(guideId: number, date: Dayjs) {
    console.log(`Retrieving guide data for ${date.format("YYYY-MM-DD")}`);

    const formattedDate = date.format("YYYY-MM-DD");
    const guideResponse = await axios.get<ABCGuide>(
      `https://cdn.iview.abc.net.au/epg/processed/Sydney_${formattedDate}.json`
    );
    const guide = guideResponse.data;
    
    const searchList = await SearchItem.findAll({ where: { searchActive: true } });
    
    const showsFound: ShowData[] = [];
    for (const channelData of guide.schedule) {
      for (const show of channelData.listing) {
        for (const searchItem of searchList) {
          if (show.title.toLowerCase().includes(searchItem.show.toLowerCase())) {
            const showData: ShowData = {
              title: show.title,
              channel: channelData.channel,
              start_time: new Date(show.start_time),
              end_time: new Date(show.end_time),
              season_number: show?.series_num ?? -1,
              episode_number: show?.episode_num ?? 0,
              episode_title: show?.episode_title ?? "",
            };
            
            if (searchItem.checkSearchConditions(showData)) {
              showsFound.push(showData);
            }
          }
        }
      }
    }

    showsFound.sort((showA, showB) => 
      showA.start_time.getTime() - showB.start_time.getTime() ||
      showA.channel.localeCompare(showB.channel)
    );

    const processedShows = showsFound.flatMap(show => this.buildShowData(show));

    const guideEpisodes: GuideEpisode[] = [];
    for (const show of processedShows) {
      const showDetails = await ShowDetails.findOne({
        where: { title: show.title },
        include: [
          {
            model: Reminder,
            as: "reminders",
          },
        ],
      });
      const showEpisode = await ShowEpisode.findShowEpisode(show);

      if (showDetails) {
        const reminders = showDetails.reminders;
        const guideEpisode = await GuideEpisode.create({
          title: show.title,
          channel: show.channel,
          startTime: show.start_time,
          endTime: show.end_time,
          seasonNumber: showEpisode?.seasonNumber ?? show.season_number,
          episodeNumber: showEpisode?.episodeNumber ?? show.episode_number,
          episodeTitle: showEpisode?.episodeTitle ?? show.episode_title,
          repeat: showEpisode ? showEpisode.airDates.length > 0 : false,
          dbEvent: null,
          showId: showDetails.id,
          episodeId: showEpisode?.id ?? null,
          reminderId: reminders && reminders.length > 0 ? reminders[0].id : null,
          guideId: guideId,
        });
        
        await guideEpisode.reload({
          include: [
            {
              model: ShowEpisode,
              as: "showEpisode",
            },
            {
              model: Reminder,
              as: "reminder",
            },
          ],
        });

        if (!show.channel.includes("HD")) {
          await guideEpisode.captureDBEvent();
        }
        
        guideEpisodes.push(guideEpisode);
      }
    }
  }

  findUpcomingReminders(guide: Guide): UpcomingReminders[] {
    const upcomingReminders = guide.shows.filter(show => 
      show.reminder &&
      !show.channel.includes("HD") &&
      dayjs(show.startTime).isAfter(guide.date, "hour")
    );

    return upcomingReminders.map(show => ({
      show: show,
      notifyTime: show.reminder!.calculateNotificationTime(show.startTime),
    }));
  }

  buildShowData(show: ShowData): ShowData[] {
    const { title, seasonNumber, episodeNumber, episodeTitle } = parseShow(show);

    const episodes: ShowData[] = [];
    if (title.includes("Cyberverse") && episodeTitle.includes("/")) {
      const episodeTitles = episodeTitle.split("/");
      episodeTitles.forEach((episodeTitle, idx) => {
        const duration = dayjs(show.end_time).diff(dayjs(show.start_time), "minutes");
        const lastShowStartTime = dayjs(show.start_time).add(
          Math.ceil(duration) / 2,
          "minutes"
        );
        episodes.push({
          title: title,
          channel: show.channel,
          start_time: idx === 0 ? show.start_time : lastShowStartTime.toDate(),
          end_time: idx === 0 ? lastShowStartTime.toDate() : show.end_time,
          season_number: seasonNumber,
          episode_number: idx === 0 ? episodeNumber : episodeNumber + 1,
          episode_title: formatEpisodeTitle(episodeTitle),
        });
      });
    }
    else {
      episodes.push({
        title: title,
        channel: show.channel,
        start_time: show.start_time,
        end_time: show.end_time,
        season_number: seasonNumber,
        episode_number: episodeNumber,
        episode_title: formatEpisodeTitle(episodeTitle),
      });
    }

    return episodes;
  }
}

export default GuideService;