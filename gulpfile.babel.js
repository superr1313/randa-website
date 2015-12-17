/**
 * User: john
 * Date: 10/5/15
 * Time: 6:00 PM
 */

var gulp = require('gulp');
var stylus = require('gulp-stylus');

gulp.task('styles', function () {
    return gulp.src('./src/main/web/app/src/styles/app.styl')
        .pipe(stylus())
        .pipe(gulp.dest('./src/main/web/app/src/css'));
});

gulp.task('watch', function() {
    gulp.watch('src/main/web/app/src/styles/**/*.styl', gulp.series('styles'));
});


gulp.task('default', gulp.series('styles', 'watch'));

