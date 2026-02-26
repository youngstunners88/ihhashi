import { useState, useEffect } from 'react'

export default function SplashScreen() {
  const [fade, setFade] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setFade(true), 1500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div 
      className={`fixed inset-0 bg-yellow-400 flex flex-col items-center justify-center transition-opacity duration-500 ${fade ? 'opacity-0' : 'opacity-100'}`}
    >
      {/* Logo */}
      <div className="flex items-center gap-4">
        <img 
          src="/logo.png" 
          alt="iHhashi Logo" 
          className="w-24 h-24 object-contain"
        />
        <h1 className="text-4xl font-bold text-black">iHhashi</h1>
      </div>
      
      {/* Tagline */}
      <p className="mt-4 text-black text-lg">Food Delivery SA</p>
      
      {/* Loading indicator */}
      <div className="mt-8 flex gap-2">
        <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-3 h-3 bg-black rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  )
}
