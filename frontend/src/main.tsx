import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

/**
 * Main entry point for the React application
 *
 * This file initializes the React root and mounts the main App component
 * to the DOM. It uses React 18's createRoot API for concurrent rendering.
 */

const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error(
    'Failed to find the root element. Make sure index.html has a div with id="root".'
  )
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
