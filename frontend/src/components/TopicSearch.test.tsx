import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { TopicSearch } from './TopicSearch'

const topics = [
  { id: 'percentages', name: 'Percentages', description: 'desc1' },
  { id: 'ratio', name: 'Ratio', description: 'desc2' },
]

describe('TopicSearch', () => {
  it('renders all topics by default', () => {
    render(<TopicSearch topics={topics} selectedTopicId={null} onSelect={vi.fn()} />)
    expect(screen.getByText('Percentages')).toBeInTheDocument()
    expect(screen.getByText('Ratio')).toBeInTheDocument()
  })

  it('filters topics by search query', async () => {
    const user = userEvent.setup()
    render(<TopicSearch topics={topics} selectedTopicId={null} onSelect={vi.fn()} />)
    await user.type(screen.getByLabelText('Search for a topic'), 'perce')
    expect(screen.getByText('Percentages')).toBeInTheDocument()
    expect(screen.queryByText('Ratio')).not.toBeInTheDocument()
  })

  it('calls onSelect when a topic is clicked', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    render(<TopicSearch topics={topics} selectedTopicId={null} onSelect={onSelect} />)
    await user.click(screen.getByText('Ratio'))
    expect(onSelect).toHaveBeenCalledWith('ratio')
  })

  it('shows an empty state when nothing matches', async () => {
    const user = userEvent.setup()
    render(<TopicSearch topics={topics} selectedTopicId={null} onSelect={vi.fn()} />)
    await user.type(screen.getByLabelText('Search for a topic'), 'zzz')
    expect(screen.getByText(/No topics match/)).toBeInTheDocument()
  })
})
