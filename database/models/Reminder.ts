import { DataTypes, Model } from "sequelize";

import { sequelize } from "../connection";
import { Reminder as TReminder } from "../../types";



class Reminder extends Model<TReminder, Omit<TReminder, "id">> {
  declare id: number;
  declare show: string;
  declare alert: "Before" | "During" | "After";
  declare warning_time: number;
  declare occasions: string;
  declare show_id: number;
}


Reminder.init(
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
    alert: {
      type: DataTypes.ENUM("Before", "During", "After"),
      allowNull: false,
    },
    warningTime: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "warning_time",
    },
    occasions: {
      type: DataTypes.TEXT,
      allowNull: true,
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
    tableName: "Reminder",
    timestamps: false,
  },
);

export default Reminder;
