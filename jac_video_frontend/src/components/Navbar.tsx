'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  VideoCameraIcon
} from '@heroicons/react/24/outline'

const Navbar = () => {
  const pathname = usePathname()

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center">
          {/* Logo和品牌名 */}
          <div className="flex items-center mr-8">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-9 h-9 bg-gradient-to-r from-[#8778E5] to-[#EF6DA0] rounded-full flex items-center justify-center text-white font-bold">
                J
              </div>
              <span className="text-xl font-bold gradient-text">球的 Video</span>
            </Link>
          </div>

          {/* 主导航 */}
          <div className="flex-grow">
            <Link
              href="/products"
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-gray-700 hover:text-[#8778E5] 
                transition-colors duration-200 ${pathname.startsWith('/products') ? 'bg-[#F5F7FF] text-[#8778E5]' : ''}`}
            >
              <svg 
                className="w-5 h-5" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={1.5}
                  d="M7 4v16m0-8h10m0-8v16"
                />
              </svg>
              <span>产品功能</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar 