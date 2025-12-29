'use client'

import { FixturesList } from '@/components/fixtures/FixturesList'
import { StatsOverview } from '@/components/stats/StatsOverview'
import { TeamSelector } from '@/components/filters/TeamSelector'
import { MatchDetailDropdown } from '@/components/predictions/MatchDetailDropdown'
import { useState } from 'react'

export default function HomePage() {
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null)

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">
          Serie A Predictions 2025/2026
        </h1>
        <p className="text-muted-foreground">
          Pronostici calcistici basati su analisi statistica e machine learning
        </p>
      </div>

      <StatsOverview />

      {/* Analisi Dettagliata Partita */}
      <div className="mt-8">
        <MatchDetailDropdown />
      </div>

      {/* Lista Partite */}
      <div className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">Prossime Partite</h2>
          <TeamSelector
            selectedTeam={selectedTeam}
            onTeamChange={setSelectedTeam}
          />
        </div>
        <FixturesList status="scheduled" limit={20} teamFilter={selectedTeam} />
      </div>
    </div>
  )
}
