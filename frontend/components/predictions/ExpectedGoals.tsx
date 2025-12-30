'use client'

import { TrendingUp } from 'lucide-react'

interface ExpectedGoalsProps {
  homeTeamName: string
  awayTeamName: string
  expectedHomeGoals?: number
  expectedAwayGoals?: number
}

export function ExpectedGoals({
  homeTeamName,
  awayTeamName,
  expectedHomeGoals,
  expectedAwayGoals
}: ExpectedGoalsProps) {
  if (!expectedHomeGoals || !expectedAwayGoals) return null

  return (
    <div className="mt-4 p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/20">
      <div className="flex items-center gap-2 mb-3">
        <TrendingUp className="h-4 w-4 text-purple-600" />
        <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
          Expected Goals (xG)
        </h4>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="text-center">
          <div className="text-xs text-muted-foreground mb-1">
            {homeTeamName}
          </div>
          <div className="text-2xl font-bold text-purple-600">
            {expectedHomeGoals.toFixed(1)}
          </div>
        </div>

        <div className="text-center">
          <div className="text-xs text-muted-foreground mb-1">
            {awayTeamName}
          </div>
          <div className="text-2xl font-bold text-blue-600">
            {expectedAwayGoals.toFixed(1)}
          </div>
        </div>
      </div>

      <div className="mt-3 text-xs text-muted-foreground text-center">
        Gol previsti dal modello predittivo
      </div>
    </div>
  )
}
