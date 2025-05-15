import { Config } from "jest";

const jestConfig: Config = {
    collectCoverage: true,
    coverageDirectory: "coverage",
    coveragePathIgnorePatterns: [
        "tests/test_data",
    ],
    preset: "ts-jest",
    setupFilesAfterEnv: [
        "./src/setupTests.js",
        "@testing-library/jest-dom/extend-expect"
    ],
    testEnvironment: "jest-environment-jsdom",
    transform: {
        "^.+\\.(ts|tsx|js|jsx)$": "ts-jest",
        "\.(scss|sass|css)$": "./tests/mocks/style.ts",
        "\\.(jpg|ico|jpeg|png)": "./tests/mocks/style.ts",
    },
    verbose: true,
};
    
export default jestConfig;