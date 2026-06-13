/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#f0fdf4",
          100: "#dcfce7",
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
          900: "#14532d",
        },
        pitch: {
          dark:  "#0a1628",
          mid:   "#0f1f3d",
          light: "#162847",
        },
      },
      fontFamily: {
        display: ["'Barlow Condensed'", "sans-serif"],
        body:    ["'DM Sans'", "sans-serif"],
        mono:    ["'JetBrains Mono'", "monospace"],
      },
      animation: {
        "pulse-live": "pulse 1.5s cubic-bezier(0.4,0,0.6,1) infinite",
        "slide-up":   "slideUp 0.3s ease-out",
        "fade-in":    "fadeIn 0.4s ease-out",
      },
      keyframes: {
        slideUp:  { "0%": { transform: "translateY(8px)", opacity: 0 }, "100%": { transform: "translateY(0)", opacity: 1 } },
        fadeIn:   { "0%": { opacity: 0 }, "100%": { opacity: 1 } },
      },
    },
  },
  plugins: [],
};
