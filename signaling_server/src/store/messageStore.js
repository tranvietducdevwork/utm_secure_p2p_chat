/**
 * Demo-only message storage for thesis showcase.
 * Disabled by default — no message content stored in production mode.
 */

const messages = [];

function addMessage({ from, to, content, encrypted }) {
  messages.push({
    id: messages.length + 1,
    from,
    to,
    content,
    encrypted: Boolean(encrypted),
    timestamp: new Date().toISOString(),
  });
  if (messages.length > 500) {
    messages.shift();
  }
}

function getMessages() {
  return [...messages];
}

function clearMessages() {
  messages.length = 0;
}

function getStats() {
  return {
    messagesStored: messages.length,
    messages: getMessages(),
  };
}

module.exports = {
  addMessage,
  getMessages,
  clearMessages,
  getStats,
};
