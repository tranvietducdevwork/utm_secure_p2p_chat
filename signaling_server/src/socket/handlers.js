const jwt = require('jsonwebtoken');
const userStore = require('../store/userStore');
const roomStore = require('../store/roomStore');

const JWT_SECRET = process.env.JWT_SECRET || 'secure-p2p-chat-dev-secret-change-in-production';

function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch {
    return null;
  }
}

function usersForRoom(roomCode, excludeUsername) {
  return roomStore
    .getRoomMembers(roomCode, excludeUsername)
    .map((name) => userStore.findByUsername(name))
    .filter(Boolean)
    .map((u) => ({
      id: u.id,
      username: u.username,
      publicKey: u.publicKey,
      online: u.online,
    }));
}

function broadcastRoomUsers(io, roomCode) {
  const code = roomStore.normalizeCode(roomCode);
  for (const username of roomStore.getAllRoomMembers(code)) {
    const socketId = userStore.getSocketId(username);
    if (!socketId) continue;
    io.to(socketId).emit('room-users', {
      roomCode: code,
      users: usersForRoom(code, username),
    });
  }
}

function canTalk(currentUser, targetUsername) {
  if (!currentUser || !targetUsername) return false;
  return roomStore.areInSameRoom(currentUser.username, targetUsername);
}

function registerSocketHandlers(io) {
  io.on('connection', (socket) => {
    let currentUser = null;

    socket.on('authenticate', ({ token }) => {
      const payload = verifyToken(token);
      if (!payload?.username) {
        socket.emit('auth-error', { message: 'Invalid token' });
        return;
      }
      const user = userStore.findByUsername(payload.username);
      if (!user) {
        socket.emit('auth-error', { message: 'User not found' });
        return;
      }
      currentUser = userStore.setOnline(payload.username, socket.id);
      socket.emit('authenticated', { user: currentUser });
      console.log(`[auth] ${payload.username} connected`);
    });

    socket.on('join-room', ({ roomCode }) => {
      if (!currentUser) return;
      try {
        const code = roomStore.joinRoom(currentUser.username, roomCode);
        socket.join(`room:${code}`);

        const peers = usersForRoom(code, currentUser.username);
        socket.emit('room-joined', { roomCode: code, users: peers });
        socket.to(`room:${code}`).emit('user-joined-room', {
          roomCode: code,
          user: currentUser,
        });
        broadcastRoomUsers(io, code);
        console.log(`[room] ${currentUser.username} joined ${code} (${peers.length + 1} total)`);
      } catch (err) {
        socket.emit('room-error', { message: 'Mã phòng không hợp lệ (tối thiểu 4 ký tự)' });
      }
    });

    socket.on('leave-room', () => {
      if (!currentUser) return;
      const code = roomStore.leaveRoom(currentUser.username);
      if (code) {
        socket.leave(`room:${code}`);
        socket.to(`room:${code}`).emit('user-left-room', {
          username: currentUser.username,
          roomCode: code,
        });
        broadcastRoomUsers(io, code);
      }
      socket.emit('room-left', {});
    });

    socket.on('get-room-users', () => {
      if (!currentUser) return;
      const code = roomStore.getUserRoom(currentUser.username);
      if (!code) return;
      socket.emit('room-users', {
        roomCode: code,
        users: usersForRoom(code, currentUser.username),
      });
    });

    socket.on('webrtc-offer', ({ to, offer }) => {
      if (!currentUser || !canTalk(currentUser, to)) return;
      const targetSocket = userStore.getSocketId(to);
      if (targetSocket) {
        io.to(targetSocket).emit('webrtc-offer', { from: currentUser.username, offer });
      }
    });

    socket.on('webrtc-answer', ({ to, answer }) => {
      if (!currentUser || !canTalk(currentUser, to)) return;
      const targetSocket = userStore.getSocketId(to);
      if (targetSocket) {
        io.to(targetSocket).emit('webrtc-answer', { from: currentUser.username, answer });
      }
    });

    socket.on('ice-candidate', ({ to, candidate }) => {
      if (!currentUser || !canTalk(currentUser, to)) return;
      const targetSocket = userStore.getSocketId(to);
      if (targetSocket) {
        io.to(targetSocket).emit('ice-candidate', { from: currentUser.username, candidate });
      }
    });

    socket.on('e2e-message', ({ to, payload }) => {
      if (!currentUser || !payload || !canTalk(currentUser, to)) return;
      const targetSocket = userStore.getSocketId(to);
      if (targetSocket) {
        io.to(targetSocket).emit('e2e-message', { from: currentUser.username, payload });
      }
    });

    socket.on('disconnect', () => {
      if (!currentUser) return;
      const username = currentUser.username;
      const roomCode = roomStore.leaveRoom(username);
      userStore.setOffline(socket.id);
      if (roomCode) {
        socket.to(`room:${roomCode}`).emit('user-left-room', { username, roomCode });
        broadcastRoomUsers(io, roomCode);
      }
      console.log(`[disconnect] ${username}`);
      currentUser = null;
    });
  });
}

module.exports = { registerSocketHandlers, JWT_SECRET };
