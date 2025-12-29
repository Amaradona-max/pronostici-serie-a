'use client'

import { useEffect, useState } from 'react'

export default function DebugPage() {
  const [apiUrl, setApiUrl] = useState<string>('')
  const [testResult, setTestResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Get API URL from environment
    const url = process.env.NEXT_PUBLIC_API_URL || '/api'
    setApiUrl(url)

    // Test API connection
    const testApi = async () => {
      try {
        const healthUrl = `${url}/api/v1/health`
        console.log('Testing API at:', healthUrl)

        const response = await fetch(healthUrl)
        const data = await response.json()

        setTestResult(data)
      } catch (err: any) {
        setError(err.message)
      }
    }

    testApi()
  }, [])

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Debug Configuration</h1>

      <div className="space-y-6">
        <div className="rounded-lg border p-6">
          <h2 className="text-xl font-semibold mb-2">Environment Variables</h2>
          <div className="space-y-2">
            <div>
              <span className="font-mono text-sm text-muted-foreground">NEXT_PUBLIC_API_URL:</span>
              <p className="font-mono text-lg">{apiUrl}</p>
            </div>
          </div>
        </div>

        <div className="rounded-lg border p-6">
          <h2 className="text-xl font-semibold mb-2">API Health Check</h2>
          <div className="space-y-2">
            <div>
              <span className="font-mono text-sm text-muted-foreground">Testing URL:</span>
              <p className="font-mono text-sm break-all">{apiUrl}/api/v1/health</p>
            </div>

            {error && (
              <div className="rounded bg-destructive/10 border border-destructive p-4">
                <p className="text-destructive font-semibold">Error:</p>
                <p className="font-mono text-sm">{error}</p>
              </div>
            )}

            {testResult && (
              <div className="rounded bg-green-500/10 border border-green-500 p-4">
                <p className="text-green-600 font-semibold mb-2">Success! ✓</p>
                <pre className="font-mono text-sm overflow-auto">
                  {JSON.stringify(testResult, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        <div className="rounded-lg border border-yellow-500 bg-yellow-500/10 p-6">
          <h2 className="text-xl font-semibold mb-2 text-yellow-600">Expected Configuration</h2>
          <p className="mb-2">La variabile deve essere impostata su Vercel come:</p>
          <div className="rounded bg-background p-3 font-mono text-sm">
            <div>Name: <span className="text-blue-500">NEXT_PUBLIC_API_URL</span></div>
            <div>Value: <span className="text-green-500">https://seriea-predictions-api.onrender.com</span></div>
          </div>
          <p className="mt-3 text-sm text-muted-foreground">
            ⚠️ NON includere /api/v1 alla fine - viene aggiunto automaticamente dal codice!
          </p>
        </div>
      </div>
    </div>
  )
}
