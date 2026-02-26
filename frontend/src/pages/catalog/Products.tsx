import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Search, ShoppingCart, Plus, Minus } from 'lucide-react'
import { useCart } from '../../hooks/useCart'

const mockProducts = [
  { id: '1', name: 'Stainless Steel Spork', price: 45, category: 'utensils', stock: 50, image: 'https://placehold.co/200x200/FF6B35/white?text=Spork' },
  { id: '2', name: 'Bic Ballpoint Pens (10pk)', price: 35, category: 'stationery', stock: 100, image: 'https://placehold.co/200x200/3B82F6/white?text=Pens' },
  { id: '3', name: 'Kitchen Towels (3pk)', price: 55, category: 'household', stock: 30, image: 'https://placehold.co/200x200/10B981/white?text=Towels' },
  { id: '4', name: 'USB Charging Cable', price: 89, category: 'electronics', stock: 25, image: 'https://placehold.co/200x200/8B5CF6/white?text=Cable' },
  { id: '5', name: 'Notebook A5 (100 pages)', price: 25, category: 'stationery', stock: 75, image: 'https://placehold.co/200x200/3B82F6/white?text=Notebook' },
  { id: '6', name: 'Wooden Spatula', price: 35, category: 'utensils', stock: 40, image: 'https://placehold.co/200x200/FF6B35/white?text=Spatula' },
]

const categories = ['All', 'Utensils', 'Stationery', 'Household', 'Electronics']

export default function Products() {
  const { category } = useParams()
  const [searchQuery, setSearchQuery] = useState('')
  const [activeCategory, setActiveCategory] = useState(category || 'All')
  const { items, addItem, updateQuantity } = useCart()

  const filteredProducts = mockProducts.filter(p => {
    const matchesCategory = activeCategory === 'All' || p.category.toLowerCase() === activeCategory.toLowerCase()
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const getItemQuantity = (productId: string) => {
    const item = items.find(i => i.productId === productId)
    return item?.quantity || 0
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="px-4 py-3 flex items-center gap-3">
          <Link to="/" className="p-2 -ml-2">
            <ArrowLeft className="w-6 h-6" />
          </Link>
          <div className="flex-1 relative">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10"
            />
          </div>
          <Link to="/cart" className="relative">
            <ShoppingCart className="w-6 h-6 text-gray-600" />
            {items.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-[#FF6B35] text-white text-xs w-4 h-4 rounded-full flex items-center justify-center">
                {items.length}
              </span>
            )}
          </Link>
        </div>

        {/* Category Tabs */}
        <div className="px-4 py-2 flex gap-2 overflow-x-auto">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-4 py-1.5 rounded-full text-sm whitespace-nowrap ${
                activeCategory === cat
                  ? 'bg-[#FF6B35] text-white'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </header>

      {/* Product Grid */}
      <div className="max-w-lg mx-auto px-4 py-4">
        <div className="grid grid-cols-2 gap-3">
          {filteredProducts.map(product => {
            const qty = getItemQuantity(product.id)
            return (
              <div key={product.id} className="card">
                <img src={product.image} alt={product.name} className="w-full aspect-square object-cover rounded-lg mb-2" />
                <h4 className="font-medium text-sm line-clamp-2">{product.name}</h4>
                <p className="text-xs text-gray-400 mt-1">{product.stock} in stock</p>
                <div className="flex justify-between items-center mt-2">
                  <span className="font-bold text-[#FF6B35]">R{product.price}</span>
                  {qty > 0 ? (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => updateQuantity(product.id, qty - 1)}
                        className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center"
                      >
                        <Minus className="w-4 h-4" />
                      </button>
                      <span className="font-medium">{qty}</span>
                      <button
                        onClick={() => updateQuantity(product.id, qty + 1)}
                        className="w-7 h-7 rounded-full bg-[#FF6B35] text-white flex items-center justify-center"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => addItem({
                        productId: product.id,
                        name: product.name,
                        price: product.price,
                        quantity: 1,
                        image: product.image
                      })}
                      className="bg-[#FF6B35] text-white text-xs px-3 py-1.5 rounded-lg"
                    >
                      Add
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Floating Cart Button */}
      {items.length > 0 && (
        <div className="fixed bottom-4 left-4 right-4 max-w-lg mx-auto">
          <Link
            to="/cart"
            className="bg-[#FF6B35] text-white py-4 px-6 rounded-xl flex items-center justify-between shadow-lg"
          >
            <span>{items.length} items</span>
            <span className="font-bold">R{useCart.getState().getTotal()}</span>
          </Link>
        </div>
      )}
    </div>
  )
}