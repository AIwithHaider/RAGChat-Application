const API_BASE_URL = 'http://localhost:8000'

export async function fetchDocuments() {
  const response = await fetch(`${API_BASE_URL}/documents`)

  if (!response.ok) {
    throw new Error('Failed to fetch documents')
  }

  return response.json()
}