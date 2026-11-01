import { parseArgs, ParseArgsConfig } from "util";
import dayjs from "dayjs";
import dotenv from "dotenv";

dotenv.config({ quiet: true });

interface Config {
  hermesToken: string;
  tvguideChannelId: string;
  nGinUserId: string;
  date?: string;
  verbose?: boolean;
}

const argumentsConfig: ParseArgsConfig = {
  options: {
    date: {
      type: "string",
      default: dayjs().format("YYYY-MM-DD"),
    },
    verbose: {
      type: "boolean",
      short: "v",
      default: false,
    }
  },
};

const { values } = parseArgs(argumentsConfig);
const date = values.date as string | undefined;
const verbose = values.verbose as boolean | undefined;


const getEnvironmentVariable = (envVar: string) => {
  const environmentVariable = process.env[envVar];
  if (!environmentVariable) {
    throw Error(`Environment variable for ${envVar} not set`);
  }

  return environmentVariable;
};

export const appConfig: Config = {
  hermesToken: getEnvironmentVariable("HERMES"),
  tvguideChannelId: getEnvironmentVariable("TVGUIDE_CHANNEL"),
  nGinUserId: getEnvironmentVariable("NGIN"),
  date: date,
  verbose: verbose,
};
