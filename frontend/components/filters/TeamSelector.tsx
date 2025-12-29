'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface TeamSelectorProps {
  selectedTeam: string | null
  onTeamChange: (team: string | null) => void
}

export function TeamSelector({ selectedTeam, onTeamChange }: TeamSelectorProps) {
  const { data: standings } = useQuery({
    queryKey: ['standings-for-filter'],
    queryFn: () => apiClient.getStandings(),
  })

  return (
    <Select
      value={selectedTeam || 'all'}
      onValueChange={(value) => onTeamChange(value === 'all' ? null : value)}
    >
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Tutte le squadre" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="all">Tutte le squadre</SelectItem>
        {standings?.map((team) => (
          <SelectItem key={team.team_name} value={team.team_name}>
            {team.team_short_name} - {team.team_name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
