import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Import Tailwind CSS first so its styles take precedence
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
