'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { FixtureCard } from './FixtureCard'
import { Loader2 } from 'lucide-react'

interface FixturesListProps {
  status?: string
  round?: string
  limit?: number
}

export function FixturesList({ status = 'scheduled', round, limit = 20 }: FixturesListProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['fixtures', { status, round, page_size: limit }],
    queryFn: () => api.getFixtures({ status, round, page_size: limit }),
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive bg-destructive/10 p-6 text-center">
        <p className="text-destructive">Errore nel caricamento delle partite</p>
      </div>
    )
  }

  if (!data || data.fixtures.length === 0) {
    return (
      <div className="rounded-lg border bg-muted/50 p-6 text-center">
        <p className="text-muted-foreground">Nessuna partita trovata</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {data.fixtures.map((fixture) => (
        <FixtureCard key={fixture.id} fixture={fixture} />
      ))}
    </div>
  )
}
