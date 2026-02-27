import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  // Get API URL from environment, default to localhost
  const apiUrl = env.VITE_API_URL || 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        // Proxy API requests to backend
        '/api': {
          target: apiUrl,
          changeOrigin: true,
          // Optional: rewrite path if needed
          // rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
        },
      },
    },
  }
})
