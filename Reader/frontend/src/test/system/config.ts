import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/test/system/**/*.test.ts'],
    exclude: ['node_modules', 'dist'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.d.ts',
        '**/*.test.ts',
        '**/*.spec.ts',
        '**/__tests__/**',
        '**/__mocks__/**'
      ]
    },
    deps: {
      inline: ['@vue', '@vueuse']
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../../src')
    }
  }
}) 