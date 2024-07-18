/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      keyframes: {
        'background-pan': {
          '0%': { backgroundPosition: '0% center' },
          '100%': { backgroundPosition: '-200% center' },
        },
      },
      animation: {
        'background-pan': 'background-pan 10s linear infinite',
      },
      backgroundSize: {
        '200%': '200%',
      },
      colors: {
        g1: 'var(--g1)',
        g2: 'var(--g2)',
        black: '#222831',
        white: '#EEEEEE',
        orange: '#D65A31',
        gray: '#393E46'
      },
    },
  },
  plugins: [],
}