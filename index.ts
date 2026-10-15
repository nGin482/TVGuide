import { parseArgs, ParseArgsConfig } from "util";
import dayjs from "dayjs";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";

import { connectDB } from "./database";
import GuideService from "./services/GuideService";

dayjs.extend(timezone);
dayjs.extend(utc);

const config: ParseArgsConfig = {
  options: {
    date: {
      type: "string",
      default: dayjs().format("YYYY-MM-DD"),
    },
  },
};

const { values } = parseArgs(config);
const date = values.date as string | undefined;

const guideDate = dayjs(date).tz("Australia/Sydney");


async function main() {
  await connectDB();

  const guideService = new GuideService();
  await guideService.createNewGuide(guideDate);
}

main();