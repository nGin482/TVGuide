import { parseArgs, ParseArgsConfig } from "util";
import dayjs from "dayjs";

interface Config {
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

export const appConfig: Config = {
  date: date,
  verbose: verbose,
};
