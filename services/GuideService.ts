import axios from "axios";
import { Dayjs } from "dayjs";

import Guide from "../database/models/Guide";
import GuideEpisode from "../database/models/GuideEpisode";
import Reminder from "../database/models/Reminder";
import SearchItem from "../database/models/SearchItem";
import ShowDetails from "../database/models/ShowDetails";
import ShowEpisode from "../database/models/ShowEpisode";
import { ABCGuide, ShowData } from "../types";

class GuideService {


  async createNewGuide(date: Dayjs) {
    const guide = await Guide.create({
      date: date.toDate(),
    });
    await this.searchFTAGuide(guide.id, date);
  }
  
  async searchFTAGuide(guideId: number, date: Dayjs) {
    console.log(`Retrieving guide data for ${date}`);

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

    const guideEpisodes: GuideEpisode[] = [];
    for (const show of showsFound) {
      const showDetails = await ShowDetails.findOne({
        where: { title: show.title },
        include: [
          {
            model: Reminder,
            as: "reminders",
          },
        ],
      });
      const showEpisode = await ShowEpisode.findOne({
        // TODO: use this or episode_title
        where: {
          show: show.title,
          seasonNumber: show.season_number,
          episodeNumber: show.episode_number,
        }
      });

      if (showDetails) {
        const guideEpisode = await GuideEpisode.create({
          title: show.title,
          channel: show.channel,
          startTime: show.start_time,
          endTime: show.end_time,
          seasonNumber: show.season_number,
          episodeNumber: show.episode_number,
          episodeTitle: show.episode_title,
          repeat: showEpisode ? showEpisode.airDates.length > 0 : false,
          dbEvent: null,
          showId: showDetails.id,
          episodeId: showEpisode?.id ?? 0,
          reminderId: showDetails.reminders ? showDetails.reminders[0].id : null,
          guideId: guideId,
        });
        
        await guideEpisode.reload({
          include: [
            {
              model: ShowEpisode,
              as: "showEpisode",
            },
          ],
        });

        if (!show.channel.includes("HD")) {
          await guideEpisode.captureDBEvent();
        }
        
        guideEpisodes.push(guideEpisode);
      }
    }

    const message = this.composeMessage(guideEpisodes);
    console.log(message)
  }

  composeMessage(shows: GuideEpisode[]) {
    let message = "\nFree to Air:\n";
  
    if (shows.length === 0) {
      message += "Nothing on Free to Air today\n";
    }
    else {
      shows.forEach(show => message += `* ${show.getMessageString()}\n`);
    }
  
    return message;
  }
}

export default GuideService;