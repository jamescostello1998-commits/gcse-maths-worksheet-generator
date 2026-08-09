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
        topics: [makeTopic('area_rectangle', 'Area of a Rectangle')],
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

async function selectTopicInBox(user: ReturnType<typeof userEvent.setup>, boxIndex: number, label: string) {
  const inputs = screen.getAllByRole('combobox')
  await user.click(inputs[boxIndex])
  await user.type(inputs[boxIndex], label)
  await user.click(await screen.findByText(label))
}

async function selectAllSixTopics(user: ReturnType<typeof userEvent.setup>) {
  for (let i = 0; i < LABELS.length; i++) {
    await selectTopicInBox(user, i, LABELS[i])
  }
}

describe('BellTasksView', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    URL.revokeObjectURL = vi.fn()
  })

  it('shows a KS3/KS4 picker first, with KS3 disabled', () => {
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    expect(screen.getByText('Bell Tasks')).toBeInTheDocument()
    const ks3Button = screen.getByText('KS3').closest('button')
    const ks4Button = screen.getByText('KS4').closest('button')
    expect(ks3Button).toBeDisabled()
    expect(ks4Button).not.toBeDisabled()
  })

  it('shows 6 searchable topic boxes after choosing KS4, with tier labels on options', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('KS4'))

    const inputs = screen.getAllByRole('combobox')
    expect(inputs).toHaveLength(6)

    await user.click(inputs[0])
    expect(screen.getByText('Angles in a Triangle (Higher)')).toBeInTheDocument()
    expect(screen.getByText('Area of a Rectangle (Foundation)')).toBeInTheDocument()
  })

  it('filters the option list as the user types', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('KS4'))

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
    await user.click(screen.getByText('KS4'))

    const inputs = screen.getAllByRole('combobox')
    await user.click(inputs[0])

    expect(screen.getAllByText('Dividing Fractions (Foundation)').length).toBeGreaterThan(0)
    expect(screen.queryByText('Dividing Fractions (Foundation) (Foundation)')).not.toBeInTheDocument()
  })

  it('disables Generate until all 6 boxes have a distinct topic chosen', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('KS4'))

    const generateButton = screen.getByText('Generate Bell Tasks')
    expect(generateButton).toBeDisabled()

    await selectAllSixTopics(user)
    expect(generateButton).not.toBeDisabled()
  })

  it('shows the chosen topic label in the box once selected', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('KS4'))

    await selectTopicInBox(user, 0, LABELS[0])
    const inputs = screen.getAllByRole('combobox')
    expect(inputs[0]).toHaveValue(LABELS[0])
  })

  it('prevents choosing the same topic twice by excluding already-picked topics from other boxes', async () => {
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={() => {}} />)
    await user.click(screen.getByText('KS4'))

    await selectTopicInBox(user, 0, LABELS[0])

    const inputs = screen.getAllByRole('combobox')
    await user.click(inputs[1])
    // The topic just chosen in box 1 must not be selectable in box 2's list.
    expect(screen.queryByText(LABELS[0])).not.toBeInTheDocument()
  })

  it('posts the 6 chosen topic ids and downloads a .pptx on Generate', async () => {
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
    await user.click(screen.getByText('KS4'))
    await selectAllSixTopics(user)
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
        }),
      }),
    )
  })

  it('calls onBack when the back button is clicked', async () => {
    const onBack = vi.fn()
    const user = userEvent.setup()
    render(<BellTasksView sections={sections} onBack={onBack} />)
    await user.click(screen.getByText('← Back'))
    expect(onBack).toHaveBeenCalled()
  })
})
