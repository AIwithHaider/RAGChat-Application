function Message({ role, content }) {
  return (
    <article className={`message message-${role}`}>
      <div className="message-role">
        {role === 'user' ? 'You' : 'AI'}
      </div>

      <div className="message-content">
        {content}
      </div>
    </article>
  )
}

export default Message