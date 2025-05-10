import { Config } from "jest";

const jestConfig: Config = {
    collectCoverage: true,
    coveragePathIgnorePatterns: [
        "tests/test_data",
    ],
    preset: "ts-jest",
    setupFilesAfterEnv: [
        "./src/setupTests.js",
        "@testing-library/jest-dom/extend-expect"
    ],
    testEnvironment: "jest-environment-jsdom",
    testPathIgnorePatterns: [

    ],
    transform: {
        "^.+\\.(ts|tsx|js|jsx)$": "ts-jest",
        "\.(scss|sass|css)$": "./tests/mocks/style.ts",
        "\\.(jpg|ico|jpeg|png)": "./tests/mocks/style.ts",
    },
    verbose: true,
};

export default jestConfig;