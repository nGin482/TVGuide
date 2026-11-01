import dayjs from "dayjs";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";
import dotenv from "dotenv";

import { appConfig } from "./config";
import { connectDB } from "./database";
import GuideService from "./services/GuideService";
import { hermes } from "./services/hermes/Hermes";

dotenv.config();

const token = process.env.HERMES;

dayjs.extend(timezone);
dayjs.extend(utc);

const guideDate = dayjs(appConfig.date).tz("Australia/Sydney");


async function main() {
  await hermes.login(token);

  await connectDB();

  const guideService = new GuideService();
  await guideService.createNewGuide(guideDate);

  if (process.env.NODE_ENV === "development") {
    await hermes.destroy();
    console.log(hermes.user?.username, "signed out");
  }
}

main();