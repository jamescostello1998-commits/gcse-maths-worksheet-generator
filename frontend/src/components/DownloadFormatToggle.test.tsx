import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { DownloadFormatToggle } from './DownloadFormatToggle'
import { TopicCard } from './TopicCard'
import { FormatProvider } from '../context/FormatContext'
import type { Topic } from '../api/types'

const topic: Topic = {
  id: 'linear_one_step',
  name: 'One-Step Equations',
  description: 'Solve simple equations.',
  fixedTier: 'foundation',
  hasModelledExample: false,
  defaultQuestionCount: 20,
}

describe('DownloadFormatToggle', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
    URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    URL.revokeObjectURL = vi.fn()
  })

  it('defaults to PDF', () => {
    render(
      <FormatProvider>
        <DownloadFormatToggle />
      </FormatProvider>,
    )
    expect(screen.getByRole('radio', { name: 'PDF' })).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('radio', { name: 'Word' })).toHaveAttribute('aria-checked', 'false')
  })

  it('persists the chosen format to localStorage', async () => {
    const user = userEvent.setup()
    render(
      <FormatProvider>
        <DownloadFormatToggle />
      </FormatProvider>,
    )
    await user.click(screen.getByRole('radio', { name: 'Word' }))
    expect(screen.getByRole('radio', { name: 'Word' })).toHaveAttribute('aria-checked', 'true')
    expect(localStorage.getItem('worksheet-download-format')).toBe('docx')
  })

  it('restores the stored format on mount', () => {
    localStorage.setItem('worksheet-download-format', 'docx')
    render(
      <FormatProvider>
        <DownloadFormatToggle />
      </FormatProvider>,
    )
    expect(screen.getByRole('radio', { name: 'Word' })).toHaveAttribute('aria-checked', 'true')
  })

  it('makes a topic download request the docx format when Word is selected', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['x'], { type: 'application/octet-stream' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(
      <FormatProvider>
        <DownloadFormatToggle />
        <TopicCard topic={topic} />
      </FormatProvider>,
    )
    await user.click(screen.getByRole('radio', { name: 'Word' }))
    await user.click(screen.getByText('Worksheet'))

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/worksheets'),
      expect.objectContaining({
        body: JSON.stringify({ topic_id: 'linear_one_step', tier: 'foundation', format: 'docx' }),
      }),
    )
  })
})
