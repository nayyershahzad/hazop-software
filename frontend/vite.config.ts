import { defineConfig, splitVendorChunkPlugin } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    splitVendorChunkPlugin(), // Split vendor chunks for better caching
  ],
  build: {
    target: 'es2018',
    minify: 'terser', // Use terser for better minification
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          // Split large dependencies into separate chunks
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'pdf-viewer': ['react-pdf', 'pdfjs-dist'],
          'data-viz': ['recharts', 'chart.js'],
          'utils': ['axios', 'date-fns', 'uuid'],
          'ui-framework': ['tailwindcss']
        },
        // Improve chunking strategy
        chunkFileNames: (chunkInfo) => {
          const name = chunkInfo.name;
          if (name === 'vendor') return 'vendor-[hash].js';
          return '[name]-[hash].js';
        },
      },
    },
    chunkSizeWarningLimit: 1000, // Increase the warning limit
    sourcemap: false, // Disable sourcemaps in production for smaller files
    // Enable brotli compression for even smaller files
    reportCompressedSize: false, // Speed up build by skipping gzipped size calculation
  },
  css: {
    // CSS modules configuration
    modules: {
      localsConvention: 'camelCase',
    },
    // Optimize CSS
    postcss: {
      plugins: [
        require('autoprefixer'),
        require('cssnano')({
          preset: ['default', {
            discardComments: { removeAll: true },
          }],
        }),
      ],
    },
  },
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