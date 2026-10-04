/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        industrial: "#0E7399",
        "industrial-dark": "#0B5C7A",
        "industrial-light": "#268EB3",
        canvas: "#F8FAFC",
        line: "#E2E8F0",
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
