module.exports = function (api) {
  api.cache(true);
  return {
    presets: ["babel-preset-expo"],
    plugins: [
      [
        "module-resolver",
        {
          alias: {
            "@": "./src",
            "@components": "./src/components",
            "@design": "./src/design-system",
            "@services": "./src/services",
            "@data": "./src/data",
            "@hooks": "./src/hooks",
            "@types": "./src/types",
          },
        },
      ],
      "react-native-reanimated/plugin",
    ],
  };
};
