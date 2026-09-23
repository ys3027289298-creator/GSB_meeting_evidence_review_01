/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        space: {
          dark: '#0f172a',
          blue: '#1e3a5f',
          accent: '#06b6d4',
        },
      },
    },
  },
  plugins: [],
};
