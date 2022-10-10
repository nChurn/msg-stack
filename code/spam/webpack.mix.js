const mix = require('laravel-mix');

/*
 |--------------------------------------------------------------------------
 | Mix Asset Management
 |--------------------------------------------------------------------------
 |
 | Mix provides a clean, fluent API for defining some Webpack build steps
 | for your Laravel application. By default, we are compiling the Sass
 | file for the application as well as bundling up all the JS files.
 |
 */

mix.
	js('resources/js/app.js', 'public/js')
	// .extract(['bootstrap'])
   .sass('resources/sass/app.scss', 'public/css')
   .copy('resources/js/tinymce.min.js', 'public/js/tinymce.min.js')
   .copy('node_modules/tempusdominus-bootstrap-4/build/js/tempusdominus-bootstrap-4.min.js', 'public/js/tempusdominus-bootstrap-4.min.js')
   .copy('resources/js/themes/', 'public/js/themes')
   .copy('resources/js/plugins/', 'public/js/plugins')
   .copy('resources/js/langs/', 'public/js/langs')
   .copy('resources/js/skins/', 'public/js/skins')
   // .copy('node_modules/trumbowyg/dist/ui/icons.svg', 'public/svg/icons.svg')
   // .copy('node_modules/trumbowyg/dist/ui/icons.svg', 'public/svg/icons.svg')
   ;
