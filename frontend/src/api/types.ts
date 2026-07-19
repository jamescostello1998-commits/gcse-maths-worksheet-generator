export type Tier = 'foundation' | 'higher'

export interface Topic {
  id: string
  name: string
  description: string
}

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export class NetworkError extends Error {
  constructor(message = 'Could not reach the server. Is the backend running?') {
    super(message)
    this.name = 'NetworkError'
  }
}
