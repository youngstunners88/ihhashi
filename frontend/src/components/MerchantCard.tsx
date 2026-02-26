import { Star, Clock } from 'lucide-react'

interface Merchant {
  id: string
  name: string
  category: string
  description: string
  rating: number
  reviews: number
  deliveryTime: string
  deliveryFee: number
  image: string
}

interface MerchantCardProps {
  merchant: Merchant
}

export function MerchantCard({ merchant }: MerchantCardProps) {
  return (
    <a
      href={`/merchant/${merchant.id}`}
      className="block bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition"
    >
      {/* Image */}
      <div className="relative h-40">
        <img
          src={merchant.image}
          alt={merchant.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute top-3 right-3 bg-white px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {merchant.deliveryTime} min
        </div>
      </div>
      
      {/* Info */}
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-gray-800">{merchant.name}</h3>
            <p className="text-sm text-gray-500 mt-1">{merchant.description}</p>
          </div>
          <div className="flex items-center gap-1 bg-green-50 px-2 py-1 rounded">
            <Star className="w-4 h-4 text-yellow-500 fill-current" />
            <span className="text-sm font-medium text-gray-700">{merchant.rating}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
          <span>R{merchant.deliveryFee} delivery</span>
          <span>•</span>
          <span>{merchant.reviews} reviews</span>
        </div>
      </div>
    </a>
  )
}
