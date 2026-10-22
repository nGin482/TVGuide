import { Config } from "jest";

const jestConfig: Config = {
  collectCoverage: true,
  coverageDirectory: "coverage",
  coveragePathIgnorePatterns: [
    "tests/",
    "__tests__/__fixtures",
  ],
  preset: "ts-jest",
  testPathIgnorePatterns: [
    "frontend/tests",
    "__tests__/__fixtures__",
  ],
  transform: {
    "^.+\\.(ts|tsx|js|jsx)$": "ts-jest",
  },
  verbose: true,
};

export default jestConfig;