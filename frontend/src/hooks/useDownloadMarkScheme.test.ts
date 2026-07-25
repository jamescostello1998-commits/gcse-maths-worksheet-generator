import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useDownloadMarkScheme } from './useDownloadMarkScheme'

describe('useDownloadMarkScheme', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    URL.revokeObjectURL = vi.fn()
  })

  it('downloads the mark scheme on success', async () => {
    const blob = new Blob(['%PDF-fake'], { type: 'application/pdf' })
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => blob,
    })
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => useDownloadMarkScheme())
    await act(async () => {
      await result.current.download('foundation-01')
    })

    expect(result.current.status).toBe('success')
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/practice-tests/foundation-01/mark-scheme'),
    )
    expect(URL.createObjectURL).toHaveBeenCalledWith(blob)
  })

  it('surfaces an API error status', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Unknown practice test' }),
      }),
    )

    const { result } = renderHook(() => useDownloadMarkScheme())
    await act(async () => {
      await result.current.download('bad-id')
    })
    expect(result.current.status).toBe('error')
    expect(result.current.error).toBe('Unknown practice test')
  })

  it('surfaces a network error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('down')))

    const { result } = renderHook(() => useDownloadMarkScheme())
    await act(async () => {
      await result.current.download('foundation-01')
    })
    expect(result.current.status).toBe('error')
    expect(result.current.error).toMatch(/reach the server/i)
  })
})
