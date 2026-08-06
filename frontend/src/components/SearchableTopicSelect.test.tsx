import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { SearchableTopicSelect, type SearchableTopicOption } from './SearchableTopicSelect'

const options: SearchableTopicOption[] = [
  { id: 'fractions_simplify', label: 'Simplifying Fractions (Foundation)', breadcrumb: 'Number › Fractions' },
  { id: 'linear_two_step', label: 'Two-Step Equations (Foundation)', breadcrumb: 'Algebra › Solving Linear Equations' },
  { id: 'angles_triangle', label: 'Angles in a Triangle (Higher)', breadcrumb: 'Geometry › Angles' },
]

describe('SearchableTopicSelect', () => {
  it('shows the full option list when focused with no value chosen', async () => {
    const user = userEvent.setup()
    render(<SearchableTopicSelect ariaLabel="Box 1 topic" options={options} value="" onChange={() => {}} />)

    await user.click(screen.getByRole('combobox'))
    expect(screen.getByText('Simplifying Fractions (Foundation)')).toBeInTheDocument()
    expect(screen.getByText('Two-Step Equations (Foundation)')).toBeInTheDocument()
    expect(screen.getByText('Angles in a Triangle (Higher)')).toBeInTheDocument()
  })

  it('filters options as the user types', async () => {
    const user = userEvent.setup()
    render(<SearchableTopicSelect ariaLabel="Box 1 topic" options={options} value="" onChange={() => {}} />)

    const input = screen.getByRole('combobox')
    await user.click(input)
    await user.type(input, 'angle')

    expect(screen.getByText('Angles in a Triangle (Higher)')).toBeInTheDocument()
    expect(screen.queryByText('Simplifying Fractions (Foundation)')).not.toBeInTheDocument()
    expect(screen.queryByText('Two-Step Equations (Foundation)')).not.toBeInTheDocument()
  })

  it('shows a no-match message when nothing filters in', async () => {
    const user = userEvent.setup()
    render(<SearchableTopicSelect ariaLabel="Box 1 topic" options={options} value="" onChange={() => {}} />)

    const input = screen.getByRole('combobox')
    await user.click(input)
    await user.type(input, 'zzzzz')

    expect(screen.getByText('No topics match')).toBeInTheDocument()
  })

  it('calls onChange with the topic id when an option is clicked', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<SearchableTopicSelect ariaLabel="Box 1 topic" options={options} value="" onChange={onChange} />)

    await user.click(screen.getByRole('combobox'))
    await user.click(screen.getByText('Angles in a Triangle (Higher)'))

    expect(onChange).toHaveBeenCalledWith('angles_triangle')
  })

  it('closes the list and shows the selected label after choosing an option', async () => {
    const user = userEvent.setup()
    function Wrapper() {
      const [value, setValue] = useState('')
      return <SearchableTopicSelect ariaLabel="Box 1 topic" options={options} value={value} onChange={setValue} />
    }
    render(<Wrapper />)

    const input = screen.getByRole('combobox')
    await user.click(input)
    await user.click(screen.getByText('Angles in a Triangle (Higher)'))

    expect(screen.queryByText('Simplifying Fractions (Foundation)')).not.toBeInTheDocument()
    expect(input).toHaveValue('Angles in a Triangle (Higher)')
  })

  it('closes the list on Escape', async () => {
    const user = userEvent.setup()
    render(<SearchableTopicSelect ariaLabel="Box 1 topic" options={options} value="" onChange={() => {}} />)

    const input = screen.getByRole('combobox')
    await user.click(input)
    expect(screen.getByText('Simplifying Fractions (Foundation)')).toBeInTheDocument()

    await user.keyboard('{Escape}')
    expect(screen.queryByText('Simplifying Fractions (Foundation)')).not.toBeInTheDocument()
  })
})
