import { DataTypes, Model } from "sequelize";

import { sequelize } from "../connection";
import GuideEpisode from "./GuideEpisode";
import { formatDate } from "../../utils";
import { Guide as TGuide } from "../../types";



class Guide extends Model<TGuide, Omit<TGuide, "id">> {
  declare id: number;
  declare date: Date;
  declare shows: GuideEpisode[];

  static associate() {
    Guide.hasMany(GuideEpisode, { foreignKey: "guide_id", as: "shows" });
  }

  composeMessage() {
    let message = `# ${formatDate(this.date, "dddd DD-MM-YYYY")} TVGuide\n`;
    message += "\nFree to Air:\n";
  
    if (this.shows.length === 0) {
      message += "Nothing on Free to Air today\n";
    }
    else {
     this.shows.forEach(show => message += `* ${show.getMessageString()}\n`);
    }
  
    return message;
  }

  composeEventsMessage() {
    let message = `# Events - ${formatDate(this.date, "dddd DD-MM-YYYY")}\n`

    if (this.shows.length > 0) {
      const events = this.shows.map(
        show => `${show.title} - ${show.dbEvent}`
      );
      message += `* ${events.join("\n* ")}`;
    }
    else {
      message += "No events occurred today"
    }

    return message
  }
}

Guide.init(
  {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      allowNull: false,
      autoIncrement: true,
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