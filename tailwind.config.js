/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./pravaah/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        background: '#000000',
        primary: '#FFFFFF',
        secondary: '#A0A0A0',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['"Cormorant Garamond"', '"Noto Serif Devanagari"', '"Noto Serif Gurmukhi"', 'serif'],
      },
    },
  },
  plugins: [],
}
