import type { DownloadFormat } from '../api/types'
import { useFormat } from '../context/FormatContext'

const OPTIONS: { value: DownloadFormat; label: string }[] = [
  { value: 'pdf', label: 'PDF' },
  { value: 'docx', label: 'Word' },
]

export function DownloadFormatToggle() {
  const { format, setFormat } = useFormat()

  return (
    <div className="format-toggle">
      <span className="format-toggle__label">Download as</span>
      <div className="format-toggle__switch" role="radiogroup" aria-label="Download format">
        {OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            role="radio"
            aria-checked={format === option.value}
            className={
              format === option.value
                ? 'format-toggle__option format-toggle__option--active'
                : 'format-toggle__option'
            }
            onClick={() => setFormat(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  )
}
