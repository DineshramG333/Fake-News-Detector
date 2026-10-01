/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      keyframes: {
        scan: {
          "0%": { transform: "translateX(-100%)" },
          "50%": { transform: "translateX(150%)" },
          "100%": { transform: "translateX(150%)" },
        },
      },
      animation: {
        scan: "scan 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
