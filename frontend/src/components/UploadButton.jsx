import { useRef } from 'react'

function UploadButton({ onFileSelect, isUploading }) {  const fileInputRef = useRef(null)

  function handleButtonClick() {
    fileInputRef.current?.click()
  }

  function handleFileChange(event) {
  const file = event.target.files?.[0]

  if (!file) {
    return
  }

  if (file.type !== 'application/pdf') {
    event.target.value = ''
    return
  }

  onFileSelect(file)

  event.target.value = ''
}

  return (
    <>
      <button
        type="button"
        className="upload-button"
        onClick={handleButtonClick}
        disabled={isUploading}
      >
        {isUploading ? 'Uploading...' : '+ Add document'}
      </button>

      <input
      ref={fileInputRef}
      type="file"
      accept=".pdf,application/pdf"
      onChange={handleFileChange}
      hidden
      />
    </>
  )
}

export default UploadButton