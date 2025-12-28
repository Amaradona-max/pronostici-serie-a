import { FixturesList } from '../components/fixtures/FixturesList'
import { StatsOverview } from '../components/stats/StatsOverview'

export default function HomePage() {
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

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Prossime Partite</h2>
        <FixturesList status="scheduled" limit={10} />
      </div>
    </div>
  )
}
