interface GenerateButtonProps {
  disabled: boolean
  loading: boolean
  onClick: () => void
}

export function GenerateButton({ disabled, loading, onClick }: GenerateButtonProps) {
  return (
    <button
      type="button"
      className="generate-button"
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading ? 'Generating…' : 'Generate Worksheet'}
    </button>
  )
}
