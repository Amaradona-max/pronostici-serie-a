'use client'

import { FixturesList } from '@/components/fixtures/FixturesList'
import { TeamSelector } from '@/components/filters/TeamSelector'
import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function PartitePage() {
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null)

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">
          Partite Serie A
        </h1>
        <p className="text-muted-foreground">
          Calendario completo della stagione 2025/2026
        </p>
      </div>

      {/* Filter */}
      <div className="flex items-center justify-end mb-6">
        <TeamSelector
          selectedTeam={selectedTeam}
          onTeamChange={setSelectedTeam}
        />
      </div>

      {/* Tabs for different match statuses */}
      <Tabs defaultValue="scheduled" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-6">
          <TabsTrigger value="scheduled">Prossime</TabsTrigger>
          <TabsTrigger value="live">In Corso</TabsTrigger>
          <TabsTrigger value="finished">Concluse</TabsTrigger>
        </TabsList>

        <TabsContent value="scheduled">
          <div className="mb-4">
            <h2 className="text-2xl font-bold">Prossime Partite</h2>
            <p className="text-sm text-muted-foreground">
              Partite programmate con pronostici AI
            </p>
          </div>
          <FixturesList status="scheduled" limit={50} teamFilter={selectedTeam} />
        </TabsContent>

        <TabsContent value="live">
          <div className="mb-4">
            <h2 className="text-2xl font-bold">Partite in Corso</h2>
            <p className="text-sm text-muted-foreground">
              Aggiornamenti live
            </p>
          </div>
          <FixturesList status="live" limit={20} teamFilter={selectedTeam} />
        </TabsContent>

        <TabsContent value="finished">
          <div className="mb-4">
            <h2 className="text-2xl font-bold">Partite Concluse</h2>
            <p className="text-sm text-muted-foreground">
              Risultati finali
            </p>
          </div>
          <FixturesList status="finished" limit={50} teamFilter={selectedTeam} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
