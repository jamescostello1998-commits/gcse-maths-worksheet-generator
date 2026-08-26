import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { BellTasksView } from './BellTasksView'
import type { Section, Topic } from '../api/types'

function makeTopic(id: string, name: string, fixedTier: Topic['fixedTier'] = 'foundation'): Topic {
  return { id, name, description: '', fixedTier, hasModelledExample: true, defaultQuestionCount: 20 }
}

const sections: Section[] = [
  {
    id: 'number',
    name: 'Number',
    groups: [
      { name: 'Fractions', topics: [makeTopic('fractions_add_subtract', 'Add and Subtract Fractions')] },
      { name: 'Decimals', topics: [makeTopic('decimals_multiply', 'Multiply Decimals')] },
    ],
  },
  {
    id: 'algebra',
    name: 'Algebra',
    groups: [
      {
        name: 'Solving Linear Equations',
        topics: [makeTopic('linear_two_step', 'Two-Step Equations'), makeTopic('linear_one_step', 'One-Step Equations')],
      },
    ],
  },
  {
    id: 'geometry',
    name: 'Geometry',
    groups: [
      {
        name: 'Angles',
        topics: [makeTopic('angles_triangle', 'Angles in a Triangle', 'higher')],
      },
      {
        name: 'Area & Perimeter',
        topics: [
          makeTopic('area_rectangle', 'Area of a Rectangle'),
          makeTopic('circle_parts', 'Parts of a Circle'),
          makeTopic('area_triangle', 'Area of a Triangle'),
        ],
      },
    ],
  },
]

const LABELS = [
  'Add and Subtract Fractions (Foundation)',
  'Multiply Decimals (Foundation)',
  'Two-Step Equations (Foundation)',
  'One-Step Equations (Foundation)',
  'Angles in a Triangle (Higher)',
  'Area of a Rectangle (Foundation)',
]

const EIGHT_LABELS = [...LABELS, 'Parts of a Circle (Foundation)', 'Area of a Triangle (Foundation)']

async function selectTopicInBox(user: ReturnType<typeof userEvent.setup>, boxIndex: number, label: string) {
  const inputs = screen.getAllByRole('combobox')
  await user.click(inputs[boxIndex])
  await user.type(inputs[boxIndex], label)
  await user.click(await screen.findByText(label))
}

async function selectTopics(user: ReturnType<typeof userEvent.setup>, labels: string[]) {
  for (let i = 0; i < labels.length; i++) {
    await selectTopicInBox(user, i, labels[i])
  }
}

describe('BellTasksView', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    URL.revokeObjectURL = vi.fn()
  })

  it('shows a Year 11 / Year 10 / Years 7-9 picker first, with Years 7-9 disabled', () => {
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    expect(screen.getByText('Bell Tasks')).toBeInTheDocument()
    const year11Button = screen.getByText('Year 11').closest('button')
    const year10Button = screen.getByText('Year 10').closest('button')
    const years79Button = screen.getByText('Years 7-9').closest('button')
    expect(year11Button).not.toBeDisabled()
    expect(year10Button).not.toBeDisabled()
    expect(years79Button).toBeDisabled()
  })

  it('shows 6 searchable topic boxes after choosing Year 10, with tier labels on options', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('Year 10'))

    const inputs = screen.getAllByRole('combobox')
    expect(inputs).toHaveLength(6)

    await user.click(inputs[0])
    expect(screen.getByText('Angles in a Triangle (Higher)')).toBeInTheDocument()
    expect(screen.getByText('Area of a Rectangle (Foundation)')).toBeInTheDocument()
  })

  it('shows 8 searchable topic boxes after choosing Year 11', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('Year 11'))

    const inputs = screen.getAllByRole('combobox')
    expect(inputs).toHaveLength(8)
  })

  it('filters the option list as the user types', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('Year 10'))

    const inputs = screen.getAllByRole('combobox')
    await user.click(inputs[0])
    await user.type(inputs[0], 'triangle')

    expect(screen.getByText('Angles in a Triangle (Higher)')).toBeInTheDocument()
    expect(screen.queryByText('Area of a Rectangle (Foundation)')).not.toBeInTheDocument()
  })

  it('does not double up a tier suffix already baked into the topic name', async () => {
    const sectionsWithSelfSuffixedName: Section[] = [
      {
        id: 'number',
        name: 'Number',
        groups: [
          { name: 'Fractions', topics: [makeTopic('fractions_divide_foundation', 'Dividing Fractions (Foundation)')] },
        ],
      },
    ]
    const user = userEvent.setup()
    render(<BellTasksView sections={sectionsWithSelfSuffixedName} onBack={() => {}} />)
    await user.click(screen.getByText('Year 10'))

    const inputs = screen.getAllByRole('combobox')
    await user.click(inputs[0])

    expect(screen.getAllByText('Dividing Fractions (Foundation)').length).toBeGreaterThan(0)
    expect(screen.queryByText('Dividing Fractions (Foundation) (Foundation)')).not.toBeInTheDocument()
  })

  it('disables Generate until all 6 boxes have a distinct topic chosen (Year 10)', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('Year 10'))

    const generateButton = screen.getByText('Generate Bell Tasks')
    expect(generateButton).toBeDisabled()

    await selectTopics(user, LABELS)
    expect(generateButton).not.toBeDisabled()
  })

  it('disables Generate until all 8 boxes have a distinct topic chosen (Year 11)', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('Year 11'))

    const generateButton = screen.getByText('Generate Bell Tasks')
    expect(generateButton).toBeDisabled()

    await selectTopics(user, EIGHT_LABELS)
    expect(generateButton).not.toBeDisabled()
  }, 15000)

  it('shows the chosen topic label in the box once selected', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('Year 10'))

    await selectTopicInBox(user, 0, LABELS[0])
    const inputs = screen.getAllByRole('combobox')
    expect(inputs[0]).toHaveValue(LABELS[0])
  })

  it('prevents choosing the same topic twice by excluding already-picked topics from other boxes', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('Year 10'))

    await selectTopicInBox(user, 0, LABELS[0])

    const inputs = screen.getAllByRole('combobox')
    await user.click(inputs[1])
    // The topic just chosen in box 1 must not be selectable in box 2's list.
    expect(screen.queryByText(LABELS[0])).not.toBeInTheDocument()
  })

  it('posts the 6 chosen topic ids and year_10 and downloads a .pptx on Generate', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () =>
        new Blob(['PK'], {
          type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('Year 10'))
    await selectTopics(user, LABELS)
    await user.click(screen.getByText('Generate Bell Tasks'))

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/bell-tasks'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          topic_ids: [
            'fractions_add_subtract',
            'decimals_multiply',
            'linear_two_step',
            'linear_one_step',
            'angles_triangle',
            'area_rectangle',
          ],
          year: 'year_10',
        }),
      }),
    )
  })

  it('posts the 8 chosen topic ids and year_11 and downloads a .pptx on Generate', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () =>
        new Blob(['PK'], {
          type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('Year 11'))
    await selectTopics(user, EIGHT_LABELS)
    await user.click(screen.getByText('Generate Bell Tasks'))

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/bell-tasks'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          topic_ids: [
            'fractions_add_subtract',
            'decimals_multiply',
            'linear_two_step',
            'linear_one_step',
            'angles_triangle',
            'area_rectangle',
            'circle_parts',
            'area_triangle',
          ],
          year: 'year_11',
        }),
      }),
    )
  }, 15000)

  it('calls onBack when the back button is clicked', async () => {
    const onBack = vi.fn()
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={onBack} />)
    await user.click(screen.getByText('← Back'))
    expect(onBack).toHaveBeenCalled()
  })
})
