import { useMemo, useRef, useState } from 'react'
import type { FocusEvent } from 'react'

export interface SearchableTopicOption {
  id: string
  label: string
  breadcrumb: string
}

interface SearchableTopicSelectProps {
  ariaLabel: string
  options: SearchableTopicOption[]
  value: string
  onChange: (topicId: string) => void
}

export function SearchableTopicSelect({ ariaLabel, options, value, onChange }: SearchableTopicSelectProps) {
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const selected = options.find((o) => o.id === value) ?? null

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return options
    return options.filter((o) => o.label.toLowerCase().includes(q))
  }, [options, query])

  function openForSearch() {
    setQuery('')
    setIsOpen(true)
  }

  function handleSelect(topicId: string) {
    onChange(topicId)
    setQuery('')
    setIsOpen(false)
  }

  function handleBlur(e: FocusEvent<HTMLDivElement>) {
    if (!containerRef.current?.contains(e.relatedTarget as Node | null)) {
      setIsOpen(false)
      setQuery('')
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Escape') {
      setIsOpen(false)
      setQuery('')
    }
  }

  return (
    <div className="searchable-select" ref={containerRef} onBlur={handleBlur} onKeyDown={handleKeyDown}>
      <input
        type="text"
        className="searchable-select__input"
        placeholder="Search for a topic..."
        value={isOpen ? query : (selected?.label ?? '')}
        onChange={(e) => {
          setQuery(e.target.value)
          setIsOpen(true)
        }}
        onFocus={openForSearch}
        aria-label={ariaLabel}
        role="combobox"
        aria-expanded={isOpen}
      />
      {isOpen && (
        <ul className="searchable-select__list" role="listbox">
          {filtered.length === 0 ? (
            <li className="searchable-select__empty">No topics match</li>
          ) : (
            filtered.map((option) => (
              <li key={option.id} role="option" aria-selected={option.id === value}>
                <button
                  type="button"
                  className="searchable-select__option"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => handleSelect(option.id)}
                >
                  <span className="searchable-select__option-name">{option.label}</span>
                  <span className="searchable-select__option-breadcrumb">{option.breadcrumb}</span>
                </button>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  )
}
