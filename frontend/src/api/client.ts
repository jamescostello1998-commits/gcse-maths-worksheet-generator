import {
  ApiError,
  NetworkError,
  type PracticeTestSummary,
  type Section,
  type Tier,
  type Topic,
  type WorksheetOptions,
} from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

interface RawTopic {
  id: string
  name: string
  description: string
  fixed_tier: Tier | null
  has_modelled_example: boolean
  default_question_count: number
}

interface RawGroup {
  name: string
  topics: RawTopic[]
}

interface RawSection {
  id: string
  name: string
  groups: RawGroup[]
}

function toTopic(raw: RawTopic): Topic {
  return {
    id: raw.id,
    name: raw.name,
    description: raw.description,
    fixedTier: raw.fixed_tier,
    hasModelledExample: raw.has_modelled_example,
    defaultQuestionCount: raw.default_question_count,
  }
}

async function parseErrorDetail(response: Response): Promise<string> {
  try {
    const body = await response.json()
    if (typeof body?.detail === 'string') {
      return body.detail
    }
  } catch {
    // response body wasn't JSON; fall through to a generic message
  }
  return `Request failed with status ${response.status}`
}

async function getJson<T>(path: string, errorContext: string): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`)
  } catch (err) {
    console.error(`Network error ${errorContext}:`, err)
    throw new NetworkError()
  }

  if (!response.ok) {
    const detail = await parseErrorDetail(response)
    console.error(`API error ${errorContext}:`, detail)
    throw new ApiError(detail, response.status)
  }

  return response.json()
}

async function getBlob(path: string, errorContext: string): Promise<Blob> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`)
  } catch (err) {
    console.error(`Network error ${errorContext}:`, err)
    throw new NetworkError()
  }

  if (!response.ok) {
    const detail = await parseErrorDetail(response)
    console.error(`API error ${errorContext}:`, detail)
    throw new ApiError(detail, response.status)
  }

  return response.blob()
}

export async function fetchSections(): Promise<Section[]> {
  const raw = await getJson<RawSection[]>('/api/sections', 'fetching sections')
  return raw.map((section) => ({
    id: section.id,
    name: section.name,
    groups: section.groups.map((group) => ({
      name: group.name,
      topics: group.topics.map(toTopic),
    })),
  }))
}

export async function generateWorksheet(topicId: string, tier: Tier, options: WorksheetOptions = {}): Promise<Blob> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}/api/worksheets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic_id: topicId,
        tier,
        ...(options.count !== undefined ? { count: options.count } : {}),
        ...(options.answersOnly ? { answers_only: true } : {}),
      }),
    })
  } catch (err) {
    console.error('Network error generating worksheet:', err)
    throw new NetworkError()
  }

  if (!response.ok) {
    const detail = await parseErrorDetail(response)
    console.error('API error generating worksheet:', detail)
    throw new ApiError(detail, response.status)
  }

  return response.blob()
}

export async function generateModelledExample(topicId: string, tier: Tier): Promise<Blob> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}/api/modelled-examples`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic_id: topicId, tier }),
    })
  } catch (err) {
    console.error('Network error generating modelled example:', err)
    throw new NetworkError()
  }

  if (!response.ok) {
    const detail = await parseErrorDetail(response)
    console.error('API error generating modelled example:', detail)
    throw new ApiError(detail, response.status)
  }

  return response.blob()
}

interface RawPracticeTestSummary {
  id: string
  name: string
  tier: Tier
  sitting_id: string
  paper_number: number
  calculator_allowed: boolean
  total_marks: number
  question_count: number
}

function toPracticeTestSummary(raw: RawPracticeTestSummary): PracticeTestSummary {
  return {
    id: raw.id,
    name: raw.name,
    tier: raw.tier,
    sittingId: raw.sitting_id,
    paperNumber: raw.paper_number,
    calculatorAllowed: raw.calculator_allowed,
    totalMarks: raw.total_marks,
    questionCount: raw.question_count,
  }
}

export async function fetchPracticeTests(): Promise<PracticeTestSummary[]> {
  const raw = await getJson<RawPracticeTestSummary[]>('/api/practice-tests', 'fetching practice tests')
  return raw.map(toPracticeTestSummary)
}

export async function downloadPracticeTestPaper(paperId: string): Promise<Blob> {
  return getBlob(`/api/practice-tests/${paperId}/paper`, 'downloading practice test paper')
}

export async function downloadPracticeTestMarkScheme(paperId: string): Promise<Blob> {
  return getBlob(`/api/practice-tests/${paperId}/mark-scheme`, 'downloading practice test mark scheme')
}

export async function generateBellTasks(topicIds: string[]): Promise<Blob> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}/api/bell-tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic_ids: topicIds }),
    })
  } catch (err) {
    console.error('Network error generating bell tasks:', err)
    throw new NetworkError()
  }

  if (!response.ok) {
    const detail = await parseErrorDetail(response)
    console.error('API error generating bell tasks:', detail)
    throw new ApiError(detail, response.status)
  }

  return response.blob()
}
