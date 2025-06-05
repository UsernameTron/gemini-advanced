/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          blue: '#40E0FF',
          pink: '#FF6B9D',
          purple: '#C471ED',
        },
        secondary: {
          teal: '#4ECDC4',
          coral: '#FF6B6B',
          mint: '#96CEB4',
          sky: '#45B7D1',
        },
        background: {
          dark: '#0F0F23',
          light: '#16213E',
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#B0B8C8',
        },
      },
      fontFamily: {
        sans: ['Segoe UI', 'sans-serif'],
      },
      fontSize: {
        'h1': '3.5rem',
        'h2': '2.5rem',
        'h3': '1.8rem',
        'body': '1rem',
        'small': '0.9rem',
      },
      fontWeight: {
        normal: 400,
        medium: 600,
        bold: 700,
      },
      backdropFilter: {
        'blur': 'blur(10px)',
      },
    },
  },
  plugins: [],
}