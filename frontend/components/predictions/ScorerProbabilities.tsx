'use client'

import { useState } from 'react'
import { Target, ChevronDown, ChevronUp } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

interface ScorerProb {
  player_name: string
  position: string
  probability: number
}

interface ScorerProbabilitiesProps {
  fixtureId: number
  homeTeamName: string
  awayTeamName: string
}

export function ScorerProbabilities({
  fixtureId,
  homeTeamName,
  awayTeamName
}: ScorerProbabilitiesProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [data, setData] = useState<{
    home_team_scorers: ScorerProb[]
    away_team_scorers: ScorerProb[]
  } | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchData = async () => {
    if (data) {
      setIsOpen(!isOpen)
      return
    }

    setLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || ''
      const res = await fetch(`${apiUrl}/api/v1/predictions/${fixtureId}/scorer-probabilities`)
      const json = await res.json()
      setData(json)
      setIsOpen(true)
    } catch (err) {
      console.error('Error fetching scorer probabilities:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-4 border border-orange-500/20 rounded-lg overflow-hidden">
      {/* Header - Always visible */}
      <button
        onClick={fetchData}
        className="w-full p-4 bg-gradient-to-r from-orange-500/10 to-red-500/10 hover:from-orange-500/15 hover:to-red-500/15 transition-colors flex items-center justify-between"
      >
        <div className="flex items-center gap-2">
          <Target className="h-4 w-4 text-orange-600" />
          <span className="text-sm font-semibold text-muted-foreground">
            Probabilità Marcatori Top 5
          </span>
        </div>
        {loading ? (
          <div className="animate-spin h-4 w-4 border-2 border-orange-600 border-t-transparent rounded-full" />
        ) : isOpen ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      {/* Collapsible Content */}
      {isOpen && data && (
        <div className="p-4 bg-background/50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Home Team */}
            <div>
              <h5 className="text-xs font-bold text-primary mb-3">
                {homeTeamName}
              </h5>
              <div className="space-y-2">
                {data.home_team_scorers.map((scorer, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 rounded bg-primary/5 hover:bg-primary/10 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-primary w-4">
                        {idx + 1}.
                      </span>
                      <div>
                        <div className="text-sm font-medium">
                          {scorer.player_name}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {scorer.position}
                        </div>
                      </div>
                    </div>
                    <Badge variant="outline" className="bg-orange-500/10 text-orange-600 border-orange-500/20">
                      {(scorer.probability * 100).toFixed(0)}%
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            {/* Away Team */}
            <div>
              <h5 className="text-xs font-bold text-secondary mb-3">
                {awayTeamName}
              </h5>
              <div className="space-y-2">
                {data.away_team_scorers.map((scorer, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 rounded bg-secondary/5 hover:bg-secondary/10 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-secondary w-4">
                        {idx + 1}.
                      </span>
                      <div>
                        <div className="text-sm font-medium">
                          {scorer.player_name}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {scorer.position}
                        </div>
                      </div>
                    </div>
                    <Badge variant="outline" className="bg-orange-500/10 text-orange-600 border-orange-500/20">
                      {(scorer.probability * 100).toFixed(0)}%
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
