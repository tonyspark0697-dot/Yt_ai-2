/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0f1115',
        card: '#181b22',
        line: '#272c38',
        text: '#eef0f4',
        mut: '#8b93a3',
        acc: '#ff3b47',
        ok: '#2ecc71',
        warn: '#f5a623',
      }
    },
  },
  plugins: [],
}
