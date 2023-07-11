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
        './**/templates/**/*.html',
        './**/templates/**/**/*.html',
        './**/static/js/*.js',
    ],
    theme: {
        extend: {
            colors: {
                'bg-default' : '#121212',
                'bg-light' : '#656565',
                'default' : '#121212',
                'card-bg' : '#262626',
                'card-bg-dark': '#1C1C1C',
                'hover-bg-light': '#373b3d',
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
                'bf2042-1-sm' : '0 0 1px #011C26',
                'bf2042-2-sm' : '0 0 1px #025159',
                'bf2042-3-sm' : '0 0 1px #08A696',
                'bf2042-4-sm' : '0 0 1px #26FFDF',
                'bf2042-5-sm' : '0 0 1px #F26A1B',
                'bf2042-6-sm' : '0 0 1px #FF2C10',
                'bf2042-6-lg' : '0 0 10px #FF2C10',
                'bf2042-3-lg' : '0 0 10px #08A696',
                'bf2042-2-lg' : '0 0 10px #025159',
                'hover-bg-light-sm' : '0 1px 1px #474c50',
                'hover-bg-light' : '0 0 0.35rem #474c50',
                'hover-bg-light-lg' : '0 0 10px #474c50',
            },
            gridTemplateColumns: {
                'auto-fit': 'repeat(auto-fit, minmax(0, 1fr))',
                'auto-fll': 'repeat(auto-fill, minmax(0, 1fr))',
            },
            borderWidth:{
                '1/2' : '0.5px',
            },
            backgroundImage: {
                'bf_stripe_bg' : "url('/static/images/bf_stripe_bg.png')",
                'repeated-square' : "url('/static/images/repeated-square-dark.png')",
            },
            fontFamily: {
                montserrat: ["MONTSERRAT", "sans-serif"],
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
