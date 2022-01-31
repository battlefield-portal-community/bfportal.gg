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
                'bg-default' : '#121212',
                'card-bg' : '#262626',
                'hover-bg-light': '#474c50',
                'accent-bg' : '#303030',
                'discord-dark': "#303434",
                'discord-light-dark': "#36393f",
                'bf2042-1': "#011C26",
                'bf2042-2': "#025159",
                'bf2042-3': "#08A696",
                'bf2042-4': "#26FFDF",
                'bf2042-5': "#F26A1B",
                'bf2042-6': "#FF2C10",
            },
            dropShadow: {
                'bf2042-1' : '0 0 0.35rem #011C26',
                'bf2042-2' : '0 0 0.35rem #025159',
                'bf2042-3' : '0 0 0.35rem #08A696',
                'bf2042-4' : '0 0 0.35rem #26FFDF',
                'bf2042-5' : '0 0 0.35rem #F26A1B',
                'bf2042-6' : '0 0 0.35rem #FF2C10',
                'bf2042-1-sm' : '0 1px 1px #011C26',
                'bf2042-2-sm' : '0 1px 1px #025159',
                'bf2042-3-sm' : '0 1px 1px #08A696',
                'bf2042-4-sm' : '0 1px 1px #26FFDF',
                'bf2042-5-sm' : '0 1px 1px #F26A1B',
                'bf2042-6-sm' : '0 1px 1px #FF2C10',
                'hover-bg-light' : '0 1px 1px #474c50',
            },
            gridTemplateColumns: {
                'auto-fit': 'repeat(auto-fit, minmax(0, 1fr))',
                'auto-fll': 'repeat(auto-fill, minmax(0, 1fr))',
            },
            borderWidth:{
                '1/2' : '0.5px',
            },
        }
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
    ],
}
