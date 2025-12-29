'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, TrendingUp, Target, Award } from 'lucide-react'

export default function StatistichePage() {
  // TODO: Fetch real stats from API
  const stats = {
    totalPredictions: 184,
    accuracy1X2: 54.3,
    accuracyOverUnder: 62.1,
    accuracyBTTS: 58.7,
    bestTeamPredicted: 'Inter',
    worstTeamPredicted: 'Fiorentina',
    lastWeekAccuracy: 70.0,
    modelVersion: 'v1.2.0 (Dixon-Coles)',
    lastUpdate: '29/12/2025 19:53',
    avgConfidence: 67.5,
    highConfidenceWins: 45,
    lowConfidenceWins: 23,
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 flex items-center gap-2">
          <BarChart3 className="h-8 w-8" />
          Statistiche Pronostici
        </h1>
        <p className="text-muted-foreground">
          Performance del modello AI e accuratezza delle predizioni
        </p>
      </div>

      {/* Main Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Accuracy 1X2</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{stats.accuracy1X2}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              Su {stats.totalPredictions} partite analizzate
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Over/Under</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">{stats.accuracyOverUnder}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              Migliore metrica del modello
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">BTTS Accuracy</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">{stats.accuracyBTTS}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              Both Teams To Score
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ultima Giornata</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">{stats.lastWeekAccuracy}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              7/10 pronostici corretti
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Stats */}
      <div className="grid gap-6 md:grid-cols-2 mb-8">
        {/* Performance by Confidence */}
        <Card>
          <CardHeader>
            <CardTitle>Performance per Affidabilità</CardTitle>
            <CardDescription>Rapporto tra confidence del modello e risultati</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Alta Affidabilità (&gt;70%)</p>
                  <p className="text-xs text-muted-foreground">Pronostici con alta confidence</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600">78%</p>
                  <p className="text-xs text-muted-foreground">{stats.highConfidenceWins} successi</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Media Affidabilità (50-70%)</p>
                  <p className="text-xs text-muted-foreground">Pronostici con media confidence</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-yellow-600">56%</p>
                  <p className="text-xs text-muted-foreground">89 successi</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Bassa Affidabilità (&lt;50%)</p>
                  <p className="text-xs text-muted-foreground">Pronostici con bassa confidence</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-red-600">38%</p>
                  <p className="text-xs text-muted-foreground">{stats.lowConfidenceWins} successi</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Best/Worst Teams */}
        <Card>
          <CardHeader>
            <CardTitle>Performance per Squadra</CardTitle>
            <CardDescription>Squadre più e meno prevedibili dal modello</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-green-600">Più Prevedibile</p>
                  <p className="text-2xl font-bold">{stats.bestTeamPredicted}</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500 rounded-full" style={{ width: '85%' }}></div>
                  </div>
                  <span className="text-sm font-medium">85%</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">17/20 pronostici corretti</p>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-red-600">Meno Prevedibile</p>
                  <p className="text-2xl font-bold">{stats.worstTeamPredicted}</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-red-500 rounded-full" style={{ width: '32%' }}></div>
                  </div>
                  <span className="text-sm font-medium">32%</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">6/19 pronostici corretti</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Model Info */}
      <Card>
        <CardHeader>
          <CardTitle>Informazioni Modello</CardTitle>
          <CardDescription>Dettagli tecnici del sistema di predizione</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Modello</p>
              <p className="text-lg font-bold">{stats.modelVersion}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Ultimo Aggiornamento</p>
              <p className="text-lg font-bold">{stats.lastUpdate}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Confidence Media</p>
              <p className="text-lg font-bold">{stats.avgConfidence}%</p>
            </div>
          </div>
          <div className="mt-4 p-4 bg-muted rounded-lg">
            <p className="text-sm">
              <strong>Note:</strong> Il modello Dixon-Coles utilizza rating ELO, statistiche offensive/difensive
              e form recente per calcolare le probabilità. I pronostici vengono aggiornati automaticamente
              1 ora prima dell&apos;inizio di ogni partita.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
