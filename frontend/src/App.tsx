import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

import Home from './pages/Home'
import Auth from './pages/auth/Auth'
import Products from './pages/catalog/Products'
import { CartPage } from './pages/CartPage'
import Orders from './pages/orders/Orders'
import Profile from './pages/profile/Profile'

const queryClient = new QueryClient()

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  return (
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
  )
}

export default App