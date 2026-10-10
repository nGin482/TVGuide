import axios from "axios";

import SearchItem from "../database/models/SearchItem";
import { ABCGuide, ShowData } from "../types";

class GuideService {


  async createNewGuide(date: string) {
    console.log(`Retrieving guide data for ${date}`);

    const guideResponse = await axios.get<ABCGuide>(
      `https://cdn.iview.abc.net.au/epg/processed/Sydney_${date}.json`
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

    const message = this.composeMessage(showsFound);
    console.log(message)
  }

  composeMessage(shows: ShowData[]) {
    let message = "\nFree to Air:\n";
  
    if (shows.length === 0) {
      message += "Nothing on Free to Air today\n";
    }
    else {
      shows.forEach(show => message += `* ${this.messageString(show)}\n`);
    }
  
    return message;
  }
  
  messageString(show: ShowData) {
    const {
      channel,
      end_time,
      episode_number,
      episode_title,
      repeat,
      season_number,
      start_time,
      title,
    } = show;
  
    const seasonNumber = season_number === -1 ? "Unknown" : season_number;
    let message = `${start_time.toTimeString()}: ${title} is on ${channel}`;
    message += ` (Season ${seasonNumber}, Episode ${episode_number}`;
    if (episode_title) {
      message += `: ${episode_title}`;
    }
    message += ")";
    if (repeat) {
      message += ` (Repeat)`;
    }
    return message;
  }
}

export default GuideService;