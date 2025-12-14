'use client'

import Link from 'next/link'

export default function Navigation() {
  return (
    <nav className="fixed top-0 left-0 right-0 bg-purple-600 shadow-lg z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo space - left side */}
          <div className="flex-shrink-0">
            <Link href="/" className="block">
              <div className="w-10 h-10 bg-white/10 rounded flex items-center justify-center hover:bg-white/20 transition-colors">
                {/* Placeholder for your logo */}
                <span className="text-white text-xl font-bold">F1</span>
              </div>
            </Link>
          </div>

          {/* Navigation links - right side */}
          <div className="flex space-x-8">
            <Link
              href="/"
              className="text-white hover:text-purple-200 transition-colors px-3 py-2 text-sm font-medium"
            >
              Home
            </Link>
            <Link
              href="/results"
              className="text-white hover:text-purple-200 transition-colors px-3 py-2 text-sm font-medium"
            >
              Results
            </Link>
            <Link
              href="/analyze"
              className="text-white hover:text-purple-200 transition-colors px-3 py-2 text-sm font-medium"
            >
              Analyze
            </Link>
            <Link
              href="/about"
              className="text-white hover:text-purple-200 transition-colors px-3 py-2 text-sm font-medium"
            >
              About
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
