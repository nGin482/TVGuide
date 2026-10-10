import { DataTypes, Model } from "sequelize";

import { sequelize } from "../connection";
import ShowEpisode from "./ShowEpisode";
import GuideEpisode from "./GuideEpisode";
import SearchItem from "./SearchItem";
import Reminder from "./Reminder";
import { ShowDetails as TShowDetails } from "../../types";



class ShowDetails extends Model<TShowDetails, Omit<TShowDetails, "id">> {
  declare id: number;
  declare title: string;
  declare description: string;
  declare tvmaze_id: string;
  declare genres: string[];
  declare image: string;

  static associate() {
    ShowDetails.hasMany(
      ShowEpisode,
      { foreignKey: "show_id", as: "showEpisodes" }
    );
    ShowDetails.hasMany(
      SearchItem,
      { foreignKey: "show_id", as: "searches" }
    );
    ShowDetails.hasMany(
      Reminder,
      { foreignKey: "show_id", as: "reminders" }
    );
    ShowDetails.hasMany(
      GuideEpisode,
      { foreignKey: "show_id", as: "guideEpisodes" }
    );
  }
}

ShowDetails.init(
  {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      allowNull: false,
    },
    title: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    tvmazeId: {
      type: DataTypes.TEXT,
      allowNull: false,
      field: "tvmaze_id",
    },
    genres: {
      type: DataTypes.ARRAY(DataTypes.TEXT),
      allowNull: false,
      defaultValue: [],
    },
    image: {
      type: DataTypes.TEXT,
      allowNull: false,
    }
  },
  {
    sequelize: sequelize,
    freezeTableName: true,
    tableName: "ShowDetails",
    timestamps: false,
  },
);

export default ShowDetails;
