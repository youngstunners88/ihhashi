import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Home as HomeIcon, ShoppingCart, User, MapPin, ChevronDown, Flame, Clock, Star } from 'lucide-react'
import { MerchantCard } from '../components/MerchantCard'
import { BlueHorseBadge } from '../components/BlueHorseBadge'

interface HomeProps {
  isAuthenticated: boolean
}

const categories = [
  { id: 'all', name: 'All', icon: '🔥' },
  { id: 'fast-food', name: 'Fast Food', icon: '🍔' },
  { id: 'groceries', name: 'Groceries', icon: '🛒' },
  { id: 'fresh', name: 'Fresh', icon: '🥬' },
  { id: 'courier', name: 'Courier', icon: '📦' },
]

const featuredMerchants = [
  { 
    id: '1', 
    name: 'Kota King', 
    category: 'Fast Food',
    description: 'Best kota in Soweto',
    rating: 4.8, 
    reviews: 256,
    deliveryTime: '25-35',
    deliveryFee: 15,
    image: 'https://placehold.co/400x300/FF6B35/white?text=Kota+King',
    verified: true,
    verificationLevel: 'premium' as const,
    distance: '1.2 km'
  },
  { 
    id: '2', 
    name: 'Fresh Market', 
    category: 'Fresh',
    description: 'Farm fresh produce daily',
    rating: 4.6, 
    reviews: 189,
    deliveryTime: '30-45',
    deliveryFee: 20,
    image: 'https://placehold.co/400x300/00A86B/white?text=Fresh+Market',
    verified: true,
    verificationLevel: 'verified' as const,
    distance: '2.1 km'
  },
  { 
    id: '3', 
    name: 'Soweto Kitchen', 
    category: 'Fast Food',
    description: 'Traditional SA cuisine',
    rating: 4.9, 
    reviews: 412,
    deliveryTime: '35-50',
    deliveryFee: 18,
    image: 'https://placehold.co/400x300/1A1A1A/FFD700?text=Soweto+Kitchen',
    verified: true,
    verificationLevel: 'premium' as const,
    distance: '0.8 km'
  },
]

const popularProducts = [
  { id: '1', name: 'Fresh Tomatoes', price: 25, unit: 'per kg', image: 'https://placehold.co/200x200/FF6B35/white?text=🍅', category: 'fresh' },
  { id: '2', name: 'Braai Pack', price: 120, unit: 'mixed', image: 'https://placehold.co/200x200/DC2626/white?text=🥩', category: 'fresh' },
  { id: '3', name: 'Pap & Vleis', price: 85, unit: 'meal', image: 'https://placehold.co/200x200/FCD34D/white?text=🍽️', category: 'fast-food' },
  { id: '4', name: 'Fresh Bread', price: 18, unit: 'loaf', image: 'https://placehold.co/200x200/FBBF24/white?text=🍞', category: 'groceries' },
]

export default function Home({ isAuthenticated }: HomeProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeCategory, setActiveCategory] = useState('all')

  return (
    <div className="min-h-screen bg-[#FFD700] pb-24">
      {/* Header */}
      <header className="bg-[#FFD700] sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-4 py-3">
          {/* Logo and Location */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              {/* Horse Logo */}
              <div className="w-10 h-10 bg-[#1A1A1A] rounded-xl flex items-center justify-center overflow-hidden">
                <img 
                  src="/assets/icon-small.jpg" 
                  alt="iHhashi"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none'
                  }}
                />
              </div>
              <div>
                <h1 className="font-bold text-lg text-[#1A1A1A]">iHhashi</h1>
                <p className="text-xs text-[#1A1A1A]/70">Delivering to</p>
              </div>
            </div>
            {/* Location */}
            <button className="flex items-center gap-1 bg-white/80 backdrop-blur px-3 py-1.5 rounded-full">
              <MapPin className="w-4 h-4 text-[#FF6B35]" />
              <span className="text-sm font-medium text-[#1A1A1A]">Soweto</span>
              <ChevronDown className="w-4 h-4 text-gray-500" />
            </button>
          </div>
          
          {/* Search Bar */}
          <div className="relative">
            <Search className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search food, groceries, fresh produce..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-11 pr-4 py-3 rounded-2xl bg-white border-0 shadow-sm text-base focus:ring-2 focus:ring-[#1A1A1A]/20 outline-none"
            />
          </div>
        </div>
      </header>

      {/* Categories */}
      <div className="bg-[#FFD700] px-4 py-3">
        <div className="max-w-lg mx-auto flex gap-2 overflow-x-auto scrollbar-hide pb-2">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`flex flex-col items-center gap-1 min-w-[72px] p-3 rounded-2xl transition-all ${
                activeCategory === cat.id
                  ? 'bg-[#1A1A1A] text-[#FFD700] shadow-lg'
                  : 'bg-white text-[#1A1A1A] shadow-sm'
              }`}
            >
              <span className="text-2xl">{cat.icon}</span>
              <span className="text-xs font-medium whitespace-nowrap">{cat.name}</span>
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
          
          {/* Badge */}
          <div className="relative z-10">
            <span className="inline-block bg-[#FFD700] text-[#1A1A1A] text-xs font-bold px-3 py-1 rounded-full mb-3">
              NEW
            </span>
            <h2 className="text-2xl font-bold text-white mb-1">
              Empty Fridge?
            </h2>
            <h3 className="text-3xl font-bold text-[#FFD700] mb-2">
              Full feast!
            </h3>
            <p className="text-white/80 text-sm mb-1">
              iHhashi delivers from local favorites.
            </p>
            <p className="text-[#FFD700] text-sm font-semibold flex items-center gap-1">
              <Flame className="w-4 h-4" />
              Free delivery on first order
            </p>
          </div>
        </div>
      </div>

      {/* Verified Merchants */}
      <div className="bg-[#FFFBEB] rounded-t-3xl min-h-[300px]">
        <div className="max-w-lg mx-auto px-4 pt-6">
          {/* Section Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <BlueHorseBadge level="verified" size="sm" showLabel={false} />
              <h3 className="font-bold text-lg text-[#1A1A1A]">Verified Merchants</h3>
            </div>
            <Link to="/products" className="text-[#FF6B35] text-sm font-semibold">
              See all →
            </Link>
          </div>
          
          {/* Featured Merchant Cards */}
          <div className="space-y-4 mb-6">
            {featuredMerchants.map((merchant) => (
              <MerchantCard key={merchant.id} merchant={merchant} variant="featured" />
            ))}
          </div>

          {/* Popular Near You */}
          <div className="flex justify-between items-center mb-4 mt-6">
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

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-3 mt-6 mb-4">
            <div className="bg-white rounded-xl p-3 text-center shadow-sm">
              <Clock className="w-5 h-5 mx-auto mb-1 text-[#FF6B35]" />
              <p className="text-lg font-bold text-[#1A1A1A]">25min</p>
              <p className="text-xs text-gray-500">Avg delivery</p>
            </div>
            <div className="bg-white rounded-xl p-3 text-center shadow-sm">
              <Star className="w-5 h-5 mx-auto mb-1 text-yellow-500" />
              <p className="text-lg font-bold text-[#1A1A1A]">4.8</p>
              <p className="text-xs text-gray-500">Rating</p>
            </div>
            <div className="bg-white rounded-xl p-3 text-center shadow-sm">
              <MapPin className="w-5 h-5 mx-auto mb-1 text-green-500" />
              <p className="text-lg font-bold text-[#1A1A1A]">50+</p>
              <p className="text-xs text-gray-500">Merchants</p>
            </div>
          </div>

          {/* Become a Rider CTA */}
          <div className="bg-[#1A1A1A] rounded-2xl p-4 mb-6">
            <div className="flex items-center gap-4">
              <img 
                src="/assets/transport-motorbike.jpg" 
                alt="Become a rider"
                className="w-20 h-20 object-cover rounded-xl"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://placehold.co/100x100/FFD700/1A1A1A?text=🐴'
                }}
              />
              <div className="flex-1">
                <h4 className="font-bold text-white">Become a Delivery Hero</h4>
                <p className="text-white/70 text-sm">Earn up to R500/day delivering with iHhashi</p>
              </div>
            </div>
            <button className="mt-3 w-full bg-[#FFD700] text-[#1A1A1A] py-3 rounded-xl font-bold text-sm hover:bg-[#FFC700] transition-colors">
              Sign Up Now
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 py-2 px-4 shadow-lg">
        <div className="max-w-lg mx-auto flex justify-around">
          <Link to="/" className="flex flex-col items-center py-1 px-3">
            <div className="w-10 h-10 rounded-xl bg-[#FFD700] flex items-center justify-center">
              <HomeIcon className="w-5 h-5 text-[#1A1A1A]" />
            </div>
            <span className="text-xs mt-1 font-semibold text-[#1A1A1A]">Home</span>
          </Link>
          <Link to="/products" className="flex flex-col items-center py-1 px-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center">
              <Search className="w-5 h-5 text-gray-400" />
            </div>
            <span className="text-xs mt-1 text-gray-500">Search</span>
          </Link>
          <Link to="/orders" className="flex flex-col items-center py-1 px-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center relative">
              <ShoppingCart className="w-5 h-5 text-gray-400" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-[#FF6B35] text-white text-xs rounded-full flex items-center justify-center font-bold">
                2
              </span>
            </div>
            <span className="text-xs mt-1 text-gray-500">Orders</span>
          </Link>
          <Link to={isAuthenticated ? "/profile" : "/auth"} className="flex flex-col items-center py-1 px-3">
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
