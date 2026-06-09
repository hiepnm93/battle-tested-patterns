import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    include: ['__tests__/**/*.test.ts'],
    globals: true,
    setupFiles: ['__tests__/setup.ts'],
  },
  resolve: {
    alias: {
      vitepress: resolve(__dirname, '__tests__/mocks/vitepress.ts'),
    },
  },
});
