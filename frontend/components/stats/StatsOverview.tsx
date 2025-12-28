'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function StatsOverview() {
  // TODO: Fetch real stats from API
  const stats = {
    accuracy: 0.54,
    matches_analyzed: 184,
    model_version: 'v1.2.0',
    last_update: new Date(),
  }

  return (
    <div className="grid gap-4 md:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Accuracy 1X2</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{(stats.accuracy * 100).toFixed(1)}%</div>
          <p className="text-xs text-muted-foreground">
            Ultimi 50 match
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Partite Analizzate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.matches_analyzed}</div>
          <p className="text-xs text-muted-foreground">
            Stagione 2025/26
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Modello</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.model_version}</div>
          <p className="text-xs text-muted-foreground">
            Dixon-Coles
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Ultimo Aggiornamento</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">T-1h</div>
          <p className="text-xs text-muted-foreground">
            Automatico
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
