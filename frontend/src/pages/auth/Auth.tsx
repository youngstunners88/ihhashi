import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

interface AuthProps {
  onAuth: () => void
}

export default function Auth({ onAuth }: AuthProps) {
  const navigate = useNavigate()
  const [step, setStep] = useState<'phone' | 'otp'>('phone')
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSendOTP = async () => {
    setLoading(true)
    // TODO: Call API to send OTP
    setTimeout(() => {
      setStep('otp')
      setLoading(false)
    }, 1000)
  }

  const handleVerifyOTP = async () => {
    setLoading(true)
    // TODO: Call API to verify OTP
    setTimeout(() => {
      onAuth()
      navigate('/')
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="px-4 py-3 flex items-center border-b border-gray-100">
        <button onClick={() => navigate(-1)} className="p-2 -ml-2">
          <ArrowLeft className="w-6 h-6" />
        </button>
        <h1 className="text-lg font-semibold ml-2">Sign In</h1>
      </div>

      {/* Content */}
      <div className="max-w-md mx-auto px-6 py-8">
        <h2 className="text-2xl font-bold mb-2">
          {step === 'phone' ? 'Enter your number' : 'Verify your number'}
        </h2>
        <p className="text-gray-600 mb-8">
          {step === 'phone' 
            ? "We'll send you a verification code" 
            : `We sent a code to +27${phone}`}
        </p>

        {step === 'phone' ? (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-lg font-medium text-gray-700">+27</span>
              <input
                type="tel"
                placeholder="821234567"
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                className="input flex-1"
                maxLength={10}
              />
            </div>
            <button 
              onClick={handleSendOTP}
              disabled={phone.length < 9 || loading}
              className="btn-primary w-full disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Continue'}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex gap-2 justify-center">
              {[0, 1, 2, 3, 4, 5].map((i) => (
                <input
                  key={i}
                  type="text"
                  maxLength={1}
                  value={otp[i] || ''}
                  onChange={(e) => {
                    const val = e.target.value.replace(/\D/g, '')
                    const newOtp = otp.split('')
                    newOtp[i] = val
                    setOtp(newOtp.join(''))
                    // Auto-focus next input
                    if (val && i < 5) {
                      const next = e.target.nextElementSibling as HTMLInputElement
                      next?.focus()
                    }
                  }}
                  className="w-12 h-12 text-center text-xl font-bold border border-gray-200 rounded-xl focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 outline-none"
                />
              ))}
            </div>
            <button 
              onClick={handleVerifyOTP}
              disabled={otp.length < 6 || loading}
              className="btn-primary w-full disabled:opacity-50"
            >
              {loading ? 'Verifying...' : 'Verify'}
            </button>
            <button 
              onClick={() => setStep('phone')}
              className="text-[#FF6B35] text-sm font-medium w-full py-2"
            >
              Change number
            </button>
          </div>
        )}

        <p className="text-xs text-gray-400 text-center mt-8">
          By continuing, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  )
}