/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      colors: {
        brand: {
          yellow: "#FCD34D",
          orange: "#FBBF24",
          cream: "#FEF3C7",
          softYellow: "#FAF6D5",
          darkBlue: "#1E293B",
          dark: "#111827",
        },
      },
    },
  },

  plugins: [],
};
