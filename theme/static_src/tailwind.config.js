/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
            colors: {
                dark: '#2E2E46',
                light: '#3A3956',
                violet: '#9999C2',
                menu: '#626284',
                menulight: '#EB638B',
                white: '#FBFBFF',
                card: '#EA6CA1',
            },
            height: {
            '800': '800px',
            '700': '700px',
            '650': '650px',
            '620': '620px',
            '600': '600px',
            '580': '580px',
            '550': '550px',
            '500': '500px',
            '450': '450px',
            '430': '430px',
            '400': '400px',
            },
            width: {
            '1000': '1000px',
            '850': '850px',
            '800': '800px',
            '700': '700px',
            '650': '650px',
            '620': '620px',
            '600': '600px',
            '580': '580px',
            '550': '550px',
            '500': '500px',
            '450': '450px',
            '400': '400px',
            }       
        },
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/line-clamp'),
        require('@tailwindcss/aspect-ratio'),
        require('tailwind-scrollbar'),
    ],
}
