import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
const path = require("path");

module.exports = {
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.watchOptions = {
        ignored: [
          '**/node_modules',
          '**/.git',
          '**/C:/pagefile.sys', // ignore system file
        ],
      };
    }
    return config;
  },
};
