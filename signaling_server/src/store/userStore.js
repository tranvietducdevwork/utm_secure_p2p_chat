/**
 * User registry with file persistence (survives server restart on same disk).
 * Stores: username, password hash, public key — NEVER message content.
 */

const fs = require('fs');
const path = require('path');

const users = new Map();
const socketToUser = new Map();

const DATA_FILE =
  process.env.USER_DATA_FILE || path.join(__dirname, '../../data/users.json');

function persistUsers() {
  try {
    const dir = path.dirname(DATA_FILE);
    fs.mkdirSync(dir, { recursive: true });
    const payload = [...users.values()].map((u) => ({
      id: u.id,
      username: u.username,
      passwordHash: u.passwordHash,
      publicKey: u.publicKey,
      createdAt: u.createdAt,
    }));
    fs.writeFileSync(DATA_FILE, JSON.stringify(payload, null, 2), 'utf8');
    console.log(`[userStore] saved ${payload.length} user(s)`);
  } catch (err) {
    console.error('[userStore] persist failed:', err.message);
  }
}

function loadUsers() {
  try {
    if (!fs.existsSync(DATA_FILE)) return;
    const payload = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    for (const u of payload) {
      users.set(u.username, {
        ...u,
        online: false,
        socketId: null,
      });
    }
    console.log(`[userStore] loaded ${payload.length} user(s) from disk`);
  } catch (err) {
    console.error('[userStore] load failed:', err.message);
  }
}

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
  persistUsers();
  return sanitizeUser(user);
}

function findByUsername(username) {
  return users.get(username) || null;
}

function setOnline(username, socketId) {
  const user = users.get(username);
  if (!user) return null;

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
  persistUsers();
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

loadUsers();

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
