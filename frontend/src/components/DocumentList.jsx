// function DocumentList({ documents }) {
//   if (documents.length === 0) {
//     return (
//       <div className="document-list">
//         <p className="empty-state">No documents yet.</p>
//       </div>
//     )
//   }

//   return (
//     <div className="document-list">
//       {documents.map((document) => (
//         <div key={document.id} className="document-item">
//           {document.filename}
//         </div>
//       ))}
//     </div>
//   )
// }

// export default DocumentList




function DocumentList({ documents, isLoading, error }) {
  if (isLoading) {
    return (
      <div className="document-list">
        <p className="loading-state">Loading documents...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="document-list">
        <p className="error-state">Failed to load documents.</p>
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="document-list">
        <p className="empty-state">No documents yet.</p>
      </div>
    )
  }

  return (
    <div className="document-list">
      {documents.map((document) => (
        <div key={document.id} className="document-item">
          {document.filename}
        </div>
      ))}
    </div>
  )
}

export default DocumentList