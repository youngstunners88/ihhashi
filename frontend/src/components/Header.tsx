import { useState } from 'react'
import { Bell, ShoppingCart, Menu, X, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'

interface HeaderProps {
  showCart?: boolean
  cartCount?: number
}

export function Header({ showCart = false, cartCount = 0 }: HeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <>
      <header className="bg-black sticky top-0 z-50 shadow-kasi">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
              <Zap className="w-6 h-6 text-black fill-black animate-zap-pulse" />
            </div>
            <span className="font-black text-xl tracking-tight text-primary uppercase">
              IHHASHI
            </span>
          </Link>

          {/* Actions */}
          <div className="flex items-center gap-3">
            {showCart && (
              <Link to="/cart" className="relative p-2 hover:bg-white/10 rounded-full transition-colors">
                <ShoppingCart className="w-5 h-5 text-primary" />
                {cartCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-primary text-black text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">
                    {cartCount}
                  </span>
                )}
              </Link>
            )}

            <button className="relative p-2 hover:bg-white/10 rounded-full transition-colors">
              <Bell className="w-5 h-5 text-primary" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
            >
              {isMenuOpen ? (
                <X className="w-5 h-5 text-primary" />
              ) : (
                <Menu className="w-5 h-5 text-primary" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="bg-black border-t border-primary/20 px-4 py-4 md:hidden animate-slide-down">
            <nav className="space-y-1">
              <Link to="/orders" className="block text-primary hover:text-white hover:bg-white/10 py-3 px-3 rounded-lg transition-colors font-semibold">
                My Orders
              </Link>
              <Link to="/profile" className="block text-primary hover:text-white hover:bg-white/10 py-3 px-3 rounded-lg transition-colors font-semibold">
                Profile
              </Link>
              <Link to="/rider" className="block text-primary hover:text-white hover:bg-white/10 py-3 px-3 rounded-lg transition-colors font-semibold">
                Become a Rider
              </Link>
              <Link to="/merchant-dashboard" className="block text-primary hover:text-white hover:bg-white/10 py-3 px-3 rounded-lg transition-colors font-semibold">
                Merchant Portal
              </Link>
              <hr className="my-2 border-primary/20" />
              <Link to="/auth" className="block text-red-400 hover:bg-red-500/10 py-3 px-3 rounded-lg transition-colors font-semibold">
                Sign Out
              </Link>
            </nav>
          </div>
        )}
      </header>
    </>
  )
}
