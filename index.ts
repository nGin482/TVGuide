import dayjs from "dayjs";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";

import { appConfig } from "./config";
import { connectDB } from "./database";
import GuideService from "./services/GuideService";

dayjs.extend(timezone);
dayjs.extend(utc);

const guideDate = dayjs(appConfig.date).tz("Australia/Sydney");


async function main() {
  await connectDB();

  const guideService = new GuideService();
  await guideService.createNewGuide(guideDate);
}

main();