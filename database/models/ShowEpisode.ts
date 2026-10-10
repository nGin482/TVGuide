import { DataTypes, Model } from "sequelize";

import { sequelize } from "../connection";
import ShowDetails from "./ShowDetails";
import { ShowEpisode as TShowEpisode } from "../../types";



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
  }
}

ShowEpisode.init(
  {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      allowNull: false,
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
