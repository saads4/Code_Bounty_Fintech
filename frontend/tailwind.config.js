/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0b1020',
        card: '#121a33',
        accent: '#6ea8fe',
      },
      boxShadow: {
        card: '0 6px 22px rgba(0,0,0,0.25)'
      }
    },
  },
  darkMode: 'class',
  plugins: [],
}
