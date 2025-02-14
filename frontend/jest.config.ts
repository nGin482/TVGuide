import { Config } from "jest";

const jestConfig: Config = {
    preset: "ts-jest",
    verbose: true,
    testEnvironment: "jest-environment-jsdom",
    transform: {
        "^.+\\.(ts|tsx|js|jsx)$": "ts-jest",
        "\.(scss|sass|css)$": "./src/tests/mocks/style.ts",
        "\\.(jpg|ico|jpeg|png)": "./src/tests/mocks/style.ts",
    },
    setupFilesAfterEnv: [
        "./src/setupTests.js",
        "@testing-library/jest-dom/extend-expect"
    ],
};

export default jestConfig;