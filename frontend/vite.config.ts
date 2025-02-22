import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "url";

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, `./`, "");
    return {
        plugins: [
            react()
        ],
        base: "./",
        build: {
            rollupOptions: {
                input: {
                    app: fileURLToPath(new URL("./index.html", import.meta.url))
                },
                output: [
                    {
                        name: "app",
                        dir: "build"
                    }
                ]
            }
        },
        preview: {
            open: true,
        },
        define: {
            "process.env": env
        },
    }
})