import { DataTypes, Model } from "sequelize";

import { Guide as TGuide } from "../../types";
import { sequelize } from "..";



class Guide extends Model<TGuide, Omit<TGuide, "id">> {
  declare id: number;
  declare date: Date;
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