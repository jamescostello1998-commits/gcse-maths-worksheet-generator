import { ApiError, NetworkError, type Section, type Tier, type Topic } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

interface RawTopic {
  id: string
  name: string
  description: string
  fixed_tier: Tier | null
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

export async function generateWorksheet(topicId: string, tier: Tier): Promise<Blob> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}/api/worksheets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic_id: topicId, tier }),
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
