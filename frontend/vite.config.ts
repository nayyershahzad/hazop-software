import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  css: {
    // CSS modules configuration
    modules: {
      localsConvention: 'camelCase',
    }
  },
  resolve: {
    alias: {
      // Add an alias for source directory
      '@': resolve(__dirname, 'src'),
      // Keep the PDF styles alias
      '@pdf-styles': resolve(__dirname, 'src/pdf-styles.css')
    }
  }
})