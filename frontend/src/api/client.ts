import { ApiError, NetworkError, type Tier, type Topic } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

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

export async function fetchTopics(): Promise<Topic[]> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}/api/topics`)
  } catch (err) {
    console.error('Network error fetching topics:', err)
    throw new NetworkError()
  }

  if (!response.ok) {
    const detail = await parseErrorDetail(response)
    console.error('API error fetching topics:', detail)
    throw new ApiError(detail, response.status)
  }

  return response.json()
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
