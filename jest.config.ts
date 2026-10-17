import { Config } from "jest";

const jestConfig: Config = {
  collectCoverage: true,
  coverageDirectory: "coverage",
  coveragePathIgnorePatterns: [
    "tests/",
  ],
  preset: "ts-jest",
  testPathIgnorePatterns: [
    "frontend/tests",
  ],
  transform: {
    "^.+\\.(ts|tsx|js|jsx)$": "ts-jest",
  },
  verbose: true,
};

export default jestConfig;