import { CheckCircle, Shield, Award } from 'lucide-react'

interface BlueHorseBadgeProps {
  level: 'basic' | 'verified' | 'premium'
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  className?: string
}

const levelConfig = {
  basic: {
    color: 'bg-gray-100 border-gray-300',
    iconColor: 'text-gray-500',
    label: 'Basic',
    description: 'Account created'
  },
  verified: {
    color: 'bg-cyan-50 border-cyan-400',
    iconColor: 'text-cyan-500',
    label: 'Blue Horse Verified',
    description: 'Identity verified'
  },
  premium: {
    color: 'bg-gradient-to-r from-cyan-50 to-blue-50 border-cyan-400',
    iconColor: 'text-cyan-600',
    label: 'Blue Horse Premium',
    description: 'Fully verified business'
  }
}

const sizeConfig = {
  sm: {
    container: 'w-6 h-6',
    icon: 'w-3 h-3',
    text: 'text-xs',
    padding: 'px-2 py-0.5'
  },
  md: {
    container: 'w-10 h-10',
    icon: 'w-5 h-5',
    text: 'text-sm',
    padding: 'px-3 py-1'
  },
  lg: {
    container: 'w-16 h-16',
    icon: 'w-8 h-8',
    text: 'text-base',
    padding: 'px-4 py-2'
  }
}

export function BlueHorseBadge({ 
  level = 'verified', 
  size = 'md', 
  showLabel = true,
  className = '' 
}: BlueHorseBadgeProps) {
  const config = levelConfig[level]
  const sizeCfg = sizeConfig[size]

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Badge Icon */}
      <div className={`relative ${sizeCfg.container} rounded-full border-2 ${config.color} flex items-center justify-center shadow-sm`}>
        <img
          src="/assets/blue-horse-badge.jpg"
          alt="Blue Horse"
          className="w-3/4 h-3/4 object-contain rounded-full"
        />
        {level === 'premium' && (
          <div className="absolute -top-1 -right-1 bg-yellow-400 rounded-full p-0.5">
            <Award className="w-2 h-2 text-white" />
          </div>
        )}
        {level === 'verified' && (
          <div className="absolute -bottom-0.5 -right-0.5 bg-cyan-500 rounded-full p-0.5">
            <CheckCircle className="w-2 h-2 text-white" />
          </div>
        )}
      </div>
      
      {/* Label */}
      {showLabel && (
        <div className={`flex flex-col ${sizeCfg.padding}`}>
          <span className={`font-semibold ${config.iconColor} ${sizeCfg.text}`}>
            {config.label}
          </span>
          <span className="text-xs text-gray-500">
            {config.description}
          </span>
        </div>
      )}
    </div>
  )
}

// Verification level indicator
export function VerificationProgress({ currentLevel }: { currentLevel: 0 | 1 | 2 | 3 }) {
  const levels = [
    { label: 'Unverified', color: 'bg-gray-300' },
    { label: 'Basic', color: 'bg-yellow-400' },
    { label: 'Verified', color: 'bg-cyan-500' },
    { label: 'Premium', color: 'bg-gradient-to-r from-cyan-500 to-blue-500' }
  ]

  return (
    <div className="w-full">
      <div className="flex justify-between text-xs text-gray-600 mb-2">
        {levels.map((level, idx) => (
          <span key={idx} className={idx <= currentLevel ? 'font-semibold text-[#1A1A1A]' : ''}>
            {level.label}
          </span>
        ))}
      </div>
      <div className="flex gap-1">
        {levels.map((level, idx) => (
          <div
            key={idx}
            className={`h-2 flex-1 rounded-full transition-all ${
              idx <= currentLevel ? level.color : 'bg-gray-200'
            }`}
          />
        ))}
      </div>
    </div>
  )
}

// Merchant verification card
export function MerchantVerificationCard({ 
  merchantName, 
  level,
  documents
}: { 
  merchantName: string
  level: 'basic' | 'verified' | 'premium'
  documents?: { type: string; verified: boolean }[]
}) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-bold text-[#1A1A1A]">{merchantName}</h3>
          <p className="text-sm text-gray-500">Verification Status</p>
        </div>
        <BlueHorseBadge level={level} size="md" showLabel={false} />
      </div>
      
      {documents && (
        <div className="space-y-2">
          {documents.map((doc, idx) => (
            <div key={idx} className="flex items-center justify-between text-sm">
              <span className="text-gray-600">{doc.type}</span>
              {doc.verified ? (
                <CheckCircle className="w-4 h-4 text-green-500" />
              ) : (
                <span className="text-xs text-orange-500">Pending</span>
              )}
            </div>
          ))}
        </div>
      )}
      
      {level !== 'premium' && (
        <button className="mt-4 w-full py-2 bg-[#FFD700] text-[#1A1A1A] rounded-xl font-semibold text-sm hover:bg-[#FFC700] transition-colors">
          Upgrade Verification
        </button>
      )}
    </div>
  )
}
