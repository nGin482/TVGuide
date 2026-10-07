import { Sequelize } from "sequelize";
import * as dotenv from "dotenv";

dotenv.config({ quiet: true });

const DB_URL = process.env.DB_URL;

if (!DB_URL) {
  throw Error("DB_URL variable not set");
}

export const sequelize = new Sequelize(
  DB_URL,
  {
    timezone: "+10:00",
  }
);