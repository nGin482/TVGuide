import { DataTypes, Model } from "sequelize";

import { sequelize } from "../connection";
import Guide from "./Guide";
import { GuideEpisode as TGuideEpisode } from "../../types";



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
  declare reminderId: string;

  static associate() {
    GuideEpisode.belongsTo(Guide, { foreignKey: "guide_id" });
  }
}


GuideEpisode.init(
  {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      allowNull: false,
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
      allowNull: false,
      field: "db_event",
    },
    showId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "show_id",
    },
    episodeId: {
      type: DataTypes.INTEGER,
      allowNull: false,
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