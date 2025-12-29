'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Minus, AlertCircle, Target } from 'lucide-react'
import { apiClient, type FixtureWithPrediction } from '@/lib/api'

export function MatchDetailDropdown() {
  const [selectedMatchId, setSelectedMatchId] = useState<string>('')

  const { data: fixtures } = useQuery({
    queryKey: ['fixtures', 'serie-a', '2025-2026', 'scheduled'],
    queryFn: async () => {
      const response = await apiClient.getFixtures({
        season: '2025-2026',
        status: 'scheduled',
        page: 1,
        page_size: 20
      })
      return response
    },
  })
  const selectedMatch = fixtures?.find(f => f.id.toString() === selectedMatchId)

  return (
    <div className="space-y-6">
      {/* Dropdown per selezionare la partita */}
      <Card>
        <CardHeader>
          <CardTitle>Analisi Dettagliata Partita</CardTitle>
          <CardDescription>
            Seleziona una partita per vedere il pronostico completo e le statistiche
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select value={selectedMatchId} onValueChange={setSelectedMatchId}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Seleziona una partita..." />
            </SelectTrigger>
            <SelectContent>
              {fixtures?.map((fixture) => (
                <SelectItem key={fixture.id} value={fixture.id.toString()}>
                  {fixture.home_team.name} vs {fixture.away_team.name} -{' '}
                  {new Date(fixture.match_date).toLocaleDateString('it-IT', {
                    day: 'numeric',
                    month: 'short',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Dettaglio Partita Selezionata */}
      {selectedMatch && (
        <div className="space-y-6">
          {/* Header Partita */}
          <Card className="border-2">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex-1 text-center">
                  <h3 className="text-2xl font-bold">{selectedMatch.home_team.name}</h3>
                  <Badge variant="secondary" className="mt-2">Casa</Badge>
                </div>
                <div className="px-8">
                  <div className="text-4xl font-bold text-muted-foreground">VS</div>
                  <div className="text-xs text-center text-muted-foreground mt-2">
                    {new Date(selectedMatch.match_date).toLocaleDateString('it-IT', {
                      day: 'numeric',
                      month: 'long',
                    })}
                  </div>
                  <div className="text-xs text-center font-medium">
                    {new Date(selectedMatch.match_date).toLocaleTimeString('it-IT', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </div>
                </div>
                <div className="flex-1 text-center">
                  <h3 className="text-2xl font-bold">{selectedMatch.away_team.name}</h3>
                  <Badge variant="outline" className="mt-2">Trasferta</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pronostico Dettagliato */}
          {selectedMatch.prediction ? (
            <>
              {/* Probabilità 1X2 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Probabilità Risultato (1X2)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Vittoria Casa */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">1 - Vittoria {selectedMatch.home_team.short_name}</span>
                        <span className="text-2xl font-bold text-green-600">
                          {(selectedMatch.prediction.prob_home_win * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500 rounded-full transition-all"
                          style={{ width: `${selectedMatch.prediction.prob_home_win * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Pareggio */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">X - Pareggio</span>
                        <span className="text-2xl font-bold text-yellow-600">
                          {(selectedMatch.prediction.prob_draw * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-yellow-500 rounded-full transition-all"
                          style={{ width: `${selectedMatch.prediction.prob_draw * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Vittoria Trasferta */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">2 - Vittoria {selectedMatch.away_team.short_name}</span>
                        <span className="text-2xl font-bold text-blue-600">
                          {(selectedMatch.prediction.prob_away_win * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full transition-all"
                          style={{ width: `${selectedMatch.prediction.prob_away_win * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  {/* Pronostico Consigliato */}
                  <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 rounded-lg border-2 border-blue-300 dark:border-blue-700">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Pronostico Consigliato</p>
                        <p className="text-2xl font-bold mt-1">
                          {selectedMatch.prediction.prob_home_win > selectedMatch.prediction.prob_away_win &&
                          selectedMatch.prediction.prob_home_win > selectedMatch.prediction.prob_draw
                            ? `1 - ${selectedMatch.home_team.short_name}`
                            : selectedMatch.prediction.prob_away_win > selectedMatch.prediction.prob_draw
                            ? `2 - ${selectedMatch.away_team.short_name}`
                            : 'X - Pareggio'}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-muted-foreground">Affidabilità</p>
                        <Badge variant={selectedMatch.prediction.confidence_score > 0.7 ? 'default' : 'secondary'} className="mt-1">
                          {(selectedMatch.prediction.confidence_score * 100).toFixed(0)}%
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Altri Mercati */}
              <div className="grid gap-6 md:grid-cols-2">
                {/* Risultato Esatto */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Target className="h-5 w-5" />
                      Risultato Più Probabile
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center">
                      <div className="text-5xl font-bold text-primary mb-2">
                        {selectedMatch.prediction.most_likely_score}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Basato su expected goals
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Over/Under 2.5 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <TrendingUp className="h-5 w-5" />
                      Over/Under 2.5 Gol
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Over 2.5</span>
                        <span className="text-xl font-bold">
                          {(selectedMatch.prediction.prob_over_25 * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Under 2.5</span>
                        <span className="text-xl font-bold">
                          {(selectedMatch.prediction.prob_under_25 * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="mt-4 p-3 bg-muted rounded-lg">
                        <p className="text-sm font-medium">
                          Consiglio:{' '}
                          <span className="text-primary">
                            {selectedMatch.prediction.prob_over_25 > selectedMatch.prediction.prob_under_25 ? 'Over 2.5' : 'Under 2.5'}
                          </span>
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* BTTS (Both Teams To Score) */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Target className="h-5 w-5" />
                      Goal (BTTS)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Entrambe Segnano (GG)</span>
                        <span className="text-xl font-bold text-green-600">
                          {(selectedMatch.prediction.prob_btts_yes * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Almeno una Non Segna (NG)</span>
                        <span className="text-xl font-bold text-red-600">
                          {(selectedMatch.prediction.prob_btts_no * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="mt-4 p-3 bg-muted rounded-lg">
                        <p className="text-sm font-medium">
                          Consiglio:{' '}
                          <span className="text-primary">
                            {selectedMatch.prediction.prob_btts_yes > selectedMatch.prediction.prob_btts_no ? 'GG (Goal/Goal)' : 'NG (No Goal)'}
                          </span>
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Confidence Level */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <AlertCircle className="h-5 w-5" />
                      Livello di Affidabilità
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center">
                      <div className="text-5xl font-bold mb-2">
                        {(selectedMatch.prediction.confidence_score * 100).toFixed(0)}%
                      </div>
                      <Badge
                        variant={
                          selectedMatch.prediction.confidence_score > 0.7
                            ? 'default'
                            : selectedMatch.prediction.confidence_score > 0.5
                            ? 'secondary'
                            : 'outline'
                        }
                        className="text-base px-4 py-1"
                      >
                        {selectedMatch.prediction.confidence_score > 0.7
                          ? 'Alta Affidabilità'
                          : selectedMatch.prediction.confidence_score > 0.5
                          ? 'Media Affidabilità'
                          : 'Bassa Affidabilità'}
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-4">
                        Basato su rating ELO, forma recente e statistiche offensive/difensive
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Note e Disclaimer */}
              <Card className="border-yellow-500/50 bg-yellow-50 dark:bg-yellow-950/20">
                <CardContent className="pt-6">
                  <div className="flex gap-3">
                    <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div className="space-y-2 text-sm">
                      <p className="font-medium">Note Importanti:</p>
                      <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                        <li>I pronostici sono generati da algoritmi statistici e non garantiscono il risultato</li>
                        <li>Le probabilità vengono aggiornate 1 ora prima dell&apos;inizio della partita</li>
                        <li>Considera sempre altri fattori: infortuni, squalifiche, motivazioni</li>
                        <li>Gioca responsabilmente</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-8">
                  <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-lg font-medium">Nessun pronostico disponibile</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    I pronostici verranno generati 1 ora prima dell&apos;inizio della partita
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Placeholder quando nessuna partita selezionata */}
      {!selectedMatch && (
        <Card className="border-dashed">
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <TrendingUp className="h-16 w-16 text-muted-foreground/50 mx-auto mb-4" />
              <p className="text-lg font-medium text-muted-foreground">
                Seleziona una partita per vedere l&apos;analisi dettagliata
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
