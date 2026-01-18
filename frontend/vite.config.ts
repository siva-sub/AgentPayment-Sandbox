import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  // Base path for GitHub Pages (set to repo name)
  base: process.env.NODE_ENV === 'production' ? '/AgentPayment-Sandbox/' : '/',
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/mock': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})
