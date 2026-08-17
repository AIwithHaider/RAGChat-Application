// import { useState } from 'react'
// import './App.css'
// import Sidebar from './components/Sidebar'
// import Chat from './components/Chat'

// function App() {
//   const [documents, setDocuments] = useState([
//   {
//     id: 1,
//     name: 'report.pdf',
//   },
//   {
//     id: 2,
//     name: 'manual.pdf',
//   },
// ])

//   return (
//     <div className="app">
//       <header className="app-header">
//         <h1>RAGChat Application</h1>
//       </header>

//       <div className="app-body">
//         <Sidebar documents={documents} />
//         <Chat />
//       </div>
//     </div>
//   )
// }

// export default App



import { useEffect, useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import Chat from './components/Chat'
import { fetchDocuments } from './api/documents'

function App() {
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadDocuments() {
      try {
        setIsLoading(true)
        setError(null)

        const data = await fetchDocuments()
        setDocuments(data)
      } catch (err) {
        console.error('Failed to load documents:', err)
        setError('Failed to load documents')
      } finally {
        setIsLoading(false)
      }
    }

    loadDocuments()
  }, [])

  function handleFileSelect(file) {
    setDocuments((currentDocuments) => [
      ...currentDocuments,
      {
        id: Date.now(),
        filename: file.name,
      },
    ])
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>RAGChat Application</h1>
      </header>

      <div className="app-body">
        <Sidebar
          documents={documents}
          isLoading={isLoading}
          error={error}
          onFileSelect={handleFileSelect}
        />

        <Chat />
      </div>
    </div>
  )
}

export default App