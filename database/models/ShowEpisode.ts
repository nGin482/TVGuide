import { DataTypes, Model } from "sequelize";

import { sequelize } from "../connection";
import ShowDetails from "./ShowDetails";
import GuideEpisode from "./GuideEpisode";
import { ShowData, ShowEpisode as TShowEpisode } from "../../types";



class ShowEpisode extends Model<TShowEpisode, Omit<TShowEpisode, "id">> {
  declare id: number;
  declare show: string;
  declare seasonNumber: number;
  declare episodeNumber: number;
  declare episodeTitle: string;
  declare alternativeTitles: string[];
  declare summary: string;
  declare channels: string[];
  declare airDates: Date[];
  declare showId: number;

  static associate() {
    ShowEpisode.belongsTo(
      ShowDetails,
      { foreignKey: "show_id", as: "ShowDetails" }
    );
    ShowEpisode.hasMany(
      GuideEpisode,
      { foreignKey: "episode_id", as: "guideEpisodes" }
    );
  }

  static async findShowEpisode(guideEpisode: ShowData) {
    const { season_number, episode_number, episode_title } = guideEpisode;

    if (season_number === -1 && episode_number === 0 && episode_title === "") {
      return null;
    }

    if (season_number !== -1 && episode_number !== 0) {
      const showEpisode = ShowEpisode.findOne({
        where: {
          seasonNumber: season_number,
          episodeNumber: episode_number,
        },
      });
      return showEpisode;
    }
    else {
      const showEpisode = ShowEpisode.findOne({
        where: { episodeTitle: episode_title }
      });
      return showEpisode;
    }
  }

  /**
    * Check that the given episode is present in the episode's channel list.
    * Return True if present, False if not.
    * 
    * If `ABC1` is present, also check `ABCHD`.
    * If `SBS` is present, also check `SBSHD`.
    * If `10` is present, also check `TENHD`.
   * @param channel 
   * @returns an array of the missing channels
   */
  checkChannel(channel: string) {
    const missingChannels: string[] = [];
    if (!this.channels.includes(channel)) {
      missingChannels.push(channel);
    }

    if (this.channels.includes("ABC1") && !this.channels.includes("ABCHD")) {
      missingChannels.push("ABCHD");
    }
    if (this.channels.includes("SBS") && !this.channels.includes("SBSHD")) {
      missingChannels.push("SBSHD");
    }
    if (this.channels.includes("10") && !this.channels.includes("TENHD")) {
      missingChannels.push("TENHD");
    }
    
    return missingChannels;
  }
  
  addChannels(channels: string[]) {
    const updatedChannels = [...this.channels, ...channels];
    this.set("channels", updatedChannels);
    this.channels = updatedChannels;

    const word = channels.length > 1 ? "have" : "has";
    return `${channels.join(", ")} ${word} been added to the channel list`;
  }
}



ShowEpisode.init(
  {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      allowNull: false,
      autoIncrement: true,
    },
    show: {
      type: DataTypes.TEXT,
      allowNull: false,
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
    alternativeTitles: {
      type: DataTypes.ARRAY(DataTypes.TEXT),
      allowNull: false,
      field: "alternative_titles",
    },
    summary: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    channels: {
      type: DataTypes.ARRAY(DataTypes.TEXT),
      allowNull: false,
    },
    airDates: {
      type: DataTypes.ARRAY(DataTypes.DATE),
      allowNull: false,
      field: "air_dates",
    },
    showId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "show_id",
    },
  },
  {
    sequelize: sequelize,
    freezeTableName: true,
    tableName: "ShowEpisode",
    timestamps: false,
  },
);

export default ShowEpisode;
