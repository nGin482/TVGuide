import { DataTypes, Model } from "sequelize";

import { sequelize } from "../connection";
import GuideEpisode from "./GuideEpisode";
import { Guide as TGuide } from "../../types";



class Guide extends Model<TGuide, Omit<TGuide, "id">> {
  declare id: number;
  declare date: Date;

  static associate() {
    Guide.hasMany(GuideEpisode, { foreignKey: "guide_id", as: "episodes" });
  }
}

Guide.init(
  {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      allowNull: false,
    },
    date: {
      type: DataTypes.DATE,
      allowNull: false,
    },
  },
  {
    sequelize: sequelize,
    freezeTableName: true,
    tableName: "Guide",
    timestamps: false,
  }, 
);


export default Guide;