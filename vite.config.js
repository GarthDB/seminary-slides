import { defineConfig } from 'vite'
import { githubPagesSpa } from '@sctg/vite-plugin-github-pages-spa'

export default defineConfig({
  plugins: [
    githubPagesSpa({
      verbose: false, // Set to true for debugging
    }),
  ],
})


