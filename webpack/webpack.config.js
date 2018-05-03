const path = require('path')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const build_dir = process.env.BUILD_DIR || '../build'

module.exports = {
  entry: {
    // entrypoints
    // foundation based stylesheets
    stylesheets: 'stylesheets/universitas.scss',
    // public page chunks
    head: 'javascripts/head.js',
    vendor: 'javascripts/vendor.js',
    foot: 'javascripts/foot.js',
    // react apps
    photo_list_view: 'entrypoints/photo_list_view.js',
    photo_crop_app: 'entrypoints/photo_crop_app.js',
    prodsys: 'entrypoints/prodsys.js',
  },
  output: {
    // for example ../build/head.[hash].js
    path: path.join(build_dir, ''),
    filename: '[name].js',
  },
  plugins: [
    new webpack.ProvidePlugin({
      // implicitly `import`
      $: 'jquery',
      jQuery: 'jquery',
      React: 'react',
      R: 'ramda',
      PropTypes: 'prop-types',
    }),
    new BundleTracker({
      // for django integration
      indent: ' ',
      path: build_dir,
      filename: 'webpack-stats.json',
    }),
    new webpack.optimize.CommonsChunkPlugin({
      // output a react-common chunk
      name: 'react-common',
      chunks: ['prodsys', 'photo_list_view', 'photo_crop_app'],
    }),
    new webpack.optimize.CommonsChunkPlugin({
      // output a chunk to bootstrap react
      name: 'webpack-bootstrap',
      minChunks: Infinity,
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(svg|gif|jpg|png|woff|woff2|eot|ttf|svg)$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              name: 'assets/[name]-[hash:12].[ext]',
              limit: 20000, // inline smaller files in css
            },
          },
        ],
      },
      {
        test: /\.scss$/,
        use: [
          { loader: 'style-loader' },
          { loader: 'css-loader', options: { sourceMap: false } },
          {
            loader: 'postcss-loader', // for autoprefix
            options: {
              sourceMap: false,
              plugins: () => [require('autoprefixer')],
            },
          },
          {
            loader: 'sass-loader',
            options: {
              sourceMap: false,
              includePaths: [
                'node_modules/foundation-sites/scss/',
                'node_modules/slick-carousel/',
              ],
            },
          },
        ],
      },
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'babel-loader',
            options: {
              cacheDirectory: true,
            },
          },
        ],
      },
    ],
  },
  resolve: {
    modules: ['src/react', 'src', 'node_modules'],
    unsafeCache: true,
    alias: {
      // use unminified jquery source to enable deduping etc.
      // http://stackoverflow.com/a/28989476/1977847
      jquery: 'jquery/src/jquery',
    },
  },
}
