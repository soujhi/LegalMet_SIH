/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          navy: '#0F2942',
          blue: '#1E40AF',
          gold: '#B45309',
          saffron: '#EA580C',
          green: '#15803D',
          slate: '#F8FAFC',
          card: '#FFFFFF',
          border: '#E2E8F0'
        }
      }
    },
  },
  plugins: [],
}
