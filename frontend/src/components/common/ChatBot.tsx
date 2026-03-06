import { useState } from 'react'
import { X, MessageCircle, Send } from 'lucide-react'

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<{text: string, isUser: boolean}[]>([
    { text: "Hi! I'm Nduna, your iHhashi assistant. How can I help you today?", isUser: false }
  ])
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (!input.trim()) return
    setMessages([...messages, { text: input, isUser: true }])
    setInput('')
    // Simulate Nduna response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        text: "Thanks for your message! I'm connecting you with a support agent...", 
        isUser: false 
      }])
    }, 1000)
  }

  return (
    <>
      {/* Floating Nduna Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-20 right-4 z-50 w-14 h-14 bg-secondary rounded-full shadow-lg flex items-center justify-center hover:scale-105 transition-transform border-2 border-primary"
          aria-label="Chat with Nduna"
        >
          {/* Nduna Horse Head Icon */}
          <svg width="32" height="32" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            {/* Horse head silhouette */}
            <path 
              d="M30 85C30 85 25 70 30 60C35 50 40 45 45 40C50 35 55 30 60 25C65 20 70 15 75 15C80 15 85 20 85 25C85 30 80 35 75 40C70 45 65 50 63 55C61 60 63 65 65 70C67 75 70 80 70 85" 
              fill="#FFD700"
            />
            {/* Eye */}
            <circle cx="75" cy="28" r="4" fill="#1A1A1A"/>
            {/* Smile */}
            <path 
              d="M80 35C80 35 77 38 75 38C73 38 73 35 75 33" 
              stroke="#1A1A1A" 
              strokeWidth="2" 
              fill="none"
            />
            {/* Mane */}
            <path 
              d="M55 20C55 20 50 15 52 10C54 5 58 8 60 12" 
              fill="#FFD700"
            />
          </svg>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 z-50 w-80 bg-white rounded-2xl shadow-2xl border border-secondary/10 overflow-hidden">
          {/* Header */}
          <div className="bg-secondary p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <svg width="20" height="20" viewBox="0 0 100 100" fill="none">
                  <path d="M30 85C30 85 25 70 30 60C35 50 40 45 45 40C50 35 55 30 60 25C65 20 70 15 75 15C80 15 85 20 85 25C85 30 80 35 75 40C70 45 65 50 63 55C61 60 63 65 65 70C67 75 70 80 70 85" fill="#1A1A1A"/>
                  <circle cx="75" cy="28" r="3" fill="white"/>
                </svg>
              </div>
              <div>
                <h3 className="text-primary font-bold text-sm">Nduna</h3>
                <p className="text-primary/60 text-xs">iHhashi Assistant</p>
              </div>
            </div>
            <button 
              onClick={() => setIsOpen(false)}
              className="text-primary/60 hover:text-primary"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="h-64 overflow-y-auto p-4 space-y-3 bg-gray-50">
            {messages.map((msg, idx) => (
              <div 
                key={idx} 
                className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div 
                  className={`max-w-[80%] px-3 py-2 rounded-2xl text-sm ${
                    msg.isUser 
                      ? 'bg-secondary text-white rounded-br-md' 
                      : 'bg-white border border-secondary/10 text-secondary rounded-bl-md'
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
          </div>

          {/* Input */}
          <div className="p-3 border-t border-secondary/10 bg-white">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type a message..."
                className="flex-1 px-3 py-2 bg-gray-100 rounded-xl text-sm text-secondary placeholder-secondary/40 focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button 
                onClick={handleSend}
                className="w-10 h-10 bg-secondary rounded-xl flex items-center justify-center hover:bg-secondary/80 transition-colors"
              >
                <Send className="w-4 h-4 text-primary" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
