import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { TopicSearch } from './TopicSearch'
import type { Section } from '../api/types'

const sections: Section[] = [
  {
    id: 'ratio_proportion',
    name: 'Ratio & Proportion',
    groups: [
      {
        name: 'Percentages',
        topics: [
          { id: 'percentage_of_amount', name: 'Percentage of an Amount', description: 'desc1', fixedTier: 'foundation', hasModelledExample: false, defaultQuestionCount: 20 },
        ],
      },
      {
        name: 'Ratio',
        topics: [
          { id: 'ratio_share_two_part', name: 'Share a Two-Part Ratio', description: 'desc2', fixedTier: 'foundation', hasModelledExample: false, defaultQuestionCount: 20 },
        ],
      },
    ],
  },
]

describe('TopicSearch', () => {
  it('shows all topics with breadcrumbs when query is empty', () => {
    render(<TopicSearch sections={sections} query="" />)
    expect(screen.getByText('Percentage of an Amount')).toBeInTheDocument()
    expect(screen.getByText('Share a Two-Part Ratio')).toBeInTheDocument()
    expect(screen.getByText('Ratio & Proportion › Percentages')).toBeInTheDocument()
    expect(screen.getByText('Ratio & Proportion › Ratio')).toBeInTheDocument()
  })

  it('filters topics by query', () => {
    render(<TopicSearch sections={sections} query="percentage" />)
    expect(screen.getByText('Percentage of an Amount')).toBeInTheDocument()
    expect(screen.queryByText('Share a Two-Part Ratio')).not.toBeInTheDocument()
  })

  it('shows an empty state when nothing matches', () => {
    render(<TopicSearch sections={sections} query="zzz" />)
    expect(screen.getByText(/No topics match/)).toBeInTheDocument()
  })
})
