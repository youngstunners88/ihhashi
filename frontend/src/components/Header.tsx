import { useState } from 'react'
import { Menu, Bell, ShoppingCart } from 'lucide-react'

interface HeaderProps {
  showCart?: boolean
  cartCount?: number
}

export function Header({ showCart = false, cartCount = 0 }: HeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">H</span>
          </div>
          <span className="font-bold text-xl text-gray-800">iHhashi</span>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-4">
          {showCart && (
            <button className="relative">
              <ShoppingCart className="w-6 h-6 text-gray-600" />
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-primary-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </button>
          )}
          
          <button className="relative">
            <Bell className="w-6 h-6 text-gray-600" />
            <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full" />
          </button>
          
          <button onClick={() => setIsMenuOpen(!isMenuOpen)}>
            <Menu className="w-6 h-6 text-gray-600" />
          </button>
        </div>
      </div>
      
      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="bg-white border-t px-4 py-3 md:hidden">
          <nav className="space-y-3">
            <a href="/orders" className="block text-gray-700 py-2">My Orders</a>
            <a href="/profile" className="block text-gray-700 py-2">Profile</a>
            <a href="/rider" className="block text-gray-700 py-2">Become a Rider</a>
            <a href="/merchant-dashboard" className="block text-gray-700 py-2">Merchant Portal</a>
            <hr />
            <a href="#" className="block text-red-500 py-2">Sign Out</a>
          </nav>
        </div>
      )}
    </header>
  )
}
