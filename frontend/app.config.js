const appJson = require("./app.json");

if (!process.env.EXPO_PUBLIC_API_BASE_URL && process.env.VITE_API_BASE_URL) {
  process.env.EXPO_PUBLIC_API_BASE_URL = process.env.VITE_API_BASE_URL;
}

module.exports = appJson;
