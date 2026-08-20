const API_BASE_URL = 'http://localhost:8000'

export async function fetchDocuments() {
  const response = await fetch(`${API_BASE_URL}/documents`)

  if (!response.ok) {
    throw new Error('Failed to fetch documents')
  }

  return response.json()
}

export async function uploadDocument(file, tenantId) {
  const formData = new FormData()

  formData.append('tenant_id', tenantId)
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error('Failed to upload document')
  }

  return response.json()
}