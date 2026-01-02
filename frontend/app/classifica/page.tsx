'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Trophy, TrendingUp, TrendingDown, Minus, ChevronUp, ChevronDown } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

interface TeamStanding {
  position: number
  team_name: string
  team_short_name: string
  matches_played: number
  wins: number
  draws: number
  losses: number
  goals_scored: number
  goals_conceded: number
  goal_difference: number
  points: number
}

export default function ClassificaPage() {
  const { data: standings, isLoading, error } = useQuery({
    queryKey: ['standings'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/v1/standings/serie-a/2025-2026`)
      if (!res.ok) throw new Error('Failed to fetch standings')
      return res.json() as Promise<TeamStanding[]>
    },
    refetchInterval: 5 * 60 * 1000,
  })

  const getPositionStyle = (position: number) => {
    if (position <= 4) return 'bg-blue-500/10 border-l-4 border-blue-500' // Champions
    if (position === 5) return 'bg-orange-500/10 border-l-4 border-orange-500' // Europa
    if (position === 6) return 'bg-green-500/10 border-l-4 border-green-500' // Conference
    if (position >= 18) return 'bg-red-500/10 border-l-4 border-red-500' // Retrocessione
    return 'border-l-4 border-transparent'
  }

  const getPositionBadge = (position: number) => {
    if (position <= 4) return <Badge className="bg-blue-600">UCL</Badge>
    if (position === 5) return <Badge className="bg-orange-600">UEL</Badge>
    if (position === 6) return <Badge className="bg-green-600">UECL</Badge>
    if (position >= 18) return <Badge variant="destructive">RET</Badge>
    return null
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          {[...Array(20)].map((_, i) => (
            <div key={i} className="h-16 bg-muted rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Errore!</strong>
          <span className="block sm:inline"> Impossibile caricare la classifica. Riprova più tardi.</span>
          <div className="text-xs mt-2 font-mono">{error instanceof Error ? error.message : 'Unknown error'}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <Trophy className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold">Classifica Serie A</h1>
        </div>
        <p className="text-muted-foreground">
          Stagione 2025/2026 - Aggiornata in tempo reale
        </p>
      </div>

      {/* Legend */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded" />
              <span>Champions League</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-orange-500 rounded" />
              <span>Europa League</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded" />
              <span>Conference League</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded" />
              <span>Retrocessione</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table Header */}
      <div className="hidden md:grid md:grid-cols-12 gap-4 px-4 py-2 text-sm font-semibold text-muted-foreground border-b mb-2">
        <div className="col-span-1 text-center">#</div>
        <div className="col-span-4">Squadra</div>
        <div className="col-span-1 text-center">G</div>
        <div className="col-span-1 text-center">V</div>
        <div className="col-span-1 text-center">N</div>
        <div className="col-span-1 text-center">P</div>
        <div className="col-span-1 text-center">GF</div>
        <div className="col-span-1 text-center">GS</div>
        <div className="col-span-1 text-center font-bold">PT</div>
      </div>

      {/* Standings List */}
      <div className="space-y-2">
        {standings?.map((team) => (
          <Card
            key={team.position}
            className={`group hover:shadow-lg transition-all duration-300 ${getPositionStyle(team.position)}`}
          >
            <CardContent className="p-4">
              <div className="grid grid-cols-12 gap-4 items-center">
                {/* Position */}
                <div className="col-span-1 text-center">
                  <div className="flex flex-col items-center gap-1">
                    <span className="text-2xl font-bold">{team.position}</span>
                    {getPositionBadge(team.position)}
                  </div>
                </div>

                {/* Team */}
                <div className="col-span-11 md:col-span-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center flex-shrink-0">
                      <span className="font-bold text-primary">
                        {team.team_short_name}
                      </span>
                    </div>
                    <div>
                      <div className="font-bold text-lg group-hover:text-primary transition-colors">
                        {team.team_name}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Stats - Desktop */}
                <div className="hidden md:block col-span-1 text-center font-medium">
                  {team.matches_played}
                </div>
                <div className="hidden md:block col-span-1 text-center text-green-600 font-semibold">
                  {team.wins}
                </div>
                <div className="hidden md:block col-span-1 text-center text-gray-600">
                  {team.draws}
                </div>
                <div className="hidden md:block col-span-1 text-center text-red-600 font-semibold">
                  {team.losses}
                </div>
                <div className="hidden md:block col-span-1 text-center">
                  {team.goals_scored}
                </div>
                <div className="hidden md:block col-span-1 text-center">
                  {team.goals_conceded}
                </div>

                {/* Points */}
                <div className="hidden md:block col-span-1 text-center">
                  <div className="text-2xl font-bold text-primary">
                    {team.points}
                  </div>
                </div>

                {/* Mobile Stats */}
                <div className="md:hidden col-span-11 grid grid-cols-3 gap-2 mt-2 text-sm">
                  <div className="text-center">
                    <div className="text-xs text-muted-foreground">Punti</div>
                    <div className="text-lg font-bold text-primary">{team.points}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-muted-foreground">G</div>
                    <div className="font-semibold">{team.matches_played}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-muted-foreground">Diff</div>
                    <div className={`font-semibold ${team.goal_difference > 0 ? 'text-green-600' : team.goal_difference < 0 ? 'text-red-600' : ''}`}>
                      {team.goal_difference > 0 ? '+' : ''}{team.goal_difference}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
