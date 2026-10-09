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
  SearchItem.associate();
};

import Guide from "./models/Guide";
import GuideEpisode from "./models/GuideEpisode";
import SearchItem from "./models/SearchItem";
import User from "./models/User";
import UserSearchSubscription from "./models/UserSearchSubscription";
