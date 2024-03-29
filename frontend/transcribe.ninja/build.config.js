/**
 * This file/module contains all configuration for the build process.
 */
module.exports = {
  /**
   * The `build_dir` folder is where our projects are compiled during
   * development and the `compile_dir` folder is where our app resides once it's
   * completely built.
   */
  build_dir: 'build',
  compile_dir: 'bin',

  /**
   * This is a collection of file patterns that refer to our app code (the
   * stuff in `src/`). These file paths are used in the configuration of
   * build tasks. `js` is all project javascript, less tests. `ctpl` contains
   * our reusable components' (`src/common`) template HTML files, while
   * `atpl` contains the same, but for our app's code. `html` is just our
   * main HTML file, `less` is our main stylesheet, and `unit` contains our
   * app's unit tests.
   */
   
  app_files: {
    commonjs: [ '../src/app/**/*.js', '!../src/app/**/*.spec.js' ],
    js: [ 'src/**/*.js', '!src/**/*.spec.js', '!src/assets/**/*.js' ],
    jsunit: [ '../common/app/**/*.spec.js', 'src/**/*.spec.js' ],
    
    coffee: [ 'src/**/*.coffee', '!src/**/*.spec.coffee' ],
    coffeeunit: [ 'src/**/*.spec.coffee' ],

    atpl: [ 'src/app/**/*.tpl.html' ],
    ctpl: [ '../src/app/**/*.tpl.html' ],

    html: [ 'src/index.html' ],
    less: 'src/less/main.less'
  },

  /**
   * This is a collection of files used during testing only.
   */
  test_files: {
    js: [
      'vendor/angular-mocks/angular-mocks.js'
    ]
  },

  /**
   * This is the same as `app_files`, except it contains patterns that
   * reference vendor code (`vendor/`) that we need to place into the build
   * process somewhere. While the `app_files` property ensures all
   * standardized files are collected for compilation, it is the user's job
   * to ensure non-standardized (i.e. vendor-related) files are handled
   * appropriately in `vendor_files.js`.
   *
   * The `vendor_files.js` property holds files to be automatically
   * concatenated and minified with our project source files.
   *
   * The `vendor_files.css` property holds any CSS files to be automatically
   * included in our app.
   *
   * The `vendor_files.assets` property holds any assets to be copied along
   * with our app's assets. This structure is flattened, so it is not
   * recommended that you use wildcards.
   */
  vendor_files: {
    js: [
      'vendor/angular/angular.js',
      'vendor/placeholders/angular-placeholders-0.0.1-SNAPSHOT.min.js',
      'vendor/angular-ui-router/release/angular-ui-router.js',
      'vendor/angular-ui-utils/modules/route/route.js',
      'vendor/angular-inflector/dist/angular-inflector.js',
      'vendor/es5-shim/es5-shim.js',
      'vendor/angular-translate/angular-translate.min.js',
      'vendor/angular-sanitize/angular-sanitize.js',
      'vendor/angular-file-upload/dist/angular-file-upload.js',
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
      'vendor/peaks.js/peaks.min.js',
      'vendor/peaks.js/peaks.min.map',
      'vendor/angular-elastic/elastic.js',
      'vendor/jquery-highlighttextarea/jquery.highlighttextarea.js',
      'vendor/google-diff-match-patch/diff_match_patch_uncompressed.js',
      'vendor/angular-diff-match-patch/angular-diff-match-patch.js',
      'vendor/angular-mask/dist/ngMask.js',
      // 'vendor/angular-bootstrap/'
      // 'vendor/jquery/dist/jquery.js',
      // 'vendor/wavesurfer.js/build/wavesurfer.min.js',

      
      
    ],
    css: [
    // 'vendor/jquery-highlighttextarea/jquery.highlighttextarea.css'
    ],
    assets: [
    ]
  },
};
