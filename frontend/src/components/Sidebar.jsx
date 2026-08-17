// import DocumentList from './DocumentList'
// import UploadButton from './UploadButton'

// function Sidebar({ documents }) {
//   return (
//     <aside className="sidebar">
//       <div className="sidebar-header">
//         <h2>Documents</h2>
//       </div>

//       <DocumentList documents={documents} />

//       <div className="sidebar-footer">
//         <UploadButton />
//       </div>
//     </aside>
//   )
// }

// export default Sidebar


import DocumentList from './DocumentList'
import UploadButton from './UploadButton'

function Sidebar({
  documents,
  isLoading,
  error,
  onFileSelect,
}) {
    return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Documents</h2>
      </div>

      <DocumentList
        documents={documents}
        isLoading={isLoading}
        error={error}
        />

      <div className="sidebar-footer">
        <UploadButton onFileSelect={onFileSelect} />
      </div>
    </aside>
  )
}

export default Sidebar