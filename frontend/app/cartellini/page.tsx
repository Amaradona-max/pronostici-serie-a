'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, AlertCircle, Shield, User } from 'lucide-react'
import { useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api'

interface PlayerCard {
  player_name: string
  team_name: string
  team_short_name: string
  yellow_cards: number
  red_cards: number
  total_cards: number
  is_suspended: boolean
}

interface TeamCards {
  team_name: string
  team_short_name: string
  yellow_cards: number
  red_cards: number
  total_cards: number
  players: PlayerCard[]
}

export default function CartelliniPage() {
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null)

  const { data: teamsCards, isLoading } = useQuery({
    queryKey: ['cards'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/v1/standings/cards/2025-2026`)
      if (!res.ok) throw new Error('Failed to fetch cards')
      return res.json() as Promise<TeamCards[]>
    },
    refetchInterval: 5 * 60 * 1000,
  })

  const getCardRiskLevel = (yellowCards: number, redCards: number) => {
    if (redCards >= 1) return { level: 'critical', color: 'bg-red-600', text: 'Squalificato' }
    if (yellowCards >= 4) return { level: 'warning', color: 'bg-orange-600', text: 'A rischio' }
    if (yellowCards >= 2) return { level: 'caution', color: 'bg-yellow-600', text: 'Attenzione' }
    return { level: 'safe', color: 'bg-green-600', text: 'Regolare' }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-32 bg-muted rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  // Get at-risk players across all teams
  const atRiskPlayers = teamsCards?.flatMap(team =>
    team.players.filter(p => p.yellow_cards >= 3 || p.red_cards >= 1)
  ) || []

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <Shield className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold">Situazione Cartellini</h1>
        </div>
        <p className="text-muted-foreground">
          Cartellini gialli e rossi - Giocatori a rischio squalifica
        </p>
      </div>

      {/* Alert Box - At Risk Players */}
      {atRiskPlayers.length > 0 && (
        <Card className="mb-6 border-orange-500/50 bg-orange-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span>Giocatori a Rischio Squalifica</span>
              <Badge variant="destructive">{atRiskPlayers.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {atRiskPlayers.map((player, idx) => {
                const risk = getCardRiskLevel(player.yellow_cards, player.red_cards)
                return (
                  <div key={idx} className="flex items-center gap-3 p-3 rounded-lg bg-background border">
                    <AlertCircle className={`h-5 w-5 ${player.is_suspended ? 'text-red-600' : 'text-orange-600'}`} />
                    <div className="flex-1">
                      <div className="font-semibold">{player.player_name}</div>
                      <div className="text-xs text-muted-foreground">{player.team_short_name}</div>
                    </div>
                    <div className="flex gap-1">
                      {[...Array(player.yellow_cards)].map((_, i) => (
                        <div key={i} className="w-3 h-4 bg-yellow-400 rounded-sm" />
                      ))}
                      {[...Array(player.red_cards)].map((_, i) => (
                        <div key={i} className="w-3 h-4 bg-red-600 rounded-sm" />
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Legend */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-4 bg-yellow-400 rounded-sm" />
              <span>Ammonizione</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-4 bg-red-600 rounded-sm" />
              <span>Espulsione</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge className="bg-red-600">Squalificato</Badge>
              <span>1+ Rossi o 5+ Gialli</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge className="bg-orange-600">A rischio</Badge>
              <span>4 Gialli</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Teams Cards */}
      <div className="space-y-4">
        {teamsCards?.map((team) => (
          <Card
            key={team.team_name}
            className="group hover:shadow-lg transition-all duration-300 cursor-pointer"
            onClick={() => setSelectedTeam(selectedTeam === team.team_name ? null : team.team_name)}
          >
            <CardContent className="p-6">
              {/* Team Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
                    <span className="font-bold text-primary">{team.team_short_name}</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold group-hover:text-primary transition-colors">
                      {team.team_name}
                    </h3>
                    <div className="text-sm text-muted-foreground">
                      {team.players.length} giocatori monitorati
                    </div>
                  </div>
                </div>

                {/* Team Totals */}
                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <div className="flex items-center gap-1 justify-center mb-1">
                      <div className="w-4 h-5 bg-yellow-400 rounded-sm" />
                      <span className="text-xs text-muted-foreground">Gialli</span>
                    </div>
                    <div className="text-2xl font-bold">{team.yellow_cards}</div>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center gap-1 justify-center mb-1">
                      <div className="w-4 h-5 bg-red-600 rounded-sm" />
                      <span className="text-xs text-muted-foreground">Rossi</span>
                    </div>
                    <div className="text-2xl font-bold text-red-600">{team.red_cards}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-muted-foreground mb-1">Totale</div>
                    <div className="text-2xl font-bold text-primary">{team.total_cards}</div>
                  </div>
                </div>
              </div>

              {/* Players List - Expandable */}
              {selectedTeam === team.team_name && (
                <div className="mt-6 pt-6 border-t space-y-2">
                  {team.players.map((player, idx) => {
                    const risk = getCardRiskLevel(player.yellow_cards, player.red_cards)
                    return (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <User className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <div className="font-semibold">{player.player_name}</div>
                            {player.is_suspended && (
                              <Badge variant="destructive" className="text-xs mt-1">
                                Squalificato
                              </Badge>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-4">
                          <div className="flex gap-1">
                            {[...Array(player.yellow_cards)].map((_, i) => (
                              <div key={`y-${i}`} className="w-4 h-5 bg-yellow-400 rounded-sm shadow" />
                            ))}
                            {[...Array(player.red_cards)].map((_, i) => (
                              <div key={`r-${i}`} className="w-4 h-5 bg-red-600 rounded-sm shadow" />
                            ))}
                          </div>
                          <Badge className={risk.color}>
                            {risk.text}
                          </Badge>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}

              {/* Click to expand indicator */}
              {selectedTeam !== team.team_name && (
                <div className="mt-4 text-center text-sm text-muted-foreground">
                  Clicca per vedere i giocatori
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
