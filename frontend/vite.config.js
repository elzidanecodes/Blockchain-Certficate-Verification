import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Ambil cert dan key
const key = fs.readFileSync(path.resolve(__dirname, '../backend/keys/key.pem'))
const cert = fs.readFileSync(path.resolve(__dirname, '../backend/keys/cert.pem'))

export default defineConfig({
  plugins: [react()],
  server: {
    https: {
      key,
      cert
    },
    port: 5173
  }
})
