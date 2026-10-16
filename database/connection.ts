import { Sequelize } from "sequelize";
import * as dotenv from "dotenv";

import { appConfig } from "../config";

dotenv.config({ quiet: true });

const DB_URL = process.env.DB_URL;

if (!DB_URL) {
  throw Error("DB_URL variable not set");
}

export const sequelize = new Sequelize(
  DB_URL,
  {
    logging: appConfig.verbose,
    timezone: "Australia/Sydney",
  }
);