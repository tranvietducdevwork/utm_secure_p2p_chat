/**
 * In-memory user registry.
 * Stores only: username, password hash, public key, online status.
 * NEVER stores message content.
 */

const users = new Map(); // username -> { id, username, passwordHash, publicKey, createdAt }
const socketToUser = new Map(); // socketId -> username

function createUser({ username, passwordHash, publicKey }) {
  if (users.has(username)) {
    throw new Error('USERNAME_EXISTS');
  }
  const user = {
    id: username,
    username,
    passwordHash,
    publicKey,
    online: false,
    socketId: null,
    createdAt: new Date().toISOString(),
  };
  users.set(username, user);
  return sanitizeUser(user);
}

function findByUsername(username) {
  return users.get(username) || null;
}

function setOnline(username, socketId) {
  const user = users.get(username);
  if (!user) return null;

  // User reconnects from a new socket — clear old socket mapping
  if (user.socketId && user.socketId !== socketId) {
    socketToUser.delete(user.socketId);
  }

  user.online = true;
  user.socketId = socketId;
  socketToUser.set(socketId, username);
  return sanitizeUser(user);
}

function setOffline(socketId) {
  const username = socketToUser.get(socketId);
  if (!username) return null;
  const user = users.get(username);
  if (user && user.socketId === socketId) {
    user.online = false;
    user.socketId = null;
  }
  socketToUser.delete(socketId);
  return username;
}

function getOnlineUsers(excludeUsername) {
  return [...users.values()]
    .filter((u) => u.online && u.username !== excludeUsername)
    .map(sanitizeUser);
}

function getSocketId(username) {
  const user = users.get(username);
  return user?.socketId || null;
}

function updatePublicKey(username, publicKey) {
  const user = users.get(username);
  if (!user) return null;
  user.publicKey = publicKey;
  return sanitizeUser(user);
}

function sanitizeUser(user) {
  return {
    id: user.id,
    username: user.username,
    publicKey: user.publicKey,
    online: user.online,
  };
}

function getStats() {
  const all = [...users.values()];
  return {
    totalUsers: all.length,
    onlineUsers: all.filter((u) => u.online).length,
    messagesStored: 0,
  };
}

module.exports = {
  createUser,
  findByUsername,
  setOnline,
  setOffline,
  getOnlineUsers,
  getSocketId,
  updatePublicKey,
  getStats,
};
