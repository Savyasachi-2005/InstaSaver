/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b1020",
        mist: "#8fb3ff",
        aqua: "#5eead4",
        night: "#131a2b",
      },
      boxShadow: {
        glow: "0 24px 60px rgba(94, 234, 212, 0.14)",
      },
      fontFamily: {
        display: ["'Sora'", "sans-serif"],
        body: ["'Space Grotesk'", "sans-serif"],
      },
    },
  },
  plugins: [],
};
