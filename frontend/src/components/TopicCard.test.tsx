import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { TopicCard } from './TopicCard'
import type { Topic } from '../api/types'

const fixedTopic: Topic = {
  id: 'linear_one_step',
  name: 'One-Step Equations',
  description: 'Solve simple equations.',
  fixedTier: 'foundation',
  hasModelledExample: false,
}

const flexibleTopic: Topic = {
  id: 'some_future_topic',
  name: 'Future Topic',
  description: 'Supports both tiers.',
  fixedTier: null,
  hasModelledExample: false,
}

const modelledTopic: Topic = {
  id: 'linear_two_step',
  name: 'Two-Step Equations',
  description: 'Solve equations of the form ax + b = c.',
  fixedTier: 'foundation',
  hasModelledExample: true,
}

describe('TopicCard', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    URL.revokeObjectURL = vi.fn()
  })

  it('shows a fixed tier badge and no toggle when fixedTier is set', () => {
    render(<TopicCard topic={fixedTopic} />)
    expect(screen.getByText('Foundation')).toBeInTheDocument()
    expect(screen.queryByRole('radiogroup')).not.toBeInTheDocument()
  })

  it('hides the tier badge when showTierBadge is false', () => {
    render(<TopicCard topic={fixedTopic} showTierBadge={false} />)
    expect(screen.queryByText('Foundation')).not.toBeInTheDocument()
  })

  it('shows a tier toggle when fixedTier is null', () => {
    render(<TopicCard topic={flexibleTopic} />)
    expect(screen.getByRole('radiogroup')).toBeInTheDocument()
  })

  it('generates a worksheet with the fixed tier on click', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['%PDF-'], { type: 'application/pdf' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(<TopicCard topic={fixedTopic} />)
    await user.click(screen.getByText('Worksheet'))

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/worksheets'),
      expect.objectContaining({
        body: JSON.stringify({ topic_id: 'linear_one_step', tier: 'foundation' }),
      }),
    )
  })

  it('generates with the selected tier from the mini toggle', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['%PDF-'], { type: 'application/pdf' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(<TopicCard topic={flexibleTopic} />)
    await user.click(screen.getByText('H'))
    await user.click(screen.getByText('Worksheet'))

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/worksheets'),
      expect.objectContaining({
        body: JSON.stringify({ topic_id: 'some_future_topic', tier: 'higher' }),
      }),
    )
  })

  it('does not show a modelled example button when hasModelledExample is false', () => {
    render(<TopicCard topic={fixedTopic} />)
    expect(screen.queryByText('Modelled Example')).not.toBeInTheDocument()
  })

  it('shows and generates a modelled example when hasModelledExample is true', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['%PDF-'], { type: 'application/pdf' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(<TopicCard topic={modelledTopic} />)
    await user.click(screen.getByText('Modelled Example'))

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/modelled-examples'),
      expect.objectContaining({
        body: JSON.stringify({ topic_id: 'linear_two_step', tier: 'foundation' }),
      }),
    )
  })
})
