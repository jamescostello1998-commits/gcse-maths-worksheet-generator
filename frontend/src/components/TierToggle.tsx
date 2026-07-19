import type { Tier } from '../api/types'

interface TierToggleProps {
  tier: Tier
  onChange: (tier: Tier) => void
}

export function TierToggle({ tier, onChange }: TierToggleProps) {
  return (
    <div className="tier-toggle" role="radiogroup" aria-label="Tier">
      {(['foundation', 'higher'] as const).map((option) => (
        <button
          key={option}
          type="button"
          role="radio"
          aria-checked={tier === option}
          className={
            tier === option ? 'tier-toggle__option tier-toggle__option--active' : 'tier-toggle__option'
          }
          onClick={() => onChange(option)}
        >
          {option === 'foundation' ? 'Foundation' : 'Higher'}
        </button>
      ))}
    </div>
  )
}
