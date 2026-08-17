import { useRef } from 'react'

function UploadButton({ onFileSelect }) {
  const fileInputRef = useRef(null)

  function handleButtonClick() {
    fileInputRef.current?.click()
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0]

    if (!file) {
      return
    }

    onFileSelect(file)

    // Allow selecting the same file again later.
    event.target.value = ''
  }

  return (
    <>
      <button
        type="button"
        className="upload-button"
        onClick={handleButtonClick}
      >
        + Add document
      </button>

      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        hidden
      />
    </>
  )
}

export default UploadButton