import { ArrowLeft, Star, Clock, MapPin, Plus, Minus } from 'lucide-react'
import { useState } from 'react'
import { Header } from '../components/Header'

const sampleMenu = [
  {
    id: '1',
    name: 'Kota Special',
    description: 'Bread, polony, cheese, egg, chips, atchar',
    price: 35,
    category: 'Kotas',
    image: 'https://placehold.co/200x200/FF6B00/white?text=Kota',
  },
  {
    id: '2',
    name: 'Bunny Chow Quarter',
    description: 'Quarter loaf with mutton curry',
    price: 55,
    category: 'Bunny Chow',
    image: 'https://placehold.co/200x200/F97316/white?text=Bunny',
  },
  {
    id: '3',
    name: 'Gatsby Full',
    description: 'Full roll with polony, chips, egg, cheese',
    price: 75,
    category: 'Gatsby',
    image: 'https://placehold.co/200x200/EA580C/white?text=Gatsby',
  },
]

export function MerchantPage() {
  const [cart, setCart] = useState<Record<string, number>>({})

  const addToCart = (itemId: string) => {
    setCart(prev => ({ ...prev, [itemId]: (prev[itemId] || 0) + 1 }))
  }

  const removeFromCart = (itemId: string) => {
    setCart(prev => {
      const newCart = { ...prev }
      if (newCart[itemId] && newCart[itemId] > 1) {
        newCart[itemId] -= 1
      } else {
        delete newCart[itemId]
      }
      return newCart
    })
  }

  const cartTotal = Object.entries(cart).reduce((sum, [id, qty]) => {
    const item = sampleMenu.find(m => m.id === id)
    return sum + (item ? item.price * qty : 0)
  }, 0)

  const cartCount = Object.values(cart).reduce((sum, qty) => sum + qty, 0)

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header showCart cartCount={cartCount} />
      
      {/* Hero */}
      <div className="relative h-48 bg-primary-500">
        <img
          src="https://placehold.co/800x400/FF6B00/white?text=Kota+King"
          alt="Merchant"
          className="w-full h-full object-cover"
        />
        <a href="/" className="absolute top-4 left-4 bg-white/90 p-2 rounded-full">
          <ArrowLeft className="w-5 h-5" />
        </a>
      </div>
      
      {/* Info */}
      <div className="bg-white px-4 py-4 border-b">
        <h1 className="text-2xl font-bold text-gray-800">Kota King</h1>
        <p className="text-gray-500 mt-1">Best kotas in Soweto</p>
        
        <div className="flex items-center gap-4 mt-3 text-sm">
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-yellow-500 fill-current" />
            <span className="font-medium">4.8</span>
            <span className="text-gray-400">(234)</span>
          </div>
          <div className="flex items-center gap-1 text-gray-600">
            <Clock className="w-4 h-4" />
            <span>20-30 min</span>
          </div>
          <div className="flex items-center gap-1 text-gray-600">
            <MapPin className="w-4 h-4" />
            <span>2.3 km</span>
          </div>
        </div>
      </div>
      
      {/* Menu */}
      <div className="p-4">
        <h2 className="font-semibold text-gray-800 mb-3">Menu</h2>
        
        <div className="space-y-4">
          {sampleMenu.map(item => (
            <div key={item.id} className="bg-white rounded-xl p-4 shadow-sm flex gap-4">
              <img
                src={item.image}
                alt={item.name}
                className="w-24 h-24 rounded-lg object-cover"
              />
              <div className="flex-1">
                <h3 className="font-medium text-gray-800">{item.name}</h3>
                <p className="text-sm text-gray-500 mt-1">{item.description}</p>
                <div className="flex items-center justify-between mt-3">
                  <span className="font-semibold text-primary-600">R{item.price}</span>
                  
                  {cart[item.id] ? (
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => removeFromCart(item.id)}
                        className="w-8 h-8 rounded-full border border-primary-500 flex items-center justify-center"
                      >
                        <Minus className="w-4 h-4 text-primary-500" />
                      </button>
                      <span className="font-medium">{cart[item.id]}</span>
                      <button
                        onClick={() => addToCart(item.id)}
                        className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center"
                      >
                        <Plus className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => addToCart(item.id)}
                      className="bg-primary-500 text-white px-4 py-1.5 rounded-full text-sm font-medium"
                    >
                      Add
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Cart Bar */}
      {cartCount > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4 shadow-lg">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">{cartCount} items</p>
              <p className="font-semibold text-lg">R{cartTotal}</p>
            </div>
            <button className="bg-primary-500 text-white px-6 py-3 rounded-xl font-medium">
              View Cart
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
