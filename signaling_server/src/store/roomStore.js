/**
 * Room registry — users join by room code (works over 4G/WiFi via public server).
 */

const userRoom = new Map(); // username -> roomCode
const rooms = new Map(); // roomCode -> Set<username>

function normalizeCode(code) {
  return String(code || '').trim().toUpperCase();
}

function joinRoom(username, roomCode) {
  const code = normalizeCode(roomCode);
  if (!code || code.length < 4) {
    throw new Error('INVALID_ROOM');
  }
  leaveRoom(username);
  if (!rooms.has(code)) {
    rooms.set(code, new Set());
  }
  rooms.get(code).add(username);
  userRoom.set(username, code);
  return code;
}

function leaveRoom(username) {
  const code = userRoom.get(username);
  if (!code) return null;
  const members = rooms.get(code);
  if (members) {
    members.delete(username);
    if (members.size === 0) {
      rooms.delete(code);
    }
  }
  userRoom.delete(username);
  return code;
}

function getUserRoom(username) {
  return userRoom.get(username) || null;
}

function areInSameRoom(userA, userB) {
  const roomA = userRoom.get(userA);
  const roomB = userRoom.get(userB);
  return roomA != null && roomA === roomB;
}

function getRoomMembers(roomCode, excludeUsername) {
  const code = normalizeCode(roomCode);
  const members = rooms.get(code);
  if (!members) return [];
  return [...members].filter((u) => u !== excludeUsername);
}

function getAllRoomMembers(roomCode) {
  const code = normalizeCode(roomCode);
  const members = rooms.get(code);
  return members ? [...members] : [];
}

module.exports = {
  joinRoom,
  leaveRoom,
  getUserRoom,
  areInSameRoom,
  getRoomMembers,
  getAllRoomMembers,
  normalizeCode,
};
