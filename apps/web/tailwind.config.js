/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        ink: '#090b14',
        neon: '#65e4ff',
      },
    },
  },
  plugins: [],
}
