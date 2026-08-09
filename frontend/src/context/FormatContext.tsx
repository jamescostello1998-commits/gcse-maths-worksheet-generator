import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import type { DownloadFormat } from '../api/types'

const STORAGE_KEY = 'worksheet-download-format'

interface FormatContextValue {
  format: DownloadFormat
  setFormat: (format: DownloadFormat) => void
}

const FormatContext = createContext<FormatContextValue | undefined>(undefined)

function readStoredFormat(): DownloadFormat {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'docx' ? 'docx' : 'pdf'
  } catch {
    // localStorage can throw (private mode / disabled) - fall back to PDF.
    return 'pdf'
  }
}

export function FormatProvider({ children }: { children: ReactNode }) {
  const [format, setFormatState] = useState<DownloadFormat>(readStoredFormat)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, format)
    } catch {
      // Persisting is best-effort; ignore storage failures.
    }
  }, [format])

  const setFormat = useCallback((next: DownloadFormat) => setFormatState(next), [])
  const value = useMemo(() => ({ format, setFormat }), [format, setFormat])

  return <FormatContext.Provider value={value}>{children}</FormatContext.Provider>
}

export function useFormat(): FormatContextValue {
  const ctx = useContext(FormatContext)
  if (ctx === undefined) {
    throw new Error('useFormat must be used within a FormatProvider')
  }
  return ctx
}
