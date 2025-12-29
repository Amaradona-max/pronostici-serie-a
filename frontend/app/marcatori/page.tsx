'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Target, Award, TrendingUp } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api'

interface TopScorer {
  position: number
  player_name: string
  team_name: string
  team_short_name: string
  goals: number
  assists: number
  matches: number
}

export default function MarcatoriPage() {
  const { data: scorers, isLoading } = useQuery({
    queryKey: ['topScorers'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/v1/standings/top-scorers/2025-2026?limit=20`)
      if (!res.ok) throw new Error('Failed to fetch top scorers')
      return res.json() as Promise<TopScorer[]>
    },
    refetchInterval: 5 * 60 * 1000,
  })

  const getPodiumColor = (position: number) => {
    if (position === 1) return 'from-yellow-500 to-yellow-600' // Gold
    if (position === 2) return 'from-gray-400 to-gray-500' // Silver
    if (position === 3) return 'from-orange-600 to-orange-700' // Bronze
    return 'from-primary/20 to-primary/10'
  }

  const getPodiumBadge = (position: number) => {
    if (position === 1) return '🥇'
    if (position === 2) return '🥈'
    if (position === 3) return '🥉'
    return null
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-24 bg-muted rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  const topThree = scorers?.slice(0, 3) || []
  const others = scorers?.slice(3) || []

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <Target className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold">Capocannonieri</h1>
        </div>
        <p className="text-muted-foreground">
          Classifica marcatori Serie A 2025/2026
        </p>
      </div>

      {/* Podium - Top 3 */}
      {topThree.length > 0 && (
        <div className="mb-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 2nd Place */}
            {topThree[1] && (
              <div className="md:order-1 order-2">
                <Card className="group hover:shadow-2xl transition-all duration-300 overflow-hidden">
                  <div className={`h-2 bg-gradient-to-r ${getPodiumColor(2)}`} />
                  <CardContent className="p-6 text-center">
                    <div className="text-4xl mb-2">{getPodiumBadge(2)}</div>
                    <div className="text-5xl font-bold mb-2">{topThree[1].goals}</div>
                    <div className="text-xs text-muted-foreground mb-2">GOL</div>
                    <h3 className="text-xl font-bold mb-1">{topThree[1].player_name}</h3>
                    <Badge variant="secondary">{topThree[1].team_short_name}</Badge>
                    <div className="mt-4 pt-4 border-t flex justify-center gap-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Assist</div>
                        <div className="font-semibold">{topThree[1].assists}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Partite</div>
                        <div className="font-semibold">{topThree[1].matches}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* 1st Place - Winner */}
            {topThree[0] && (
              <div className="md:order-2 order-1">
                <Card className="group hover:shadow-2xl transition-all duration-300 overflow-hidden md:scale-110 md:mt-0 mt-4">
                  <div className={`h-3 bg-gradient-to-r ${getPodiumColor(1)}`} />
                  <CardContent className="p-8 text-center relative">
                    <Award className="absolute top-4 right-4 h-8 w-8 text-yellow-500 animate-pulse" />
                    <div className="text-6xl mb-3">{getPodiumBadge(1)}</div>
                    <div className="text-7xl font-bold mb-2 text-primary">{topThree[0].goals}</div>
                    <div className="text-sm text-muted-foreground mb-3">GOL</div>
                    <h3 className="text-2xl font-bold mb-2">{topThree[0].player_name}</h3>
                    <Badge className="mb-4">{topThree[0].team_short_name}</Badge>
                    <div className="mt-6 pt-6 border-t flex justify-center gap-6">
                      <div>
                        <div className="text-muted-foreground text-sm">Assist</div>
                        <div className="font-bold text-lg">{topThree[0].assists}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground text-sm">Partite</div>
                        <div className="font-bold text-lg">{topThree[0].matches}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground text-sm">Media</div>
                        <div className="font-bold text-lg">{(topThree[0].goals / topThree[0].matches).toFixed(2)}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* 3rd Place */}
            {topThree[2] && (
              <div className="md:order-3 order-3">
                <Card className="group hover:shadow-2xl transition-all duration-300 overflow-hidden">
                  <div className={`h-2 bg-gradient-to-r ${getPodiumColor(3)}`} />
                  <CardContent className="p-6 text-center">
                    <div className="text-4xl mb-2">{getPodiumBadge(3)}</div>
                    <div className="text-5xl font-bold mb-2">{topThree[2].goals}</div>
                    <div className="text-xs text-muted-foreground mb-2">GOL</div>
                    <h3 className="text-xl font-bold mb-1">{topThree[2].player_name}</h3>
                    <Badge variant="secondary">{topThree[2].team_short_name}</Badge>
                    <div className="mt-4 pt-4 border-t flex justify-center gap-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Assist</div>
                        <div className="font-semibold">{topThree[2].assists}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Partite</div>
                        <div className="font-semibold">{topThree[2].matches}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Rest of the list */}
      <div className="space-y-2">
        {others.map((scorer) => (
          <Card key={scorer.position} className="group hover:shadow-lg hover:scale-[1.01] transition-all duration-300">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1">
                  {/* Position */}
                  <div className="text-center w-12">
                    <div className="text-2xl font-bold text-muted-foreground">
                      {scorer.position}
                    </div>
                  </div>

                  {/* Avatar */}
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center flex-shrink-0">
                    <Target className="h-6 w-6 text-primary" />
                  </div>

                  {/* Info */}
                  <div className="flex-1">
                    <div className="font-bold text-lg group-hover:text-primary transition-colors">
                      {scorer.player_name}
                    </div>
                    <div className="text-sm text-muted-foreground flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {scorer.team_short_name}
                      </Badge>
                      <span>{scorer.team_name}</span>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="flex items-center gap-6">
                  <div className="text-center hidden sm:block">
                    <div className="text-xs text-muted-foreground">Assist</div>
                    <div className="text-lg font-semibold">{scorer.assists}</div>
                  </div>
                  <div className="text-center hidden sm:block">
                    <div className="text-xs text-muted-foreground">Partite</div>
                    <div className="text-lg font-semibold">{scorer.matches}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-muted-foreground mb-1">GOL</div>
                    <div className="text-3xl font-bold text-primary">
                      {scorer.goals}
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
