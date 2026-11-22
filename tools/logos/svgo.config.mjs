// svgo settings for rebuilding brand logos (used by audit.py).
// Goal: clean, portable SVG with the same rendered pixels as the source artwork.
// Path data keeps 5 decimals so shapes are not visibly moved. audit.py measures
// the rendered difference against the source and refuses rebuilds that change it.
export default {
  multipass: true,
  floatPrecision: 5,
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          convertColors: { shorthex: false, names2hex: true, rgb2hex: true },
        },
      },
    },
    'removeDimensions',
    {
      name: 'removeAttrs',
      params: { elemSeparator: '#', attrs: ['data-name', 'xml:space', 'enable-background'] },
    },
  ],
};
