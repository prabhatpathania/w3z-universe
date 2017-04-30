var webpack = require('webpack');

var plugins = [];

module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'static/js/bundle.js'
  },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: '/(node_modules|bower_components)/',
        loader: 'babel',
        query: {
          presets: ['react', 'es2015']
        }
      },
      {
        test: /\.css$/, // Only .css files
        loader: 'style!css' // Run both loaders
      },
      {
        test: /\.json$/,
        loader: 'json'
      }
    ]
  },
  plugins: plugins
};
