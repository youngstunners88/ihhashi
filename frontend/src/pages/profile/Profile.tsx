import { Link } from 'react-router-dom'
import { ArrowLeft, MapPin, CreditCard, HelpCircle, LogOut } from 'lucide-react'

export default function Profile() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white px-4 py-3 flex items-center border-b border-gray-100">
        <Link to="/" className="p-2 -ml-2">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <h1 className="text-lg font-semibold ml-2">Profile</h1>
      </header>

      {/* Profile Header */}
      <div className="bg-white px-4 py-6 mb-3">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-[#FF6B35] flex items-center justify-center text-white text-2xl font-bold">
            T
          </div>
          <div>
            <h2 className="font-bold text-lg">Thandi Nkosi</h2>
            <p className="text-gray-500 text-sm">+27 82 123 4567</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="bg-white px-4 py-4 mb-3">
        <div className="grid grid-cols-3 text-center">
          <div>
            <p className="text-2xl font-bold text-[#FF6B35]">12</p>
            <p className="text-xs text-gray-500">Orders</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-[#FF6B35]">R850</p>
            <p className="text-xs text-gray-500">Total Spent</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-[#FF6B35]">4</p>
            <p className="text-xs text-gray-500">Addresses</p>
          </div>
        </div>
      </div>

      {/* Menu Items */}
      <div className="bg-white">
        <Link to="/profile/addresses" className="flex items-center gap-3 px-4 py-3.5 border-b border-gray-100">
          <MapPin className="w-5 h-5 text-gray-400" />
          <span className="flex-1">Saved Addresses</span>
          <span className="text-gray-400 text-sm">4</span>
        </Link>
        <Link to="/profile/payments" className="flex items-center gap-3 px-4 py-3.5 border-b border-gray-100">
          <CreditCard className="w-5 h-5 text-gray-400" />
          <span className="flex-1">Payment Methods</span>
        </Link>
        <Link to="/help" className="flex items-center gap-3 px-4 py-3.5 border-b border-gray-100">
          <HelpCircle className="w-5 h-5 text-gray-400" />
          <span className="flex-1">Help & Support</span>
        </Link>
        <button className="flex items-center gap-3 px-4 py-3.5 w-full text-left text-red-500">
          <LogOut className="w-5 h-5" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  )
}