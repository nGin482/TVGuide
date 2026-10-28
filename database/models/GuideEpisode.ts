import { DataTypes, Model } from "sequelize";
import dayjs, { Dayjs } from "dayjs";

import { sequelize } from "../connection";
import Guide from "./Guide";
import ShowDetails from "./ShowDetails";
import Reminder from "./Reminder";
import ShowEpisode from "./ShowEpisode";
import { GuideEpisode as TGuideEpisode } from "../../types";
import { convertDate } from "../../utils";



class GuideEpisode extends Model<TGuideEpisode, Omit<TGuideEpisode, "id">> {
  declare id: number;
  declare guideId: number;
  declare title: string;
  declare channel: string;
  declare startTime: Date;
  declare endTime: Date;
  declare seasonNumber: number;
  declare episodeNumber: number;
  declare episodeTitle: string;
  declare repeat: boolean;
  declare dbEvent: string;
  declare showId: number;
  declare episodeId: number;
  declare reminderId: number;
  declare showDetails: ShowDetails;
  declare showEpisode: ShowEpisode | null;
  declare reminder: Reminder | null;

  static associate() {
    GuideEpisode.belongsTo(Guide, { foreignKey: "guide_id" });
    GuideEpisode.belongsTo(
      ShowDetails,
      { foreignKey: "show_id", as: "showDetails" }
    );
    GuideEpisode.belongsTo(
      ShowEpisode,
      { foreignKey: "episode_id", as: "showEpisode" }
    );
    GuideEpisode.belongsTo(
      Reminder,
      { foreignKey: "reminder_id", as: "reminder" }
    );
  }

  async captureDBEvent() {
    if (this.showEpisode) {
      const airDate = convertDate(this.startTime);
      this.showEpisode.set(
        "airDates",
        [...this.showEpisode.airDates, airDate]
      );

      let dbEvent = `${this.getEpisodeString()} has aired today`;
      const channels = this.showEpisode.checkChannel(this.channel);
      if (channels.length > 0) {
        dbEvent = this.showEpisode.addChannels(channels);
      }
      await this.showEpisode.save();
      return await this.update({ dbEvent: dbEvent });
    }
    else {
      const showEpisode = await ShowEpisode.create({
        show: this.title,
        seasonNumber: this.seasonNumber,
        episodeNumber: this.episodeNumber,
        episodeTitle: this.episodeTitle,
        summary: "",
        alternativeTitles: [],
        airDates: [convertDate(this.startTime)],
        channels: [this.channel],
        showId: this.showId,
      });
      const dbEvent = `${this.getEpisodeString(true)} has been inserted`;
      return await this.update({
        episodeId: showEpisode.id,
        dbEvent: dbEvent,
      });
    }
  }

  getMessageString() {
    const startTime = dayjs(this.startTime).format("HH:mm");
    let message = `${startTime}: ${this.title} is on ${this.channel}`;
    message += ` (${this.getEpisodeString()})`;
    if (this.repeat) {
      message += ` (Repeat)`;
    }
    return message;
  }

  /**
   * 
   * @param seasonNumberOverride Should be passed in if season number could be -1.
   * 
   * Pass in to keep the season number as -1. Otherwise, will default to "Unknown"
   * @returns 
   */
  getEpisodeString(seasonNumberOverride?: boolean) {
    let season_number: number | "Unknown" = this.seasonNumber;
    if (season_number === -1 && !seasonNumberOverride) {
      season_number = "Unknown";
    }
    let info = `Season ${season_number}, Episode ${this.episodeNumber}`;
    if (this.episodeTitle) {
      info += `: ${this.episodeTitle}`;
    }

    return info;
  }
}


GuideEpisode.init(
  {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      allowNull: false,
      autoIncrement: true,
    },
    guideId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "guide_id",
    },
    title: {
      type: DataTypes.INTEGER,
      allowNull: false,
    },
    channel: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    startTime: {
      type: DataTypes.DATE,
      allowNull: false,
      field: "start_time",
    },
    endTime: {
      type: DataTypes.DATE,
      allowNull: false,
      field: "end_time",
    },
    seasonNumber: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "season_number",
    },
    episodeNumber: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "episode_number",
    },
    episodeTitle: {
      type: DataTypes.TEXT,
      allowNull: false,
      field: "episode_title",
    },
    repeat: {
      type: DataTypes.BOOLEAN,
      allowNull: false,
    },
    dbEvent: {
      type: DataTypes.TEXT,
      field: "db_event",
    },
    showId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "show_id",
    },
    episodeId: {
      type: DataTypes.INTEGER,
      allowNull: true,
      field: "episode_id",
    },
    reminderId: {
      type: DataTypes.INTEGER,
      allowNull: true,
      field: "reminder_id",
    },
  },
  {
    sequelize: sequelize,
    freezeTableName: true,
    tableName: "GuideEpisode",
    timestamps: false,
  },
);

export default GuideEpisode;