var webpack = require('webpack');

module.exports = {
	//entry:  __dirname + "/app/main.js",
	entry: {
		'js/top-answer-list': __dirname + '/app/top-answer-list.js',
		'js/bundle': __dirname + '/app/main.js',
	},
	output: {
		path: __dirname + '/public',
		filename: '[name].js',
	},
	module: {
		loaders: [
			{
				test: /\.(css)$/,
				use: [{
					loader: 'style-loader', // inject CSS to page
				}, {
					loader: 'css-loader', // translates CSS into CommonJS modules
				}]
			}
		]
	},
	plugins: [
		new webpack.ProvidePlugin({
			$: 'jquery',
			jQuery: 'jquery',
			'window.jQuery': 'jquery',
			Popper: ['popper.js', 'default'],
			// In case you imported plugins individually, you must also require them here:
			Util: "exports-loader?Util!bootstrap/js/dist/util",
			Dropdown: "exports-loader?Dropdown!bootstrap/js/dist/dropdown",
		})
	]
}

