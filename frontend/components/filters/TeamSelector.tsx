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
  const { data: teams } = useQuery({
    queryKey: ['teams-for-filter'],
    queryFn: () => apiClient.getTeams(),
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
        {teams?.map((team) => (
          <SelectItem key={team.name} value={team.name}>
            {team.short_name || team.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
