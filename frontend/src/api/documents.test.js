import { describe, expect, test, vi } from 'vitest'
import { uploadDocument } from './documents'

describe('uploadDocument', () => {
  test('uploads a document using multipart form data', async () => {
    const file = new File(
      ['%PDF-1.4 test content'],
      'report.pdf',
      {
        type: 'application/pdf',
      },
    )

    const mockResponse = {
      id: 1,
      tenant_id: 1,
      filename: 'report.pdf',
      status: 'pending',
    }

    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      })

    const result = await uploadDocument(file, 1)

    expect(fetchMock).toHaveBeenCalledTimes(1)

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/documents',
      expect.objectContaining({
        method: 'POST',
        body: expect.any(FormData),
      }),
    )

    const request = fetchMock.mock.calls[0][1]
    const formData = request.body

    expect(formData.get('tenant_id')).toBe('1')
    expect(formData.get('file')).toBe(file)

    expect(result).toEqual(mockResponse)
  })

  test('throws when the upload request fails', async () => {
    const file = new File(
      ['%PDF-1.4 test content'],
      'report.pdf',
      {
        type: 'application/pdf',
      },
    )

    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
    })

    await expect(
      uploadDocument(file, 1),
    ).rejects.toThrow('Failed to upload document')
  })
})