'use client'

import Link from 'next/link'
import { useTheme } from 'next-themes'
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function Header() {
  const { theme, setTheme } = useTheme()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <Link href="/" className="mr-6 flex items-center space-x-2">
          <span className="text-xl font-bold">⚽ Serie A Predictions</span>
        </Link>

        <nav className="flex items-center space-x-6 text-sm font-medium flex-1">
          <Link
            href="/"
            className="transition-colors hover:text-foreground/80 text-foreground"
          >
            Home
          </Link>
          <Link
            href="/partite"
            className="transition-colors hover:text-foreground/80 text-foreground/60"
          >
            Partite
          </Link>
          <Link
            href="/squadre"
            className="transition-colors hover:text-foreground/80 text-foreground/60"
          >
            Squadre
          </Link>
          <Link
            href="/stats"
            className="transition-colors hover:text-foreground/80 text-foreground/60"
          >
            Statistiche
          </Link>
        </nav>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </div>
    </header>
  )
}
