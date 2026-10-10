import { sequelize } from "./connection";

export const connectDB = async () => {
  try {
    await sequelize.authenticate();
    console.log("Successfully connected to database");
    await syncTables();
  }
  catch (error) {
    console.error("Could not connect to database");
    console.error(error.message);
  }
};

export const syncTables = async () => {
  Guide.associate();
  GuideEpisode.associate();
  User.associate();
  UserSearchSubscription.associate();
  ShowDetails.associate();
  ShowEpisode.associate();
  SearchItem.associate();
  Reminder.associate();
};

import Guide from "./models/Guide";
import GuideEpisode from "./models/GuideEpisode";
import Reminder from "./models/Reminder";
import SearchItem from "./models/SearchItem";
import ShowDetails from "./models/ShowDetails";
import ShowEpisode from "./models/ShowEpisode";
import User from "./models/User";
import UserSearchSubscription from "./models/UserSearchSubscription";
