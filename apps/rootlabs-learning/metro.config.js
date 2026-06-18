const { getDefaultConfig } = require("expo/metro-config");

const config = getDefaultConfig(__dirname);

// Allow importing PDF and other asset extensions
config.resolver.assetExts = [...config.resolver.assetExts, "pdf"];

module.exports = config;
