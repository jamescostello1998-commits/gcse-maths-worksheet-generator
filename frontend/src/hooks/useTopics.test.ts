import { renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useTopics } from './useTopics'

describe('useTopics', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('loads topics successfully', async () => {
    const mockTopics = [{ id: 'a', name: 'A', description: 'desc' }]
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockTopics,
      }),
    )

    const { result } = renderHook(() => useTopics())
    expect(result.current.loading).toBe(true)

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.topics).toEqual(mockTopics)
    expect(result.current.error).toBeNull()
  })

  it('surfaces an API error', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'server exploded' }),
      }),
    )

    const { result } = renderHook(() => useTopics())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBe('server exploded')
  })

  it('surfaces a network error', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new Error('network down')),
    )

    const { result } = renderHook(() => useTopics())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toMatch(/reach the server/i)
  })
})
