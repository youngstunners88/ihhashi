import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import * as Sentry from '@sentry/react'

import Home from './pages/Home'
import Auth from './pages/auth/Auth'
import Products from './pages/catalog/Products'
import { CartPage } from './pages/CartPage'
import Orders from './pages/orders/Orders'
import Profile from './pages/profile/Profile'
import ErrorBoundary from './components/common/ErrorBoundary'
import SplashScreen from './components/SplashScreen'

// Initialize GlitchTip (Sentry-compatible error tracking)
const GLITCHTIP_DSN = import.meta.env.VITE_GLITCHTIP_DSN || 'https://25a5585d096a411495f93126742fbf73@app.glitchtip.com/20760'

if (GLITCHTIP_DSN) {
  Sentry.init({
    dsn: GLITCHTIP_DSN,
    tracesSampleRate: 0.2,
    environment: import.meta.env.MODE || 'development',
  })
}

const queryClient = new QueryClient()

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showSplash, setShowSplash] = useState(true)

  useEffect(() => {
    // Show splash screen for 2 seconds with logo
    const timer = setTimeout(() => setShowSplash(false), 2000)
    return () => clearTimeout(timer)
  }, [])

  if (showSplash) {
    return <SplashScreen />
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home isAuthenticated={isAuthenticated} />} />
            <Route path="/auth" element={<Auth onAuth={() => setIsAuthenticated(true)} />} />
            <Route path="/products" element={<Products />} />
            <Route path="/products/:category" element={<Products />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/orders/:id" element={<Orders />} />
            <Route 
              path="/profile" 
              element={isAuthenticated ? <Profile /> : <Navigate to="/auth" />} 
            />
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App