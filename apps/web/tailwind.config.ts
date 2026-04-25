import preset from "@keystone/config/tailwind.preset";
import type { Config } from "tailwindcss";

const config: Config = {
  presets: [preset],
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/features/**/*.{ts,tsx}",
    "./src/shared/**/*.{ts,tsx}",
  ],
};

export default config;
