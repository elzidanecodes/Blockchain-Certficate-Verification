/** @type {import('tailwindcss').Config} */

module.exports = {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "node_modules/flowbite/**/*.js",
    "node_modules/flowbite-react/**/*.js",
  ],
  
  theme: {
    colors: {
      "default": "#F9FDFF",
      "blue-dark": "#197BBD",
      "blue-light": "#E4F0FF",
      "red-dark": "#DF0404",
      "red-light": "#FFC5C5",
      "purple": "#7e5bef",
      "pink": "#ff49db",
      "orange": "#ff7849",
      "green-light": "#A6E7D8",
      "green-dark": "#008767",
      "green-success": "#00B140",
      "green-medium": "#16C098",
      "yellow": "#ffc82c",
      "gray-dark": "#273444",
      "gray-unsuccess": "#9197B3",
      "gray-light": "#ACACAC",
      "gray-extralight": "#EEEEEE",
      "white": "#FFFFFF",

    },

    borderRadius: {
      '5': "5px",
      '8': "8px",
      '10': "10px",
      '30': "30px",
      '50': "50px",
    },

    extend: {},
  },
  plugins: [
    require('flowbite/plugin')
  ],
};