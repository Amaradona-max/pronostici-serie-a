'use client'

import { useState } from 'react'
import { Users, ChevronDown, ChevronUp, Clock } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

interface LineupPlayer {
  name: string
  position: string
  jersey_number: number
  is_starter: boolean
}

interface TeamLineup {
  team_name: string
  formation: string
  starters: LineupPlayer[]
  bench: LineupPlayer[]
}

interface LineupsData {
  fixture_id: number
  home_lineup?: TeamLineup
  away_lineup?: TeamLineup
}

interface ProbableLineupsProps {
  fixtureId: number
  homeTeamName: string
  awayTeamName: string
  matchDate: string
}

export function ProbableLineups({
  fixtureId,
  homeTeamName,
  awayTeamName,
  matchDate
}: ProbableLineupsProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [data, setData] = useState<LineupsData | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchData = async () => {
    if (data) {
      setIsOpen(!isOpen)
      return
    }

    setLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || ''
      const res = await fetch(`${apiUrl}/api/v1/predictions/${fixtureId}/lineups`)
      if (!res.ok) throw new Error('Failed to fetch lineups')
      const json = await res.json()
      setData(json)
      setIsOpen(true)
    } catch (err) {
      console.error('Error fetching lineups:', err)
    } finally {
      setLoading(false)
    }
  }

  const renderLineup = (lineup: TeamLineup) => {
    const positionGroups = {
      GK: lineup.starters.filter(p => p.position === 'GK'),
      DF: lineup.starters.filter(p => p.position === 'DF'),
      MF: lineup.starters.filter(p => p.position === 'MF'),
      FW: lineup.starters.filter(p => p.position === 'FW')
    }

    return (
      <div>
        <div className="flex items-center justify-between mb-3">
          <h5 className="text-sm font-bold">{lineup.team_name}</h5>
          <Badge variant="secondary" className="text-xs">
            {lineup.formation}
          </Badge>
        </div>

        {/* Titolari per ruolo */}
        <div className="space-y-3">
          {(['FW', 'MF', 'DF', 'GK'] as const).map(pos => (
            <div key={pos}>
              {positionGroups[pos].length > 0 && (
                <>
                  <div className="text-xs text-muted-foreground mb-1 font-semibold">
                    {pos === 'GK' ? 'Portiere' : pos === 'DF' ? 'Difensori' : pos === 'MF' ? 'Centrocampisti' : 'Attaccanti'}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {positionGroups[pos].map((player, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-1 px-2 py-1 rounded bg-green-500/10 border border-green-500/20"
                      >
                        <span className="text-xs font-bold text-green-600">
                          {player.jersey_number}
                        </span>
                        <span className="text-xs font-medium">
                          {player.name}
                        </span>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>

        {/* Panchina */}
        <div className="mt-4 pt-3 border-t">
          <div className="text-xs text-muted-foreground mb-2 font-semibold">
            Panchina
          </div>
          <div className="flex flex-wrap gap-2">
            {lineup.bench.map((player, idx) => (
              <div
                key={idx}
                className="flex items-center gap-1 px-2 py-1 rounded bg-gray-500/10 border border-gray-500/20"
              >
                <span className="text-xs font-bold text-muted-foreground">
                  {player.jersey_number}
                </span>
                <span className="text-xs">
                  {player.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="mt-4 border border-green-500/20 rounded-lg overflow-hidden">
      {/* Header */}
      <button
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          fetchData()
        }}
        className="w-full p-4 bg-gradient-to-r from-green-500/10 to-emerald-500/10 hover:from-green-500/15 hover:to-emerald-500/15 transition-colors flex items-center justify-between"
      >
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-green-600" />
          <span className="text-sm font-semibold text-muted-foreground">
            Formazioni Probabili
          </span>
        </div>
        {loading ? (
          <div className="animate-spin h-4 w-4 border-2 border-green-600 border-t-transparent rounded-full" />
        ) : isOpen ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      {/* Content */}
      {isOpen && data && (
        <div className="p-4 bg-background/50">
          {!data.home_lineup && !data.away_lineup ? (
            <div className="text-center py-8">
              <Clock className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">
                Nessuna formazione disponibile al momento
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {data.home_lineup && renderLineup(data.home_lineup)}
              {data.away_lineup && renderLineup(data.away_lineup)}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
