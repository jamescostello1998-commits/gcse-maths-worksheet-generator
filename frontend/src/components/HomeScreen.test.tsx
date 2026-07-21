import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { HomeScreen } from './HomeScreen'
import type { Section } from '../api/types'

const sections: Section[] = [
  { id: 'number', name: 'Number', groups: [] },
  {
    id: 'algebra',
    name: 'Algebra',
    groups: [
      {
        name: 'Solving Linear Equations',
        topics: [
          {
            id: 'linear_one_step',
            name: 'One-Step Equations',
            description: 'desc',
            fixedTier: 'foundation',
            hasModelledExample: false,
            defaultQuestionCount: 20,
          },
        ],
      },
    ],
  },
]

describe('HomeScreen', () => {
  it('renders all sections including an empty one', () => {
    render(<HomeScreen sections={sections} onSelectSection={vi.fn()} />)
    expect(screen.getByText('Number')).toBeInTheDocument()
    expect(screen.getByText('No topics yet')).toBeInTheDocument()
    expect(screen.getByText('Algebra')).toBeInTheDocument()
    expect(screen.getByText('1 topic')).toBeInTheDocument()
  })

  it('disables the empty section card', () => {
    render(<HomeScreen sections={sections} onSelectSection={vi.fn()} />)
    expect(screen.getByText('Number').closest('button')).toBeDisabled()
  })

  it('calls onSelectSection when a populated section is clicked', async () => {
    const user = userEvent.setup()
    const onSelectSection = vi.fn()
    render(<HomeScreen sections={sections} onSelectSection={onSelectSection} />)
    await user.click(screen.getByText('Algebra'))
    expect(onSelectSection).toHaveBeenCalledWith('algebra')
  })
})
