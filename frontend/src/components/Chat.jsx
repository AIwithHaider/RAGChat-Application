import { useState } from 'react'
import ChatInput from './ChatInput'
import Message from './Message'

function Chat() {
  const [messages] = useState([
    {
      id: 1,
      role: 'user',
      content: 'What is this application?',
    },
    {
      id: 2,
      role: 'assistant',
      content: 'This is the RAGChat application.',
    },
  ])

  const [isLoading] = useState(false)
  const [error] = useState(null)
  // const [error, setError] = useState(null)  



  return (
    <main className="chat-area">
      <header className="chat-header">
        <h1>Chat</h1>
      </header>

      <section className="chat-content">
        {messages.map((message) => (
          <Message
            key={message.id}
            role={message.role}
            content={message.content}
          />
        ))}

        {isLoading && (
          <div className="loading-message">
            Thinking...
          </div>
        )}

        {error && (
        <div className="error-message">
        {error}
        </div>
        )}

      </section>

      <ChatInput />
    </main>
  )
}

export default Chat