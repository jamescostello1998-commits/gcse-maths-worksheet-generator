import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { SectionView } from './SectionView'
import type { Section } from '../api/types'

const populatedSection: Section = {
  id: 'algebra',
  name: 'Algebra',
  groups: [
    {
      name: 'Solving Linear Equations',
      topics: [
        { id: 'linear_one_step', name: 'One-Step Equations', description: 'desc', fixedTier: 'foundation' },
        { id: 'linear_two_step', name: 'Two-Step Equations', description: 'desc', fixedTier: 'foundation' },
      ],
    },
  ],
}

const emptySection: Section = { id: 'number', name: 'Number', groups: [] }

describe('SectionView', () => {
  it('renders groups and topic cards', () => {
    render(<SectionView section={populatedSection} onBack={vi.fn()} />)
    expect(screen.getByText('Algebra')).toBeInTheDocument()
    expect(screen.getByText('Solving Linear Equations')).toBeInTheDocument()
    expect(screen.getByText('One-Step Equations')).toBeInTheDocument()
    expect(screen.getByText('Two-Step Equations')).toBeInTheDocument()
  })

  it('shows an honest empty state for a section with no topics', () => {
    render(<SectionView section={emptySection} onBack={vi.fn()} />)
    expect(screen.getByText(/No topics yet/)).toBeInTheDocument()
  })

  it('calls onBack when the back button is clicked', async () => {
    const user = userEvent.setup()
    const onBack = vi.fn()
    render(<SectionView section={populatedSection} onBack={onBack} />)
    await user.click(screen.getByText('← Back'))
    expect(onBack).toHaveBeenCalled()
  })
})
