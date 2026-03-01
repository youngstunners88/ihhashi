import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, ShoppingCart, Home as HomeIcon, Clock, User, Star, ChevronRight } from 'lucide-react'
import { useAuth } from '../App'

const categories = [
  { id: 'food', name: 'Food', icon: '🍔', color: 'bg-orange-100' },
  { id: 'groceries', name: 'Groceries', icon: '🛒', color: 'bg-green-100' },
  { id: 'fruits', name: 'Fruits', icon: '🍎', color: 'bg-red-100' },
  { id: 'vegetables', name: 'Veggies', icon: '🥬', color: 'bg-emerald-100' },
  { id: 'dairy', name: 'Dairy', icon: '🥛', color: 'bg-blue-100' },
]

const popularMerchants = [
  { id: '1', name: 'KFC Rosebank', rating: 4.8, reviews: 234, deliveryTime: '20-30', deliveryFee: 15, image: 'https://placehold.co/200x120/FFD700/1A1A1A?text=KFC', category: 'Fast Food' },
  { id: '2', name: 'Fresh Market', rating: 4.6, reviews: 189, deliveryTime: '30-45', deliveryFee: 20, image: 'https://placehold.co/200x120/22C55E/white?text=Fresh', category: 'Groceries' },
  { id: '3', name: 'Fruit Republic', rating: 4.9, reviews: 156, deliveryTime: '25-35', deliveryFee: 12, image: 'https://placehold.co/200x120/EF4444/white?text=Fruit', category: 'Fruits' },
  { id: '4', name: 'Veggie King', rating: 4.7, reviews: 98, deliveryTime: '35-50', deliveryFee: 18, image: 'https://placehold.co/200x120/10B981/white?text=Veggie', category: 'Vegetables' },
]

const featuredProducts = [
  { id: '1', name: 'Chicken Bucket (8pc)', price: 149, merchant: 'KFC Rosebank', image: 'https://placehold.co/200x200/FFD700/1A1A1A?text=🍗' },
  { id: '2', name: 'Fresh Apples (1kg)', price: 35, merchant: 'Fruit Republic', image: 'https://placehold.co/200x200/EF4444/white?text=🍎' },
  { id: '3', name: 'Full Cream Milk (2L)', price: 42, merchant: 'Fresh Market', image: 'https://placehold.co/200x200/3B82F6/white?text=🥛' },
  { id: '4', name: 'Mixed Veggies Pack', price: 55, merchant: 'Veggie King', image: 'https://placehold.co/200x200/10B981/white?text=🥬' },
]

export default function Home() {
  const { isAuthenticated } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <header className="bg-secondary-600 text-white sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-secondary-600 font-bold text-sm">H</span>
              </div>
              <span className="font-bold text-lg">iHhashi</span>
            </div>
            <Link to={isAuthenticated ? "/profile" : "/auth"} className="text-sm font-medium text-primary hover:text-primary-400 transition-colors">
              {isAuthenticated ? "Profile" : "Sign In"}
            </Link>
          </div>
          <div className="relative">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search food, groceries, fruits..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white text-secondary-600 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary shadow-sm"
            />
          </div>
        </div>
      </header>

      {/* Hero Banner */}
      <div className="max-w-lg mx-auto px-4 mt-4">
        <div className="bg-gradient-to-r from-primary to-primary-400 text-secondary-600 p-5 rounded-2xl shadow-card">
          <h2 className="text-lg font-bold mb-1">Fast delivery in 30-45 mins</h2>
          <p className="text-secondary-500 text-sm mb-3">
            Food, groceries, fruits & vegetables delivered fresh
          </p>
          <Link 
            to="/products" 
            className="inline-flex items-center gap-2 bg-secondary-600 text-primary font-semibold px-4 py-2 rounded-xl text-sm hover:bg-secondary-700 transition-colors"
          >
            Start Shopping
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* Categories */}
      <div className="max-w-lg mx-auto px-4 mt-6">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-bold text-lg text-secondary-600">Categories</h3>
          <Link to="/products" className="text-primary text-sm font-medium hover:text-primary-600 transition-colors">
            See all
          </Link>
        </div>
        <div className="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
          {categories.map((cat) => (
            <Link
              key={cat.id}
              to={`/products/${cat.id}`}
              className="flex flex-col items-center min-w-[70px]"
            >
              <div className={`${cat.color} w-14 h-14 rounded-2xl flex items-center justify-center text-2xl mb-1.5 shadow-sm`}>
                {cat.icon}
              </div>
              <span className="text-xs text-secondary-500 font-medium">{cat.name}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* Popular Merchants */}
      <div className="max-w-lg mx-auto px-4 mt-6">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-bold text-lg text-secondary-600">Popular Near You</h3>
          <Link to="/merchants" className="text-primary text-sm font-medium hover:text-primary-600 transition-colors">
            See all
          </Link>
        </div>
        <div className="space-y-3">
          {popularMerchants.map((merchant) => (
            <Link
              key={merchant.id}
              to={`/merchant/${merchant.id}`}
              className="block bg-white rounded-2xl shadow-card hover:shadow-card-hover transition-shadow overflow-hidden"
            >
              <div className="flex">
                <img 
                  src={merchant.image} 
                  alt={merchant.name} 
                  className="w-28 h-24 object-cover" 
                />
                <div className="flex-1 p-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-secondary-600">{merchant.name}</h4>
                      <p className="text-xs text-secondary-400">{merchant.category}</p>
                    </div>
                    <div className="flex items-center gap-1 bg-primary-100 px-2 py-0.5 rounded-full">
                      <Star className="w-3 h-3 text-primary fill-primary" />
                      <span className="text-xs font-medium text-secondary-600">{merchant.rating}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 mt-2 text-xs text-secondary-400">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>{merchant.deliveryTime} min</span>
                    </div>
                    <span>•</span>
                    <span>R{merchant.deliveryFee} delivery</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Featured Products */}
      <div className="max-w-lg mx-auto px-4 mt-6">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-bold text-lg text-secondary-600">Featured Items</h3>
          <Link to="/products" className="text-primary text-sm font-medium hover:text-primary-600 transition-colors">
            See all
          </Link>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {featuredProducts.map((product) => (
            <div 
              key={product.id} 
              className="bg-white rounded-2xl shadow-card hover:shadow-card-hover transition-shadow overflow-hidden"
            >
              <img 
                src={product.image} 
                alt={product.name} 
                className="w-full aspect-square object-cover" 
              />
              <div className="p-3">
                <h4 className="font-medium text-sm text-secondary-600 line-clamp-1">{product.name}</h4>
                <p className="text-xs text-secondary-400 mt-0.5">{product.merchant}</p>
                <div className="flex justify-between items-center mt-2">
                  <span className="font-bold text-primary">R{product.price}</span>
                  <button className="bg-secondary-600 text-primary text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-secondary-700 transition-colors">
                    Add
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 py-2 z-50">
        <div className="max-w-lg mx-auto flex justify-around">
          <Link to="/" className="flex flex-col items-center py-1 px-4">
            <HomeIcon className="w-6 h-6 text-primary" />
            <span className="text-xs mt-1 font-medium text-primary">Home</span>
          </Link>
          <Link to="/products" className="flex flex-col items-center py-1 px-4">
            <Search className="w-6 h-6 text-secondary-400" />
            <span className="text-xs mt-1 text-secondary-400">Browse</span>
          </Link>
          <Link to="/orders" className="flex flex-col items-center py-1 px-4">
            <ShoppingCart className="w-6 h-6 text-secondary-400" />
            <span className="text-xs mt-1 text-secondary-400">Orders</span>
          </Link>
          <Link to={isAuthenticated ? "/profile" : "/auth"} className="flex flex-col items-center py-1 px-4">
            <User className="w-6 h-6 text-secondary-400" />
            <span className="text-xs mt-1 text-secondary-400">Profile</span>
          </Link>
        </div>
      </nav>
    </div>
  )
}