import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, ShoppingCart, Menu, User } from 'lucide-react'

interface HomeProps {
  isAuthenticated: boolean
}

const categories = [
  { id: 'utensils', name: 'Utensils', icon: '🍴', color: 'bg-orange-100' },
  { id: 'stationery', name: 'Stationery', icon: '📝', color: 'bg-blue-100' },
  { id: 'household', name: 'Household', icon: '🏠', color: 'bg-green-100' },
  { id: 'electronics', name: 'Electronics', icon: '📱', color: 'bg-purple-100' },
  { id: 'groceries', name: 'Groceries', icon: '🛒', color: 'bg-yellow-100' },
]

const popularProducts = [
  { id: '1', name: 'Stainless Steel Spork', price: 45, category: 'utensils', image: 'https://placehold.co/200x200/FF6B35/white?text=Spork' },
  { id: '2', name: 'Bic Ballpoint Pens (10pk)', price: 35, category: 'stationery', image: 'https://placehold.co/200x200/3B82F6/white?text=Pens' },
  { id: '3', name: 'Kitchen Towels (3pk)', price: 55, category: 'household', image: 'https://placehold.co/200x200/10B981/white?text=Towels' },
  { id: '4', name: 'USB Charging Cable', price: 89, category: 'electronics', image: 'https://placehold.co/200x200/8B5CF6/white?text=Cable' },
]

export default function Home({ isAuthenticated }: HomeProps) {
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-4 py-3 flex items-center gap-3">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search utensils, stationery..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10"
            />
          </div>
          <Link to="/cart" className="relative">
            <ShoppingCart className="w-6 h-6 text-gray-600" />
          </Link>
          {isAuthenticated ? (
            <Link to="/profile" className="text-sm font-medium text-gray-600 hover:text-gray-900">
              Profile
            </Link>
          ) : (
            <Link to="/auth" className="text-sm font-medium text-[#FF6B35]">
              Sign In
            </Link>
          )}
        </div>
      </header>

      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-[#FF6B35] to-[#FF8B5A] text-white p-6 mx-4 mt-4 rounded-2xl">
        <h2 className="text-xl font-bold mb-2">Fast delivery, everyday essentials</h2>
        <p className="text-white/90 text-sm mb-3">
          Utensils, stationery, and household items delivered in 30-45 minutes
        </p>
        <Link to="/products" className="inline-block bg-white text-[#FF6B35] font-semibold px-4 py-2 rounded-lg text-sm">
          Start Shopping
        </Link>
      </div>

      {/* Categories */}
      <div className="max-w-lg mx-auto px-4 mt-6">
        <h3 className="font-bold text-lg mb-3">Categories</h3>
        <div className="grid grid-cols-5 gap-2">
          {categories.map((cat) => (
            <Link
              key={cat.id}
              to={`/products/${cat.id}`}
              className="flex flex-col items-center"
            >
              <div className={`${cat.color} w-14 h-14 rounded-xl flex items-center justify-center text-2xl mb-1`}>
                {cat.icon}
              </div>
              <span className="text-xs text-center">{cat.name}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* Popular Products */}
      <div className="max-w-lg mx-auto px-4 mt-6">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-bold text-lg">Popular Near You</h3>
          <Link to="/products" className="text-[#FF6B35] text-sm font-medium">See all</Link>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {popularProducts.map((product) => (
            <div key={product.id} className="card">
              <img src={product.image} alt={product.name} className="w-full aspect-square object-cover rounded-lg mb-2" />
              <h4 className="font-medium text-sm line-clamp-2">{product.name}</h4>
              <div className="flex justify-between items-center mt-2">
                <span className="font-bold text-[#FF6B35]">R{product.price}</span>
                <button className="bg-[#FF6B35] text-white text-xs px-3 py-1.5 rounded-lg">
                  Add
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 py-2">
        <div className="max-w-lg mx-auto flex justify-around">
          <Link to="/" className="flex flex-col items-center text-[#FF6B35]">
            <Menu className="w-6 h-6" />
            <span className="text-xs mt-1">Home</span>
          </Link>
          <Link to="/products" className="flex flex-col items-center text-gray-400">
            <Search className="w-6 h-6" />
            <span className="text-xs mt-1">Browse</span>
          </Link>
          <Link to="/orders" className="flex flex-col items-center text-gray-400">
            <ShoppingCart className="w-6 h-6" />
            <span className="text-xs mt-1">Orders</span>
          </Link>
          <Link to={isAuthenticated ? "/profile" : "/auth"} className="flex flex-col items-center text-gray-400">
            <User className="w-6 h-6" />
            <span className="text-xs mt-1">Profile</span>
          </Link>
        </div>
      </nav>
    </div>
  )
}