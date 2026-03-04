import { useState } from 'react'
import { 
  MapPin, Clock, DollarSign, Star, Bike, Car, 
  User, Settings, Wallet, History, Power, ChevronRight,
  TrendingUp, Package, Navigation, Phone, CheckCircle
} from 'lucide-react'
import { BlueHorseBadge, VerificationProgress } from '../components/BlueHorseBadge'

// Transport options with images
const transportOptions = [
  {
    id: 'walking',
    name: 'Walking',
    description: 'On foot delivery',
    image: '/assets/transport-walking.jpg',
    maxDistance: '2 km',
    baseRate: 15,
    perKmRate: 5,
    color: 'bg-green-100 border-green-300'
  },
  {
    id: 'skateboard',
    name: 'Skateboard',
    description: 'Skateboard delivery',
    image: '/assets/transport-skateboard.jpg',
    maxDistance: '5 km',
    baseRate: 18,
    perKmRate: 4,
    color: 'bg-purple-100 border-purple-300'
  },
  {
    id: 'bicycle',
    name: 'Bicycle',
    description: 'Eco-friendly cycling',
    image: '/assets/transport-bicycle.jpg',
    maxDistance: '10 km',
    baseRate: 20,
    perKmRate: 3,
    color: 'bg-blue-100 border-blue-300'
  },
  {
    id: 'motorbike',
    name: 'Motorbike',
    description: 'Fast delivery',
    image: '/assets/transport-motorbike.jpg',
    maxDistance: '25 km',
    baseRate: 30,
    perKmRate: 5,
    color: 'bg-orange-100 border-orange-300'
  },
  {
    id: 'car',
    name: 'Car',
    description: 'Large orders & bulk',
    image: '/assets/transport-motorbike.jpg', // Reuse for now
    maxDistance: '50 km',
    baseRate: 50,
    perKmRate: 8,
    color: 'bg-red-100 border-red-300'
  }
]

// Mock stats
const riderStats = {
  rating: 4.8,
  totalDeliveries: 156,
  earningsThisWeek: 2840,
  earningsToday: 340,
  onlineHours: 6.5,
  acceptanceRate: 94
}

// Mock active order
const activeOrder = {
  id: 'ORD-12345',
  status: 'picked_up',
  merchant: 'Soweto Kitchen',
  customer: 'John M.',
  address: '123 Vilakazi St, Soweto',
  distance: 2.3,
  items: 3,
  total: 185,
  estimatedTime: 12
}

export function RiderDashboard() {
  const [selectedTransport, setSelectedTransport] = useState('motorbike')
  const [isOnline, setIsOnline] = useState(true)
  const [activeTab, setActiveTab] = useState('home')

  const currentTransport = transportOptions.find(t => t.id === selectedTransport)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-[#FFD700] px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-12 h-12 bg-[#1A1A1A] rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-[#FFD700]" />
                </div>
                <div className={`absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-white ${isOnline ? 'bg-green-500' : 'bg-gray-400'}`} />
              </div>
              <div>
                <h1 className="font-bold text-[#1A1A1A]">Welcome back!</h1>
                <div className="flex items-center gap-1">
                  <Star className="w-3 h-3 text-[#1A1A1A] fill-current" />
                  <span className="text-sm font-medium text-[#1A1A1A]">{riderStats.rating}</span>
                </div>
              </div>
            </div>
            
            {/* Online Toggle */}
            <button
              onClick={() => setIsOnline(!isOnline)}
              className={`px-4 py-2 rounded-full font-semibold text-sm transition-all ${
                isOnline 
                  ? 'bg-green-500 text-white shadow-lg' 
                  : 'bg-gray-300 text-gray-600'
              }`}
            >
              {isOnline ? 'Online' : 'Offline'}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-lg mx-auto px-4 py-4 space-y-4">
        {/* Verification Card */}
        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-bold text-[#1A1A1A]">Verification Status</h2>
            <BlueHorseBadge level="verified" size="sm" />
          </div>
          <VerificationProgress currentLevel={2} />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-2xl p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <DollarSign className="w-4 h-4 text-green-600" />
              </div>
              <span className="text-xs text-gray-500">Today</span>
            </div>
            <p className="text-2xl font-bold text-[#1A1A1A]">R{riderStats.earningsToday}</p>
            <p className="text-xs text-gray-500">This week: R{riderStats.earningsThisWeek}</p>
          </div>
          
          <div className="bg-white rounded-2xl p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <Package className="w-4 h-4 text-blue-600" />
              </div>
              <span className="text-xs text-gray-500">Deliveries</span>
            </div>
            <p className="text-2xl font-bold text-[#1A1A1A]">{riderStats.totalDeliveries}</p>
            <p className="text-xs text-gray-500">{riderStats.acceptanceRate}% acceptance</p>
          </div>
        </div>

        {/* Transport Selection */}
        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <h2 className="font-bold text-[#1A1A1A] mb-4">Delivery Transport</h2>
          
          {/* Selected Transport */}
          {currentTransport && (
            <div className={`rounded-xl p-4 mb-4 border-2 ${currentTransport.color}`}>
              <div className="flex items-center gap-4">
                <img
                  src={currentTransport.image}
                  alt={currentTransport.name}
                  className="w-20 h-20 object-cover rounded-lg"
                />
                <div className="flex-1">
                  <h3 className="font-bold text-[#1A1A1A]">{currentTransport.name}</h3>
                  <p className="text-sm text-gray-600">{currentTransport.description}</p>
                  <div className="flex items-center gap-4 mt-2 text-xs">
                    <span className="flex items-center gap-1">
                      <Navigation className="w-3 h-3" />
                      Up to {currentTransport.maxDistance}
                    </span>
                    <span className="flex items-center gap-1">
                      <DollarSign className="w-3 h-3" />
                      R{currentTransport.baseRate} base
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Transport Options Grid */}
          <div className="grid grid-cols-5 gap-2">
            {transportOptions.map((transport) => (
              <button
                key={transport.id}
                onClick={() => setSelectedTransport(transport.id)}
                className={`flex flex-col items-center p-2 rounded-xl transition-all ${
                  selectedTransport === transport.id
                    ? 'bg-[#FFD700] ring-2 ring-[#1A1A1A]'
                    : 'bg-gray-100 hover:bg-gray-200'
                }`}
              >
                <img
                  src={transport.image}
                  alt={transport.name}
                  className="w-10 h-10 object-cover rounded-lg mb-1"
                />
                <span className={`text-xs font-medium ${
                  selectedTransport === transport.id ? 'text-[#1A1A1A]' : 'text-gray-600'
                }`}>
                  {transport.name}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Active Order */}
        {activeOrder && isOnline && (
          <div className="bg-[#1A1A1A] rounded-2xl p-4 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-green-400 text-sm font-medium">Active Delivery</span>
              </div>
              <span className="text-white/60 text-sm">#{activeOrder.id}</span>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-semibold">{activeOrder.merchant}</p>
                  <p className="text-white/60 text-sm">{activeOrder.items} items • R{activeOrder.total}</p>
                </div>
                <div className="text-right">
                  <p className="text-[#FFD700] font-bold">{activeOrder.estimatedTime} min</p>
                  <p className="text-white/60 text-sm">{activeOrder.distance} km</p>
                </div>
              </div>
              
              <div className="bg-white/10 rounded-xl p-3">
                <div className="flex items-center gap-2 text-white/80">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm">{activeOrder.address}</span>
                </div>
              </div>
              
              <div className="flex gap-2">
                <button className="flex-1 bg-[#FFD700] text-[#1A1A1A] py-3 rounded-xl font-bold text-sm hover:bg-[#FFC700] transition-colors">
                  Navigate
                </button>
                <button className="flex items-center justify-center w-12 bg-white/10 rounded-xl hover:bg-white/20 transition-colors">
                  <Phone className="w-5 h-5 text-white" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Recent Earnings */}
        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-[#1A1A1A]">Recent Earnings</h2>
            <button className="text-[#FF6B35] text-sm font-medium flex items-center gap-1">
              View All <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          
          <div className="space-y-3">
            {[
              { id: '1', merchant: 'Kota King', amount: 45, time: '2 hours ago', status: 'completed' },
              { id: '2', merchant: 'Soweto Kitchen', amount: 62, time: '4 hours ago', status: 'completed' },
              { id: '3', merchant: 'Braai Masters', amount: 38, time: '6 hours ago', status: 'completed' }
            ].map((delivery) => (
              <div key={delivery.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#FFD700] rounded-lg flex items-center justify-center">
                    <Package className="w-5 h-5 text-[#1A1A1A]" />
                  </div>
                  <div>
                    <p className="font-medium text-[#1A1A1A]">{delivery.merchant}</p>
                    <p className="text-xs text-gray-500">{delivery.time}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-[#1A1A1A]">+R{delivery.amount}</p>
                  <CheckCircle className="w-4 h-4 text-green-500 ml-auto" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 py-2 px-4 shadow-lg">
        <div className="max-w-lg mx-auto flex justify-around">
          {[
            { id: 'home', icon: Package, label: 'Deliveries' },
            { id: 'earnings', icon: Wallet, label: 'Earnings' },
            { id: 'history', icon: History, label: 'History' },
            { id: 'settings', icon: Settings, label: 'Settings' }
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className="flex flex-col items-center py-1 px-3"
            >
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all ${
                activeTab === item.id ? 'bg-[#FFD700]' : ''
              }`}>
                <item.icon className={`w-5 h-5 ${
                  activeTab === item.id ? 'text-[#1A1A1A]' : 'text-gray-400'
                }`} />
              </div>
              <span className={`text-xs mt-1 ${
                activeTab === item.id ? 'font-semibold text-[#1A1A1A]' : 'text-gray-500'
              }`}>
                {item.label}
              </span>
            </button>
          ))}
        </div>
      </nav>
      
      {/* Spacer for bottom nav */}
      <div className="h-20" />
    </div>
  )
}
