import type { AtsType } from '../types/company'

const LABELS: Record<string, string> = {
  auto: 'Auto',
  greenhouse: 'Greenhouse',
  lever: 'Lever',
  ashby: 'Ashby',
  smartrecruiters: 'SmartRecruiters',
  workable: 'Workable',
  workday: 'Workday',
  generic: 'Generic site',
  custom: 'Generic site',
}

export function atsLabel(type: AtsType | string): string {
  return LABELS[type.toLowerCase()] ?? type
}

export const ATS_OPTIONS: { value: AtsType; label: string }[] = [
  { value: 'auto', label: 'Auto-detect from URL' },
  { value: 'greenhouse', label: 'Greenhouse' },
  { value: 'lever', label: 'Lever' },
  { value: 'ashby', label: 'Ashby' },
  { value: 'smartrecruiters', label: 'SmartRecruiters' },
  { value: 'workable', label: 'Workable' },
  { value: 'workday', label: 'Workday' },
  { value: 'generic', label: 'Generic career page' },
]
