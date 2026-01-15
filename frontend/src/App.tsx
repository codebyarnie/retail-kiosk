import { useState } from 'react'
import './App.css'

/**
 * Main Application Component
 *
 * This is the root component of the Retail Kiosk application.
 * It will be expanded to include routing, state management, and
 * the main application layout.
 */

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <header className="App-header">
        <h1>Retail Kiosk</h1>
        <p>Modern Point-of-Sale System</p>
      </header>

      <main className="App-main">
        <div className="card">
          <button onClick={() => setCount((count) => count + 1)}>
            count is {count}
          </button>
          <p>
            Edit <code>src/App.tsx</code> and save to test HMR
          </p>
        </div>

        <div className="info">
          <p className="text-muted">
            Built with React + TypeScript + Vite
          </p>
        </div>
      </main>
    </div>
  )
}

export default App
