import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Home as HomeIcon, ShoppingCart, User, MapPin, ChevronDown } from 'lucide-react'

interface HomeProps {
  isAuthenticated: boolean
}

const categories = [
  { id: 'all', name: 'All', icon: '🛒' },
  { id: 'fast-food', name: 'Fast Food', icon: '🍔' },
  { id: 'groceries', name: 'Groceries', icon: '🥬' },
  { id: 'fresh', name: 'Fresh', icon: '🍎' },
]

const popularProducts = [
  { id: '1', name: 'Fresh Tomatoes', price: 25, unit: 'per kg', image: 'https://placehold.co/200x200/FF6B35/white?text=🍅', category: 'fresh' },
  { id: '2', name: 'Braai Pack', price: 120, unit: 'mixed', image: 'https://placehold.co/200x200/DC2626/white?text=🥩', category: 'fresh' },
  { id: '3', name: 'Pap & Vleis Combo', price: 85, unit: 'meal', image: 'https://placehold.co/200x200/FCD34D/white?text=🍽️', category: 'fast-food' },
  { id: '4', name: 'Fresh Bread', price: 18, unit: 'loaf', image: 'https://placehold.co/200x200/FBBF24/white?text=🍞', category: 'groceries' },
]

export default function Home({ isAuthenticated }: HomeProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeCategory, setActiveCategory] = useState('all')

  return (
    <div className="min-h-screen bg-[#FFD700] pb-20">
      {/* Header */}
      <header className="bg-[#FFD700] sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-4 py-3">
          {/* Logo and Location */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              {/* Horse Logo */}
              <div className="w-10 h-10 bg-[#1A1A1A] rounded-xl flex items-center justify-center">
                <span className="text-[#FFD700] text-xl">🐴</span>
              </div>
              <div>
                <h1 className="font-bold text-lg text-[#1A1A1A]">iHhashi</h1>
              </div>
            </div>
            {/* Location */}
            <button className="flex items-center gap-1 bg-white/80 px-3 py-1.5 rounded-full">
              <MapPin className="w-4 h-4 text-[#FF6B35]" />
              <span className="text-sm font-medium text-[#1A1A1A]">Soweto, Johann...</span>
              <ChevronDown className="w-4 h-4 text-gray-500" />
            </button>
          </div>
          
          {/* Search Bar */}
          <div className="relative">
            <Search className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search for food, groceries, fresh produce..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-11 pr-4 py-3 rounded-2xl bg-white border-0 shadow-sm text-base focus:ring-2 focus:ring-[#1A1A1A]/20 outline-none"
            />
          </div>
        </div>
      </header>

      {/* Categories */}
      <div className="bg-[#FFD700] px-4 py-3">
        <div className="max-w-lg mx-auto flex gap-2 overflow-x-auto scrollbar-hide">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full whitespace-nowrap transition-all font-medium ${
                activeCategory === cat.id
                  ? 'bg-[#1A1A1A] text-[#FFD700]'
                  : 'bg-white text-[#1A1A1A] shadow-sm'
              }`}
            >
              <span>{cat.icon}</span>
              <span>{cat.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Hero Banner */}
      <div className="px-4 pb-4">
        <div className="max-w-lg mx-auto bg-[#1A1A1A] rounded-3xl p-5 relative overflow-hidden">
          {/* Decorative elements */}
          <div className="absolute -right-8 -top-8 w-32 h-32 bg-[#FFD700]/10 rounded-full" />
          <div className="absolute -left-4 -bottom-4 w-24 h-24 bg-[#FF6B35]/20 rounded-full" />
          
          <div className="relative z-10">
            <h2 className="text-2xl font-bold text-white mb-1">
              Empty Fridge?
            </h2>
            <h3 className="text-3xl font-bold text-[#FFD700] mb-2">
              Full feast!
            </h3>
            <p className="text-white/80 text-sm mb-1">
              iHhashi delivers.
            </p>
            <p className="text-[#FFD700] text-sm font-semibold">
              🚀 Free delivery on first order
            </p>
          </div>
        </div>
      </div>

      {/* Popular Near You */}
      <div className="bg-[#FFFBEB] rounded-t-3xl min-h-[300px]">
        <div className="max-w-lg mx-auto px-4 pt-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-bold text-lg text-[#1A1A1A]">Popular Near You</h3>
            <Link to="/products" className="text-[#FF6B35] text-sm font-semibold">
              See all →
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {popularProducts.map((product) => (
              <Link
                key={product.id}
                to={`/products/${product.category}`}
                className="bg-white rounded-2xl p-3 shadow-sm border border-[#F5E6B8] hover:shadow-md transition-all active:scale-[0.98]"
              >
                <img
                  src={product.image}
                  alt={product.name}
                  className="w-full aspect-square object-cover rounded-xl mb-2 bg-[#FEF3C7]"
                />
                <h4 className="font-semibold text-sm text-[#1A1A1A] line-clamp-1">{product.name}</h4>
                <p className="text-xs text-gray-500 mb-1">{product.unit}</p>
                <div className="flex justify-between items-center">
                  <span className="font-bold text-[#FF6B35]">R{product.price}</span>
                  <button className="bg-[#1A1A1A] text-[#FFD700] text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-[#333] active:scale-95 transition-all">
                    Add
                  </button>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 py-2 px-4 shadow-lg">
        <div className="max-w-lg mx-auto flex justify-around">
          <Link to="/" className="flex flex-col items-center py-1">
            <div className="w-10 h-10 rounded-xl bg-[#FFD700] flex items-center justify-center">
              <HomeIcon className="w-5 h-5 text-[#1A1A1A]" />
            </div>
            <span className="text-xs mt-1 font-semibold text-[#1A1A1A]">Home</span>
          </Link>
          <Link to="/products" className="flex flex-col items-center py-1">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center">
              <Search className="w-5 h-5 text-gray-400" />
            </div>
            <span className="text-xs mt-1 text-gray-500">Search</span>
          </Link>
          <Link to="/orders" className="flex flex-col items-center py-1">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center relative">
              <ShoppingCart className="w-5 h-5 text-gray-400" />
            </div>
            <span className="text-xs mt-1 text-gray-500">Orders</span>
          </Link>
          <Link to={isAuthenticated ? "/profile" : "/auth"} className="flex flex-col items-center py-1">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center">
              <User className="w-5 h-5 text-gray-400" />
            </div>
            <span className="text-xs mt-1 text-gray-500">Profile</span>
          </Link>
        </div>
      </nav>
    </div>
  )
}
