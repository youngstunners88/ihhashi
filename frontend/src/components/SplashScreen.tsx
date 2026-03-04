import { useState, useEffect } from 'react'

export default function SplashScreen() {
  const [fade, setFade] = useState(false)
  const [imageLoaded, setImageLoaded] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setFade(true), 2500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div 
      className={`fixed inset-0 bg-[#FFD700] flex flex-col items-center justify-center transition-opacity duration-700 z-50 ${fade ? 'opacity-0' : 'opacity-100'}`}
    >
      {/* Main Splash Image */}
      <div className="relative w-full max-w-md px-8">
        <img
          src="/assets/splash.jpg"
          alt="iHhashi"
          className={`w-full h-auto object-contain transition-opacity duration-500 ${imageLoaded ? 'opacity-100' : 'opacity-0'}`}
          onLoad={() => setImageLoaded(true)}
        />
        {!imageLoaded && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-20 h-20 bg-[#1A1A1A] rounded-2xl flex items-center justify-center shadow-lg animate-pulse">
              <span className="text-4xl">🐴</span>
            </div>
          </div>
        )}
      </div>
      
      {/* Tagline */}
      <p className="mt-6 text-[#1A1A1A]/80 text-lg font-medium tracking-wide">
        Your Delivery Horse <span className="inline-block animate-bounce">🇿🇦</span>
      </p>
      
      {/* Loading indicator */}
      <div className="mt-8 flex gap-2">
        <div className="w-3 h-3 bg-[#1A1A1A] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-3 h-3 bg-[#1A1A1A] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-3 h-3 bg-[#1A1A1A] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      
      {/* Version */}
      <p className="mt-8 text-xs text-[#1A1A1A]/50 font-medium">
        v1.0.0 • South Africa
      </p>
    </div>
  )
}
