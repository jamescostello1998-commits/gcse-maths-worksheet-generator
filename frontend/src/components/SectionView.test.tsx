import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { SectionView } from './SectionView'
import type { Section } from '../api/types'

const populatedSection: Section = {
  id: 'geometry',
  name: 'Geometry',
  groups: [
    {
      name: 'Area & Perimeter',
      topics: [
        { id: 'area_rectangle', name: 'Rectangles', description: 'desc', fixedTier: 'foundation', hasModelledExample: false, defaultQuestionCount: 20 },
        { id: 'area_circle', name: 'Circles', description: 'desc', fixedTier: 'higher', hasModelledExample: false, defaultQuestionCount: 20 },
      ],
    },
  ],
}

const singleTierSection: Section = {
  id: 'algebra',
  name: 'Algebra',
  groups: [
    {
      name: 'Solving Linear Equations',
      topics: [
        { id: 'linear_one_step', name: 'One-Step Equations', description: 'desc', fixedTier: 'foundation', hasModelledExample: false, defaultQuestionCount: 20 },
        { id: 'linear_two_step', name: 'Two-Step Equations', description: 'desc', fixedTier: 'foundation', hasModelledExample: false, defaultQuestionCount: 20 },
      ],
    },
  ],
}

const emptySection: Section = { id: 'number', name: 'Number', groups: [] }

describe('SectionView', () => {
  it('shows a Foundation/Higher tier picker before any topics', () => {
    render(<SectionView section={populatedSection} onBack={vi.fn()} />)
    expect(screen.getByText('Geometry')).toBeInTheDocument()
    expect(screen.getByText('Foundation')).toBeInTheDocument()
    expect(screen.getByText('Higher')).toBeInTheDocument()
    expect(screen.queryByText('Rectangles')).not.toBeInTheDocument()
    expect(screen.queryByText('Circles')).not.toBeInTheDocument()
  })

  it('shows only topics for the selected tier, grouped, after picking a tier', async () => {
    const user = userEvent.setup()
    render(<SectionView section={populatedSection} onBack={vi.fn()} />)
    await user.click(screen.getByText('Foundation'))
    expect(screen.getByText('Area & Perimeter')).toBeInTheDocument()
    expect(screen.getByText('Rectangles')).toBeInTheDocument()
    expect(screen.queryByText('Circles')).not.toBeInTheDocument()
  })

  it('disables a tier button when the section has no topics for it', () => {
    render(<SectionView section={singleTierSection} onBack={vi.fn()} />)
    expect(screen.getByText('Foundation').closest('button')).toBeEnabled()
    expect(screen.getByText('Higher').closest('button')).toBeDisabled()
  })

  it('going back from the topic list returns to the tier picker, not Home', async () => {
    const user = userEvent.setup()
    const onBack = vi.fn()
    render(<SectionView section={populatedSection} onBack={onBack} />)
    await user.click(screen.getByText('Foundation'))
    expect(screen.getByText('Rectangles')).toBeInTheDocument()
    await user.click(screen.getByText('← Back'))
    expect(screen.getByText('Foundation')).toBeInTheDocument()
    expect(screen.queryByText('Rectangles')).not.toBeInTheDocument()
    expect(onBack).not.toHaveBeenCalled()
  })

  it('shows an honest empty state for a section with no topics', () => {
    render(<SectionView section={emptySection} onBack={vi.fn()} />)
    expect(screen.getByText(/No topics yet/)).toBeInTheDocument()
  })

  it('calls onBack when the back button is clicked from the tier picker', async () => {
    const user = userEvent.setup()
    const onBack = vi.fn()
    render(<SectionView section={populatedSection} onBack={onBack} />)
    await user.click(screen.getByText('← Back'))
    expect(onBack).toHaveBeenCalled()
  })
})
