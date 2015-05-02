var path = require('path');
var gulp = require('gulp');
var util = require('gulp-util');
var less = require('gulp-less');
var concat = require('gulp-concat');
var stylus = require('gulp-stylus');
var jade = require('gulp-jade');
var clean = require('gulp-clean');
var livereload = require('gulp-livereload');
var watch = require('gulp-watch');
var plumber = require('gulp-plumber');
var lazypipe = require('lazypipe');
var sass = require('gulp-sass')

// Load user config and package data.
var cfg = require('./build.config.js');

/**
 * Compile and concat scripts, styles and templates. Invoked when running 'gulp' with
 * no other arguments.
 * The task first cleans the build folder (in gulp syntax, we say the 'default' task is
 * depended on the 'clean' to run.
 */
gulp.task('default', ['build']);

/**
 * A simple command which cleans the build directory.
 */
gulp.task('clean', function () {
    return gulp.src(['build/**/*', 'compile/**/*'], { read: false })
        .pipe(clean());
});

gulp.task('build-scripts', ['clean'], function () {
    return gulp.src(cfg.appFiles.js).pipe(buildJs());
});

gulp.task('build-styles-less', ['clean'], function () {
    return gulp.src(cfg.appFiles.less).pipe(buildLess());
});

gulp.task('build-styles-stylus', ['clean'], function () {
    return gulp.src(cfg.appFiles.stylus).pipe(buildStylus());
});

gulp.task('build-styles-sass', ['clean'], function () {
    return gulp.src(cfg.appFiles.scss).pipe(buildSass());
});

gulp.task('build-styles',
    ['build-styles-less', 'build-styles-stylus', 'build-styles-sass'],
    function () {
        return gulp.src(cfg.appFiles.compiledCss).pipe(buildStyles());
    });

gulp.task('build-templates', ['clean'], function () {
    return gulp.src(cfg.appFiles.jadeTemplates).pipe(buildJade());
});

/**
 * Actual build task. Note that we hint gulp to first run clean (since we say that
 * 'build' depends on it directly.
 */
gulp.task('build', ['clean', 'build-scripts', 'build-styles', 'build-templates']);

/**
 * Watch all files and re-compile on change.
 */
gulp.task('watch', ['build'], function () {
    // Create the server so it will start listening.

    // Setup watchers.
    // Most watchers must do a full 'compilation' when a change is detected (e.g.
    // JavaScript must concat all files even if only one is changed,
    // and Jade must recompile all files since a change to a template can affect other pages.)
    var liveReloadServer = livereload({start: true, port: cfg.liveReloadPort});

    watch(cfg.appFiles.js,
        {
            emitOnGlob: false,
            name: 'JavaScript'
        },
        function (files) {
            return gulp.src(cfg.appFiles.js)
                .pipe(buildJs())
                .pipe(livereload(cfg.liveReloadPort));
        });

    watch(cfg.appFiles.jade,
        {
            emitOnGlob: false,
            name: 'Templates'
        },
        function (files) {
            return gulp.src(cfg.appFiles.jadeTemplates)
                .pipe(buildJade())
                .pipe(livereload(cfg.liveReloadPort));
        });

    // Less and Stylus can recompile only changed files since a separate watch (Css)
    // will concat all files always.
    watch(cfg.appFiles.less,
        {
            emitOnGlob: false,
            name: 'Less'
        },
        function (files) {
            return files
                .pipe(buildLess())
        });

    watch(cfg.appFiles.stylus,
        {
            emitOnGlob: false,
            name: 'Stylus'
        },
        function (files) {
            return files
                .pipe(buildStylus())
        });

    watch(cfg.appFiles.scss,
        {
            emitOnGlob: false,
            name: 'Sass'
        },
        function (files) {
            return files
                .pipe(buildSass())
        });

    watch(cfg.appFiles.compiledCss,
        {
            emitOnGlob: false,
            name: 'Css'
        },
        function (files) {
            return gulp.src(cfg.appFiles.compiledCss)
                .pipe(buildStyles())
                .pipe(livereload(cfg.liveReloadPort));
        });

    watch(cfg.appFiles.css,
        {
            emitOnGlob: false,
            name: 'Css'
        },
        function (files) {
            return files
                .pipe(livereload(cfg.liveReloadPort));
        });
});

/**
 * Concat js code to a single js file (and not vendor code).
 */
function buildJs() {
    // Lazy pipe can be attached to an existing pipe (e.g. gulp.src(..,).pipe(jsPipe)).
    var jsPipe = lazypipe()
        // Plumber takes care of errors in the pipe (ignore them and print them to the log).
        // Allows watching file and not 'crashing' when a file cannot be compiled.
        .pipe(plumber, { errorHandler: util.log })
        .pipe(concat, 'app.js')
        .pipe(gulp.dest, 'build');

    return jsPipe();
}


/**
 * Compile less styles to css.
 */
function buildLess() {
    var lessPipe = lazypipe()
        .pipe(plumber, { errorHandler: util.log })
        .pipe(less, {
            paths: [ path.join(__dirname, 'less', 'includes') ]
        })
        .pipe(gulp.dest, 'compile/css/less');

    return lessPipe();
}

/**
 * Compile stylus styles to css.
 */
function buildStylus() {
    var stylusPipe = lazypipe()
        .pipe(plumber, { errorHandler: util.log })
        .pipe(stylus)
        .pipe(gulp.dest, 'compile/css/stylus');

    return stylusPipe();
}


/**
 * Compile sass styles to css.
 */
function buildSass() {
    var stylusPipe = lazypipe()
        .pipe(plumber, { errorHandler: util.log })
        .pipe(sass)
        .pipe(gulp.dest, 'compile/css/sass');

    return stylusPipe();
}

/**
 * Compile all styles (less, stylus, etc...) to css and concat them to a single file.
 */
function buildStyles() {
    var stylesPipe = lazypipe()
        .pipe(plumber, { errorHandler: util.log })
        .pipe(concat, 'app.css')
        .pipe(gulp.dest, 'build');

    return stylesPipe();
};

/**
 * Compile jade templates to html.
 */
function buildJade() {
    var jadePipe = lazypipe()
        .pipe(plumber, { errorHandler: util.log })
        .pipe(jade, { pretty: true, locals: {buildCfg: cfg } })
        .pipe(gulp.dest, 'build');

    return jadePipe();
}