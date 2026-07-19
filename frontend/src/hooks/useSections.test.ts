import { renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useSections } from './useSections'

describe('useSections', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('loads and maps sections successfully', async () => {
    const rawSections = [
      { id: 'number', name: 'Number', groups: [] },
      {
        id: 'algebra',
        name: 'Algebra',
        groups: [
          {
            name: 'Solving Linear Equations',
            topics: [
              { id: 'linear_one_step', name: 'One-Step Equations', description: 'desc', fixed_tier: 'foundation' },
            ],
          },
        ],
      },
    ]
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => rawSections,
      }),
    )

    const { result } = renderHook(() => useSections())
    expect(result.current.loading).toBe(true)

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.sections).toHaveLength(2)
    expect(result.current.sections[0]).toEqual({ id: 'number', name: 'Number', groups: [] })
    expect(result.current.sections[1].groups[0].topics[0]).toEqual({
      id: 'linear_one_step',
      name: 'One-Step Equations',
      description: 'desc',
      fixedTier: 'foundation',
    })
    expect(result.current.error).toBeNull()
  })

  it('surfaces a network error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network down')))

    const { result } = renderHook(() => useSections())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toMatch(/reach the server/i)
  })
})
