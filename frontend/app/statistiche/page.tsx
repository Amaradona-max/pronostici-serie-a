'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, TrendingUp, Target, Award, AlertCircle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import { it } from 'date-fns/locale'

// In production (Vercel), we use relative paths to leverage Vercel's internal routing/rewrites.
// In development, we fallback to localhost:8000 if the env var isn't set.
const API_URL = process.env.NODE_ENV === 'production' 
  ? '' 
  : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')

interface PredictionStats {
  total_predictions: number
  accuracy_1x2: number
  accuracy_over_under: number
  accuracy_btts: number
  best_team_predicted: string
  worst_team_predicted: string
  last_week_accuracy: number
  model_version: string
  last_update: string
  avg_confidence: number
  high_confidence_wins: number
  high_confidence_accuracy: number
  medium_confidence_wins: number
  medium_confidence_accuracy: number
  low_confidence_wins: number
  low_confidence_accuracy: number
  best_team_accuracy: number
  best_team_correct: number
  best_team_total: number
  worst_team_accuracy: number
  worst_team_correct: number
  worst_team_total: number
}

async function fetchStats(): Promise<PredictionStats> {
  const res = await fetch(`${API_URL}/api/v1/predictions/stats`)
  if (!res.ok) {
    throw new Error('Failed to fetch stats')
  }
  return res.json()
}

export default function StatistichePage() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['prediction-stats'],
    queryFn: fetchStats,
    refetchInterval: 30000 // Refresh every 30s
  })

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-2 mb-8">
          <div className="h-8 w-8 bg-gray-200 rounded animate-pulse" />
          <div className="h-8 w-64 bg-gray-200 rounded animate-pulse" />
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="h-20" />
              <CardContent className="h-24" />
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="container mx-auto px-4 py-8 text-center text-red-500">
        <AlertCircle className="mx-auto h-12 w-12 mb-4" />
        <p>Errore nel caricamento delle statistiche. Riprova più tardi.</p>
      </div>
    )
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
            <div className="text-3xl font-bold text-green-600">{stats.accuracy_1x2}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              Su {stats.total_predictions} partite analizzate
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Over/Under</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">{stats.accuracy_over_under}%</div>
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
            <div className="text-3xl font-bold text-purple-600">{stats.accuracy_btts}%</div>
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
            <div className="text-3xl font-bold text-orange-600">{stats.last_week_accuracy}%</div>
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
                  <p className="text-2xl font-bold text-green-600">{stats.high_confidence_accuracy}%</p>
                  <p className="text-xs text-muted-foreground">{stats.high_confidence_wins} successi</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Media Affidabilità (50-70%)</p>
                  <p className="text-xs text-muted-foreground">Pronostici con media confidence</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-yellow-600">{stats.medium_confidence_accuracy}%</p>
                  <p className="text-xs text-muted-foreground">{stats.medium_confidence_wins} successi</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Bassa Affidabilità (&lt;50%)</p>
                  <p className="text-xs text-muted-foreground">Pronostici con bassa confidence</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-red-600">{stats.low_confidence_accuracy}%</p>
                  <p className="text-xs text-muted-foreground">{stats.low_confidence_wins} successi</p>
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
                  <p className="text-2xl font-bold">{stats.best_team_predicted}</p>
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
                  <p className="text-2xl font-bold">{stats.worst_team_predicted}</p>
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
              <p className="text-lg font-bold">{stats.model_version}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Ultimo Aggiornamento</p>
              <p className="text-lg font-bold">
                {format(new Date(stats.last_update), "d/MM/yyyy HH:mm", { locale: it })}
              </p>

            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Confidence Media</p>
              <p className="text-lg font-bold">{stats.avg_confidence}%</p>
            </div>
          </div>
          <div className="mt-4 p-4 bg-muted rounded-lg">
            <p className="text-sm">
              <strong>Note:</strong> Il modello Dixon-Coles utilizza rating ELO, statistiche offensive/difensive
              e form recente per calcolare le probabilità. I pronostici vengono aggiornati automaticamente
              in tempo reale.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
