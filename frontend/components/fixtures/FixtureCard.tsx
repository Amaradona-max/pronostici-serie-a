'use client'

import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/utils'
import { ChevronRight, Calendar, Clock } from 'lucide-react'
import type { FixtureWithPrediction } from '@/lib/api'
import { ExpectedGoals } from '@/components/predictions/ExpectedGoals'
import { ScorerProbabilities } from '@/components/predictions/ScorerProbabilities'
import { ProbableLineups } from '@/components/predictions/ProbableLineups'
import { TeamBiorhythms } from '@/components/predictions/TeamBiorhythms'

interface FixtureCardProps {
  fixture: FixtureWithPrediction
}

export function FixtureCard({ fixture }: FixtureCardProps) {
  const matchDate = new Date(fixture.match_date)

  // Format date and time
  const dateStr = matchDate.toLocaleDateString('it-IT', {
    weekday: 'short',
    day: 'numeric',
    month: 'short'
  })
  const timeStr = matchDate.toLocaleTimeString('it-IT', {
    hour: '2-digit',
    minute: '2-digit'
  })

  // Status badge configuration
  const getStatusBadge = () => {
    switch (fixture.status) {
      case 'scheduled':
        return <Badge variant="outline" className="bg-blue-500/10 text-blue-600 border-blue-500/20">Programmata</Badge>
      case 'live':
        return <Badge className="bg-green-500 text-white animate-pulse">● Live</Badge>
      case 'finished':
        return <Badge variant="outline" className="bg-gray-500/10 text-gray-600 border-gray-500/20">Terminata</Badge>
      default:
        return null
    }
  }

  return (
    <Link href={`/partite/${fixture.id}`}>
      <Card className="group hover:shadow-xl hover:scale-[1.02] transition-all duration-300 cursor-pointer border-2 hover:border-primary/50 overflow-hidden">
        <CardContent className="p-0">
          {/* Header with gradient */}
          <div className="bg-gradient-to-r from-primary/5 via-primary/10 to-primary/5 p-4 border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span className="font-medium">{dateStr}</span>
                <span className="text-muted-foreground/50">•</span>
                <Clock className="h-4 w-4" />
                <span className="font-medium">{timeStr}</span>
              </div>
              {fixture.round && (
                <Badge variant="secondary" className="font-semibold">
                  {fixture.round}
                </Badge>
              )}
            </div>
          </div>

          {/* Teams section */}
          <div className="p-6">
            <div className="space-y-4">
              {/* Home Team */}
              <div className="flex items-center justify-between group-hover:translate-x-1 transition-transform">
                <div className="flex items-center gap-3 flex-1">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center flex-shrink-0">
                    <span className="text-lg font-bold text-primary">
                      {fixture.home_team.short_name || fixture.home_team.name.substring(0, 3).toUpperCase()}
                    </span>
                  </div>
                  <span className="font-bold text-lg group-hover:text-primary transition-colors">
                    {fixture.home_team.name}
                  </span>
                </div>
                {fixture.status === 'finished' && fixture.home_score !== null && (
                  <span className="text-3xl font-bold text-primary ml-4">{fixture.home_score}</span>
                )}
              </div>

              {/* VS divider */}
              <div className="flex items-center gap-3">
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
                <span className="text-xs font-semibold text-muted-foreground px-2">VS</span>
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
              </div>

              {/* Away Team */}
              <div className="flex items-center justify-between group-hover:translate-x-1 transition-transform">
                <div className="flex items-center gap-3 flex-1">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-secondary/20 to-secondary/5 flex items-center justify-center flex-shrink-0">
                    <span className="text-lg font-bold text-secondary">
                      {fixture.away_team.short_name || fixture.away_team.name.substring(0, 3).toUpperCase()}
                    </span>
                  </div>
                  <span className="font-bold text-lg group-hover:text-primary transition-colors">
                    {fixture.away_team.name}
                  </span>
                </div>
                {fixture.status === 'finished' && fixture.away_score !== null && (
                  <span className="text-3xl font-bold text-primary ml-4">{fixture.away_score}</span>
                )}
              </div>
            </div>

            {/* Predictions Section (if available and scheduled) */}
            {fixture.status === 'scheduled' && fixture.prediction && (
              <div className="mt-6 p-4 rounded-lg bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/10">
                <h4 className="text-xs font-semibold text-muted-foreground mb-3 uppercase tracking-wide">
                  Pronostico AI
                </h4>
                <div className="grid grid-cols-3 gap-3 mb-3">
                  <div className="text-center p-2 rounded bg-background/50">
                    <div className="text-xs text-muted-foreground mb-1">1</div>
                    <div className="text-lg font-bold text-primary">
                      {(fixture.prediction.prob_home_win * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="text-center p-2 rounded bg-background/50">
                    <div className="text-xs text-muted-foreground mb-1">X</div>
                    <div className="text-lg font-bold">
                      {(fixture.prediction.prob_draw * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="text-center p-2 rounded bg-background/50">
                    <div className="text-xs text-muted-foreground mb-1">2</div>
                    <div className="text-lg font-bold text-secondary">
                      {(fixture.prediction.prob_away_win * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">
                    Risultato previsto: <span className="font-bold">{fixture.prediction.most_likely_score}</span>
                  </span>
                  <Badge variant="outline" className="text-xs">
                    Affidabilità {(fixture.prediction.confidence_score * 100).toFixed(0)}%
                  </Badge>
                </div>

                {/* Expected Goals */}
                <ExpectedGoals
                  homeTeamName={fixture.home_team.short_name || fixture.home_team.name}
                  awayTeamName={fixture.away_team.short_name || fixture.away_team.name}
                  expectedHomeGoals={fixture.prediction.expected_home_goals}
                  expectedAwayGoals={fixture.prediction.expected_away_goals}
                />

                {/* Scorer Probabilities */}
                <ScorerProbabilities
                  fixtureId={fixture.id}
                  homeTeamName={fixture.home_team.name}
                  awayTeamName={fixture.away_team.name}
                />

                {/* Probable Lineups */}
                <ProbableLineups
                  fixtureId={fixture.id}
                  homeTeamName={fixture.home_team.name}
                  awayTeamName={fixture.away_team.name}
                  matchDate={fixture.match_date}
                />

                {/* Team Biorhythms */}
                <TeamBiorhythms
                  fixtureId={fixture.id}
                  homeTeamName={fixture.home_team.name}
                  awayTeamName={fixture.away_team.name}
                />
              </div>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between mt-6 pt-4 border-t">
              {getStatusBadge()}
              <div className="flex items-center gap-2 text-sm text-muted-foreground group-hover:text-primary transition-colors">
                <span className="font-medium">Dettagli</span>
                <ChevronRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
