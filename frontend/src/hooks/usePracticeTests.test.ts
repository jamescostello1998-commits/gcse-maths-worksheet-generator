import { renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { usePracticeTests } from './usePracticeTests'

describe('usePracticeTests', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('loads and maps practice tests successfully', async () => {
    const raw = [
      { id: 'foundation-01', name: 'Foundation Practice Test 1', tier: 'foundation', total_marks: 100, question_count: 27 },
      { id: 'higher-01', name: 'Higher Practice Test 1', tier: 'higher', total_marks: 100, question_count: 23 },
    ]
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => raw,
      }),
    )

    const { result } = renderHook(() => usePracticeTests())
    expect(result.current.loading).toBe(true)

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.practiceTests).toHaveLength(2)
    expect(result.current.practiceTests[0]).toEqual({
      id: 'foundation-01',
      name: 'Foundation Practice Test 1',
      tier: 'foundation',
      totalMarks: 100,
      questionCount: 27,
    })
    expect(result.current.error).toBeNull()
  })

  it('surfaces a network error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network down')))

    const { result } = renderHook(() => usePracticeTests())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toMatch(/reach the server/i)
  })
})
