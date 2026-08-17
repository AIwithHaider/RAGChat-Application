function ChatInput() {
  return (
    <div className="chat-input-area">
      <input
        type="text"
        placeholder="Ask a question..."
        disabled
      />

      <button type="button" disabled>
        Send
      </button>
    </div>
  )
}

export default ChatInput