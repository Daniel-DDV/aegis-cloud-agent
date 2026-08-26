/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b1220",
        panel: "#121a2b",
        line: "#243049",
        accent: "#5eead4",
        warn: "#fbbf24",
        danger: "#fb7185",
        muted: "#94a3b8",
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "Segoe UI", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        glow: "0 0 40px rgba(94, 234, 212, 0.15)",
      },
    },
  },
  plugins: [],
};
