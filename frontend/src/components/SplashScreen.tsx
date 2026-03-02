import { useState, useEffect } from 'react'

export default function SplashScreen() {
  const [fade, setFade] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setFade(true), 1500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div 
      className={`fixed inset-0 bg-[#FFD700] flex flex-col items-center justify-center transition-opacity duration-500 ${fade ? 'opacity-0' : 'opacity-100'}`}
    >
      {/* Logo */}
      <div className="flex items-center gap-4">
        <div className="w-20 h-20 bg-[#1A1A1A] rounded-2xl flex items-center justify-center shadow-lg">
          <span className="text-4xl">🐴</span>
        </div>
        <h1 className="text-4xl font-bold text-[#1A1A1A]">iHhashi</h1>
      </div>
      
      {/* Tagline */}
      <p className="mt-4 text-[#1A1A1A]/70 text-lg font-medium">Your Delivery Horse 🇿🇦</p>
      
      {/* Loading indicator */}
      <div className="mt-8 flex gap-2">
        <div className="w-3 h-3 bg-[#1A1A1A] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-3 h-3 bg-[#1A1A1A] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-3 h-3 bg-[#1A1A1A] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  )
}
