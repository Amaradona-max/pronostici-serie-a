// Use environment variable for API URL, fallback to /api for local dev
// In production (Vercel), we use relative paths to leverage Vercel's internal routing/rewrites.
// In development, we fallback to localhost:8000 if the env var isn't set.
const API_URL = process.env.NODE_ENV === 'production' 
  ? '' 
  : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')

// Types
export interface Team {
  id: number
  name: string
  short_name?: string
  logo_url?: string
  stadium_name?: string
  stadium_capacity?: number
}

export interface Fixture {
  id: number
  home_team: Team
  away_team: Team
  match_date: string
  status: 'scheduled' | 'live' | 'finished' | 'postponed' | 'cancelled'
  home_score?: number
  away_score?: number
  round?: string
  season?: string
}

export interface Prediction {
  id: number
  fixture_id: number
  prob_home_win: number
  prob_draw: number
  prob_away_win: number
  prob_over_25: number
  prob_under_25: number
  prob_btts_yes: number
  prob_btts_no: number
  most_likely_score?: string
  most_likely_score_prob?: number
  expected_home_goals?: number
  expected_away_goals?: number
  confidence_score: number
  computed_at: string
}

export interface FixtureWithPrediction extends Fixture {
  prediction?: Prediction
}

export interface FixturesResponse {
  fixtures: FixtureWithPrediction[]
  total: number
  page: number
  page_size: number
}

export interface HealthResponse {
  status: string
  timestamp: string
  version: string
  services: {
    database: string
    redis: string
  }
}

export interface StatsOverview {
  total_predictions: number
  accuracy_1x2: number
  avg_brier_score: number
  total_fixtures: number
  upcoming_fixtures: number
}

// API Client
class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error(`API Error [${response.status}]: ${url}`, errorText)
        throw new Error(`API Error: ${response.status} ${response.statusText}`)
      }

      return response.json()
    } catch (error) {
      console.error('API Request Failed:', {
        url,
        baseUrl: this.baseUrl,
        endpoint,
        error
      })
      throw error
    }
  }

  // Health
  async getHealth(): Promise<HealthResponse> {
    return this.request('/api/v1/health')
  }

  // Fixtures
  async getFixtures(params?: {
    status?: string
    round?: string
    season?: string
    page?: number
    page_size?: number
  }): Promise<FixtureWithPrediction[]> {
    const season = params?.season || '2025-2026'
    const queryParams = new URLSearchParams()
    if (params?.status) queryParams.append('status', params.status)
    if (params?.round) queryParams.append('round', params.round)
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString())

    const query = queryParams.toString()
    const response = await this.request<FixturesResponse>(
      `/api/v1/fixtures/serie-a/${season}${query ? `?${query}` : ''}`
    )
    return response.fixtures
  }

  async getFixture(id: number): Promise<FixtureWithPrediction> {
    return this.request(`/api/v1/fixtures/${id}`)
  }

  // Predictions
  async getPrediction(fixtureId: number): Promise<Prediction> {
    return this.request(`/api/v1/predictions/${fixtureId}`)
  }

  // Stats
  async getStatsOverview(): Promise<StatsOverview> {
    return this.request('/stats/overview')
  }

  // Teams
  async getTeams(): Promise<Team[]> {
    return this.request('/api/v1/teams')
  }

  async getTeam(id: number): Promise<Team> {
    return this.request(`/api/v1/teams/${id}`)
  }
}

export const apiClient = new ApiClient(API_URL)
