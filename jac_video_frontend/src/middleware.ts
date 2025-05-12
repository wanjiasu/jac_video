import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Simple middleware that doesn't use authentication
export async function middleware(req: NextRequest) {
  // All products are now accessible without authentication
  return NextResponse.next()
}

// Only run middleware for products routes
export const config = {
  matcher: '/products/:path*'
} 