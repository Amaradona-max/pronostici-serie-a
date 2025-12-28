'use client'

import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { formatDate } from '@/lib/utils'
import { ChevronRight } from 'lucide-react'
import type { Fixture } from '@/lib/api'

interface FixtureCardProps {
  fixture: Fixture
}

export function FixtureCard({ fixture }: FixtureCardProps) {
  const matchDate = new Date(fixture.match_date)

  return (
    <Link href={`/partite/${fixture.id}`}>
      <Card className="hover:shadow-lg transition-shadow cursor-pointer">
        <CardContent className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="text-sm text-muted-foreground">
              {fixture.stadium?.name && `🏟️ ${fixture.stadium.name} • `}
              {formatDate(matchDate)}
            </div>
            {fixture.round && (
              <div className="text-sm font-medium">{fixture.round}</div>
            )}
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="font-semibold text-lg">
                  {fixture.home_team.name}
                </span>
              </div>
              {fixture.status === 'finished' && fixture.home_score !== null && (
                <span className="text-2xl font-bold">{fixture.home_score}</span>
              )}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="font-semibold text-lg">
                  {fixture.away_team.name}
                </span>
              </div>
              {fixture.status === 'finished' && fixture.away_score !== null && (
                <span className="text-2xl font-bold">{fixture.away_score}</span>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between mt-4">
            <div className="text-xs text-muted-foreground uppercase">
              {fixture.status === 'scheduled' && 'Programmata'}
              {fixture.status === 'live' && (
                <span className="text-green-500 font-semibold">● Live</span>
              )}
              {fixture.status === 'finished' && 'Terminata'}
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
