import { Star, Clock, MapPin, CheckCircle } from 'lucide-react'
import { BlueHorseBadge } from './BlueHorseBadge'

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
  verified?: boolean
  verificationLevel?: 'basic' | 'verified' | 'premium'
  distance?: string
}

interface MerchantCardProps {
  merchant: Merchant
  variant?: 'default' | 'compact' | 'featured'
}

export function MerchantCard({ merchant, variant = 'default' }: MerchantCardProps) {
  if (variant === 'compact') {
    return (
      <a
        href={`/merchant/${merchant.id}`}
        className="block bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition border border-gray-100"
      >
        <div className="flex items-center p-3 gap-3">
          <img
            src={merchant.image}
            alt={merchant.name}
            className="w-16 h-16 object-cover rounded-lg"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1">
              <h3 className="font-semibold text-gray-800 truncate">{merchant.name}</h3>
              {merchant.verified && (
                <BlueHorseBadge level={merchant.verificationLevel || 'verified'} size="sm" showLabel={false} />
              )}
            </div>
            <p className="text-xs text-gray-500">{merchant.category}</p>
            <div className="flex items-center gap-2 mt-1">
              <div className="flex items-center gap-0.5">
                <Star className="w-3 h-3 text-yellow-500 fill-current" />
                <span className="text-xs font-medium">{merchant.rating}</span>
              </div>
              <span className="text-xs text-gray-400">•</span>
              <span className="text-xs text-gray-500">{merchant.deliveryTime} min</span>
            </div>
          </div>
        </div>
      </a>
    )
  }

  if (variant === 'featured') {
    return (
      <a
        href={`/merchant/${merchant.id}`}
        className="block bg-white rounded-2xl shadow-md overflow-hidden hover:shadow-lg transition transform hover:-translate-y-1"
      >
        {/* Image */}
        <div className="relative h-48">
          <img
            src={merchant.image}
            alt={merchant.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          
          {/* Badges */}
          <div className="absolute top-3 left-3">
            {merchant.verified && (
              <BlueHorseBadge level={merchant.verificationLevel || 'verified'} size="sm" />
            )}
          </div>
          
          <div className="absolute top-3 right-3 bg-white/90 backdrop-blur px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {merchant.deliveryTime} min
          </div>
          
          {/* Bottom Info */}
          <div className="absolute bottom-0 left-0 right-0 p-4">
            <h3 className="font-bold text-white text-lg">{merchant.name}</h3>
            <p className="text-white/80 text-sm">{merchant.category}</p>
          </div>
        </div>
        
        {/* Info */}
        <div className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1 bg-green-50 px-2 py-1 rounded-lg">
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
                <span className="text-sm font-medium text-gray-700">{merchant.rating}</span>
                <span className="text-xs text-gray-500">({merchant.reviews})</span>
              </div>
              {merchant.distance && (
                <div className="flex items-center gap-1 text-gray-500 text-sm">
                  <MapPin className="w-3 h-3" />
                  {merchant.distance}
                </div>
              )}
            </div>
            <span className="text-sm font-semibold text-[#FF6B35]">
              R{merchant.deliveryFee} delivery
            </span>
          </div>
        </div>
      </a>
    )
  }

  return (
    <a
      href={`/merchant/${merchant.id}`}
      className="block bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition border border-gray-100"
    >
      {/* Image */}
      <div className="relative h-40">
        <img
          src={merchant.image}
          alt={merchant.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute top-3 right-3 bg-white/90 backdrop-blur px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {merchant.deliveryTime} min
        </div>
        
        {/* Verification Badge */}
        {merchant.verified && (
          <div className="absolute top-3 left-3">
            <BlueHorseBadge level={merchant.verificationLevel || 'verified'} size="sm" showLabel={false} />
          </div>
        )}
      </div>
      
      {/* Info */}
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-800 truncate">{merchant.name}</h3>
              {merchant.verified && (
                <CheckCircle className="w-4 h-4 text-cyan-500 flex-shrink-0" />
              )}
            </div>
            <p className="text-sm text-gray-500 mt-1">{merchant.description}</p>
          </div>
          <div className="flex items-center gap-1 bg-green-50 px-2 py-1 rounded flex-shrink-0 ml-2">
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
