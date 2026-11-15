/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        agent: {
          antigravity: "#10b981",
          claude: "#f59e0b",
          codex: "#3b82f6",
        }
      }
    },
  },
  plugins: [],
}

