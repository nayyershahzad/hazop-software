import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Removed splitVendorChunkPlugin as it's not available in this Vite version
  ],
  build: {
    target: 'es2018',
    minify: 'esbuild', // Use esbuild for faster builds
    sourcemap: false, // Disable sourcemaps in production for smaller files
    reportCompressedSize: false, // Speed up build by skipping gzipped size calculation
    chunkSizeWarningLimit: 1000, // Increase the warning limit
    rollupOptions: {
      output: {
        // Simple chunking strategy
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  },
  // Remove complex CSS processing to fix build issues
  resolve: {
    alias: {
      // Add an alias for source directory
      '@': resolve(__dirname, 'src'),
      // Keep the PDF styles alias
      '@pdf-styles': resolve(__dirname, 'src/pdf-styles.css'),
      // Add common component directories
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@api': resolve(__dirname, 'src/api'),
    }
  },
  // Optimize dev server
  server: {
    hmr: {
      overlay: true, // Show errors as overlay
    },
    headers: {
      'Cache-Control': 'no-store',
    },
  },
  // Optimize preview server
  preview: {
    headers: {
      'Cache-Control': 'max-age=31536000', // Cache static assets for 1 year
    },
  },
})