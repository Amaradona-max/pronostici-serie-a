'use client'

import { useState } from 'react'
import { Activity, ChevronDown, ChevronUp, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

interface PlayerBiorhythm {
  player_name: string
  position: string
  physical: number
  emotional: number
  intellectual: number
  overall: number
  status: 'excellent' | 'good' | 'low' | 'critical'
}

interface TeamBiorhythmData {
  team_name: string
  avg_physical: number
  avg_emotional: number
  avg_intellectual: number
  avg_overall: number
  players_excellent: number
  players_good: number
  players_low: number
  players_critical: number
  total_players: number
  top_performers: PlayerBiorhythm[]
}

interface BiorhythmsData {
  fixture_id: number
  match_date: string
  home_team_biorhythm: TeamBiorhythmData
  away_team_biorhythm: TeamBiorhythmData
  biorhythm_advantage: 'home' | 'away' | 'neutral'
}

interface TeamBiorhythmsProps {
  fixtureId: number
  homeTeamName: string
  awayTeamName: string
}

export function TeamBiorhythms({
  fixtureId,
  homeTeamName,
  awayTeamName
}: TeamBiorhythmsProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [data, setData] = useState<BiorhythmsData | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchData = async () => {
    if (data) {
      setIsOpen(!isOpen)
      return
    }

    setLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || ''
      const res = await fetch(`${apiUrl}/api/v1/predictions/${fixtureId}/biorhythms`)
      if (!res.ok) throw new Error('Failed to fetch biorhythms')
      const json = await res.json()
      setData(json)
      setIsOpen(true)
    } catch (err) {
      console.error('Error fetching biorhythms:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'excellent':
        return <Badge className="bg-green-500 text-white text-xs">Eccellente</Badge>
      case 'good':
        return <Badge className="bg-blue-500 text-white text-xs">Buono</Badge>
      case 'low':
        return <Badge variant="outline" className="text-xs border-orange-500 text-orange-600">Basso</Badge>
      case 'critical':
        return <Badge variant="destructive" className="text-xs">Critico</Badge>
      default:
        return null
    }
  }

  const getBiorhythmColor = (value: number): string => {
    if (value > 50) return 'text-green-600'
    if (value > 0) return 'text-blue-600'
    if (value > -50) return 'text-orange-600'
    return 'text-red-600'
  }

  const getBiorhythmBg = (value: number): string => {
    if (value > 50) return 'bg-green-500/10 border-green-500/20'
    if (value > 0) return 'bg-blue-500/10 border-blue-500/20'
    if (value > -50) return 'bg-orange-500/10 border-orange-500/20'
    return 'bg-red-500/10 border-red-500/20'
  }

  const getAdvantageIcon = () => {
    if (!data) return null

    if (data.biorhythm_advantage === 'home') {
      return <TrendingUp className="h-4 w-4 text-green-600" />
    } else if (data.biorhythm_advantage === 'away') {
      return <TrendingDown className="h-4 w-4 text-red-600" />
    }
    return <Minus className="h-4 w-4 text-gray-600" />
  }

  const renderTeamBiorhythms = (teamData: TeamBiorhythmData) => {
    return (
      <div>
        <div className="mb-4">
          <h5 className="text-sm font-bold mb-3">{teamData.team_name}</h5>

          {/* Average Biorhythms */}
          <div className="grid grid-cols-2 gap-2 mb-3">
            <div className={`p-2 rounded border ${getBiorhythmBg(teamData.avg_physical)}`}>
              <div className="text-xs text-muted-foreground">Fisico</div>
              <div className={`text-lg font-bold ${getBiorhythmColor(teamData.avg_physical)}`}>
                {teamData.avg_physical > 0 ? '+' : ''}{teamData.avg_physical.toFixed(0)}
              </div>
            </div>
            <div className={`p-2 rounded border ${getBiorhythmBg(teamData.avg_emotional)}`}>
              <div className="text-xs text-muted-foreground">Emotivo</div>
              <div className={`text-lg font-bold ${getBiorhythmColor(teamData.avg_emotional)}`}>
                {teamData.avg_emotional > 0 ? '+' : ''}{teamData.avg_emotional.toFixed(0)}
              </div>
            </div>
            <div className={`p-2 rounded border ${getBiorhythmBg(teamData.avg_intellectual)}`}>
              <div className="text-xs text-muted-foreground">Intellettuale</div>
              <div className={`text-lg font-bold ${getBiorhythmColor(teamData.avg_intellectual)}`}>
                {teamData.avg_intellectual > 0 ? '+' : ''}{teamData.avg_intellectual.toFixed(0)}
              </div>
            </div>
            <div className={`p-2 rounded border ${getBiorhythmBg(teamData.avg_overall)}`}>
              <div className="text-xs text-muted-foreground font-semibold">OVERALL</div>
              <div className={`text-lg font-bold ${getBiorhythmColor(teamData.avg_overall)}`}>
                {teamData.avg_overall > 0 ? '+' : ''}{teamData.avg_overall.toFixed(0)}
              </div>
            </div>
          </div>

          {/* Player Status Distribution */}
          <div className="flex gap-2 text-xs mb-3 flex-wrap">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              <span className="text-muted-foreground">{teamData.players_excellent} eccellenti</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              <span className="text-muted-foreground">{teamData.players_good} buoni</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-orange-500"></div>
              <span className="text-muted-foreground">{teamData.players_low} bassi</span>
            </div>
            {teamData.players_critical > 0 && (
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-red-500"></div>
                <span className="text-muted-foreground">{teamData.players_critical} critici</span>
              </div>
            )}
          </div>

          {/* Player Details */}
          {teamData.top_performers.length > 0 && (
            <div>
              <div className="text-xs text-muted-foreground mb-2 font-semibold">
                Dettaglio Giocatori
              </div>
              <div className="space-y-2">
                {teamData.top_performers.map((player, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 rounded bg-primary/5"
                  >
                    <div className="flex items-center gap-2 flex-1">
                      <span className="text-xs font-bold text-primary w-4">
                        {idx + 1}.
                      </span>
                      <div className="flex-1">
                        <div className="text-sm font-medium">{player.player_name}</div>
                        <div className="text-xs text-muted-foreground">{player.position}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className={`text-lg font-bold ${getBiorhythmColor(player.overall)}`}>
                        {player.overall > 0 ? '+' : ''}{player.overall.toFixed(0)}
                      </div>
                      {getStatusBadge(player.status)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="mt-4 border border-purple-500/20 rounded-lg overflow-hidden">
      {/* Header */}
      <button
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          fetchData()
        }}
        className="w-full p-4 bg-gradient-to-r from-purple-500/10 to-pink-500/10 hover:from-purple-500/15 hover:to-pink-500/15 transition-colors flex items-center justify-between"
      >
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-purple-600" />
          <span className="text-sm font-semibold text-muted-foreground">
            Bioritmi Squadre
          </span>
          {data && getAdvantageIcon()}
        </div>
        {loading ? (
          <div className="animate-spin h-4 w-4 border-2 border-purple-600 border-t-transparent rounded-full" />
        ) : isOpen ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      {/* Content */}
      {isOpen && data && (
        <div className="p-4 bg-background/50">
          {/* Info Banner */}
          <div className="mb-4 p-3 rounded bg-purple-500/5 border border-purple-500/10">
            <p className="text-xs text-muted-foreground">
              <span className="font-semibold">Bioritmi:</span> Analisi dei cicli biologici dei giocatori
              (Fisico 23gg, Emotivo 28gg, Intellettuale 33gg). I valori positivi indicano fase ascendente,
              negativi fase discendente.
            </p>
          </div>

          {/* Advantage Alert */}
          {data.biorhythm_advantage !== 'neutral' && (
            <div className={`mb-4 p-3 rounded ${
              data.biorhythm_advantage === 'home'
                ? 'bg-green-500/10 border border-green-500/20'
                : 'bg-blue-500/10 border border-blue-500/20'
            }`}>
              <div className="flex items-center gap-2">
                {data.biorhythm_advantage === 'home' ? (
                  <TrendingUp className="h-4 w-4 text-green-600" />
                ) : (
                  <TrendingUp className="h-4 w-4 text-blue-600" />
                )}
                <span className="text-sm font-semibold">
                  Vantaggio Bioritmi: {data.biorhythm_advantage === 'home' ? homeTeamName : awayTeamName}
                </span>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {renderTeamBiorhythms(data.home_team_biorhythm)}
            {renderTeamBiorhythms(data.away_team_biorhythm)}
          </div>
        </div>
      )}
    </div>
  )
}
