module.exports = function ( karma ) {
  karma.set({
    /** 
     * From where to look for files, starting with the location of this file.
     */
    basePath: '../',

    /**
     * This is the list of file patterns to load into the browser during testing.
     */
    files: [
      'vendor/angular/angular.js',
      'vendor/angular-ui-router/release/angular-ui-router.js',
      'vendor/angular-inflector/dist/angular-inflector.js',
      'vendor/angular-translate/angular-translate.min.js',
      'vendor/angular-sanitize/angular-sanitize.js',
      'vendor/angular-hotkeys/build/hotkeys.min.js',
      'vendor/angular-resource/angular-resource.js',
      'vendor/jquery/dist/jquery.js',
      'vendor/wavesurfer.js/src/wavesurfer.js',
      'vendor/wavesurfer.js/src/util.js',
      'vendor/wavesurfer.js/src/webaudio.js',
      'vendor/wavesurfer.js/src/mediaelement.js',
      'vendor/wavesurfer.js/src/drawer.js',
      'vendor/wavesurfer.js/src/drawer.canvas.js',
      'vendor/wavesurfer.js/plugin/wavesurfer.regions.js',
      'vendor/angular-elastic/elastic.js',
      'vendor/jquery-highlighttextarea/jquery.highlighttextarea.js',
      'vendor/google-diff-match-patch/diff_match_patch_uncompressed.js',
      'vendor/angular-diff-match-patch/angular-diff-match-patch.js',
      'vendor/angular-mask/dist/ngMask.js',
      'build/templates-app.js',
      'build/templates-common.js',
      'vendor/angular-mocks/angular-mocks.js',
      
      'src/**/*.js',
      'src/**/*.coffee',
    ],
    exclude: [
      'src/assets/**/*.js'
    ],
    frameworks: [ 'jasmine' ],
    plugins: [ 'karma-jasmine', 'karma-firefox-launcher', 'karma-coffee-preprocessor' ],
    preprocessors: {
      '**/*.coffee': 'coffee',
    },

    /**
     * How to report, by default.
     */
    reporters: 'dots',

    /**
     * On which port should the browser connect, on which port is the test runner
     * operating, and what is the URL path for the browser to use.
     */
    port: 9018,
    runnerPort: 9100,
    urlRoot: '/',

    /** 
     * Disable file watching by default.
     */
    autoWatch: false,

    /**
     * The list of browsers to launch to test on. This includes only "Firefox" by
     * default, but other browser names include:
     * Chrome, ChromeCanary, Firefox, Opera, Safari, PhantomJS
     *
     * Note that you can also use the executable name of the browser, like "chromium"
     * or "firefox", but that these vary based on your operating system.
     *
     * You may also leave this blank and manually navigate your browser to
     * http://localhost:9018/ when you're running tests. The window/tab can be left
     * open and the tests will automatically occur there during the build. This has
     * the aesthetic advantage of not launching a browser every time you save.
     */
    browsers: [
      'Firefox'
    ]
  });
};

