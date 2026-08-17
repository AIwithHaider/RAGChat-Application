// import { render, screen } from '@testing-library/react'
// import DocumentList from './DocumentList'

// describe('DocumentList', () => {
//   test('shows empty state when there are no documents', () => {
//     render(<DocumentList documents={[]} />)

//     expect(screen.getByText('No documents yet.')).toBeInTheDocument()
//   })
// })

import { render, screen } from '@testing-library/react'
import DocumentList from './DocumentList'

describe('DocumentList', () => {
  test('shows empty state when there are no documents', () => {
    render(<DocumentList documents={[]} />)

    expect(screen.getByText('No documents yet.')).toBeInTheDocument()
  })

  test('displays document filenames', () => {
    const documents = [
      {
        id: 1,
        tenant_id: 1,
        filename: 'report.pdf',
        status: 'pending',
      },
      {
        id: 2,
        tenant_id: 1,
        filename: 'manual.pdf',
        status: 'pending',
      },
    ]

    render(<DocumentList documents={documents} />)

    expect(screen.getByText('report.pdf')).toBeInTheDocument()
    expect(screen.getByText('manual.pdf')).toBeInTheDocument()
  })
})


