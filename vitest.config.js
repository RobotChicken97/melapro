// eslint-disable-next-line import/no-unresolved
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    coverage: {
      provider: 'v8',
      include: ['src/lib/utils.js'],
      reporter: ['text', 'lcov'],
      lines: 100,
      functions: 100,
      branches: 100,
      statements: 100,
      enabled: true,
    },
  },
})
