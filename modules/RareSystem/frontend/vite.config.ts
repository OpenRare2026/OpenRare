import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    // Loopback by default — the dev server proxies /api to the backend,
    // so exposing it on the LAN exposes patient data with it. Override with
    // `vite --host 0.0.0.0` when you deliberately need remote access.
    host: '127.0.0.1',
    port: 8888,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
      },
    },
  },
})
