import { DataTypes, Model } from "sequelize";

import { sequelize } from "../connection";
import UserSearchSubscription from "./UserSearchSubscription";
import { SearchItem as TSearchItem } from "../../types";



class SearchItem extends Model<TSearchItem, Omit<TSearchItem, "id">> {
  declare id: number;
  declare show: string;
  declare searchActive: boolean;
  declare exactTitleMatch: boolean;
  declare minSeasonNumber: number;
  declare maxSeasonNumber: number;
  declare ignoreTitles: string[];
  declare ignoreSeasons: number[];
  declare ignoreEpisodes: string[];
  declare showId: number;

  static associate() {
    SearchItem.hasMany(
      UserSearchSubscription,
      {
        foreignKey: "search_id",
        as: "subscriptions"
      }
    );
  }
}

SearchItem.init(
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
    searchActive: {
      type: DataTypes.BOOLEAN,
      allowNull: false,
      defaultValue: true,
      field: "search_active",
    },
    exactTitleMatch: {
      type: DataTypes.BOOLEAN,
      allowNull: false,
      field: "exact_title_match",
    },
    minSeasonNumber: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "min_season_number",
    },
    maxSeasonNumber: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "max_season_number",
    },
    ignoreTitles: {
      type: DataTypes.TEXT,
      allowNull: false,
      defaultValue: [],
      field: "ignore_titles",
    },
    ignoreSeasons: {
      type: DataTypes.ARRAY(DataTypes.INTEGER),
      allowNull: false,
      defaultValue: [],
      field: "ignore_seasons",
    },
    ignoreEpisodes: {
      type: DataTypes.TEXT,
      allowNull: false,
      defaultValue: [],
      field: "ignore_episodes",
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
    tableName: "SearchItem",
    timestamps: false,
  },
)

export default SearchItem;
