import { useEffect, useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import Chat from './components/Chat'
import {
  fetchDocuments,
  uploadDocument,
} from './api/documents'

function App() {
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)


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

  async function handleFileSelect(file) {
  try {
    setIsUploading(true)
    setUploadError(null)

    await uploadDocument(file, 1)

    const data = await fetchDocuments()
    setDocuments(data)
  } catch (err) {
    console.error('Failed to upload document:', err)
    setUploadError('Failed to upload document.')
  } finally {
    setIsUploading(false)
  }
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
          isUploading={isUploading}
          uploadError={uploadError}
        />

        <Chat />
      </div>
    </div>
  )
}

export default App