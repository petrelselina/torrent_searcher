/**
 * This file/module contains all the configurations for the build process.
 */


module.exports = {
	/**
	 * This is a collection of file patterns that refer to our app code (the
	 * stuff in 'src/'). These file paths are used in the configuration of
	 * build tasks.
	 */
	appFiles: {
		js: 'src/js/**/*.js',
		jade: 'src/jade/**/*.jade',
        jadeTemplates: 'src/jade/templates/**/*.jade',
		less: 'src/less/**/*.less',
		css: 'src/css/**/*.css',
		stylus: 'src/stylus/**/*.styl',
        scss: 'src/scss/**/*.scss',
		compiledCss: 'compile/css/**/*.css'
	},
	
	/**
	 * This is a collection of files used during testing only.
	 */
	 testFiles: {
		config: 'karma/karma.conf.js',
		js: [
			'vendor/angular-mocks/angularmocks.js'
		]
	},
	
	liveReloadPort: 35790
};