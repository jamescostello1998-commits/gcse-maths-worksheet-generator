import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useGenerateWorksheet } from './useGenerateWorksheet'

describe('useGenerateWorksheet', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    URL.revokeObjectURL = vi.fn()
  })

  it('downloads the worksheet on success', async () => {
    const blob = new Blob(['%PDF-fake'], { type: 'application/pdf' })
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        blob: async () => blob,
      }),
    )

    const { result } = renderHook(() => useGenerateWorksheet())
    await act(async () => {
      await result.current.generate('percentages', 'higher')
    })

    expect(result.current.status).toBe('success')
    expect(URL.createObjectURL).toHaveBeenCalledWith(blob)
  })

  it('surfaces an API error status', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Unknown topic' }),
      }),
    )

    const { result } = renderHook(() => useGenerateWorksheet())
    await act(async () => {
      await result.current.generate('bad_topic', 'foundation')
    })
    expect(result.current.status).toBe('error')
    expect(result.current.error).toBe('Unknown topic')
  })

  it('surfaces a network error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('down')))

    const { result } = renderHook(() => useGenerateWorksheet())
    await act(async () => {
      await result.current.generate('percentages', 'higher')
    })
    expect(result.current.status).toBe('error')
    expect(result.current.error).toMatch(/reach the server/i)
  })
})
