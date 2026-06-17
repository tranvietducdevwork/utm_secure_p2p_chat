const express = require('express');
const http = require('http');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { Server } = require('socket.io');
const userStore = require('./store/userStore');
const { registerSocketHandlers, JWT_SECRET } = require('./socket/handlers');

const PORT = process.env.PORT || 3000;
const app = express();
const server = http.createServer(app);

const io = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] },
});

app.use(cors());
app.use(express.json());

function signToken(username) {
  return jwt.sign({ username }, JWT_SECRET, { expiresIn: '7d' });
}

// Health check
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', ...userStore.getStats() });
});

// Register - stores only username, password hash, and public key
app.post('/api/register', async (req, res) => {
  try {
    const { username, password, publicKey } = req.body;
    if (!username || !password || !publicKey) {
      return res.status(400).json({ error: 'username, password, and publicKey are required' });
    }
    if (username.length < 3 || password.length < 6) {
      return res.status(400).json({ error: 'username min 3 chars, password min 6 chars' });
    }
    const passwordHash = await bcrypt.hash(password, 10);
    const user = userStore.createUser({ username, passwordHash, publicKey });
    const token = signToken(username);
    res.status(201).json({ token, user });
  } catch (err) {
    if (err.message === 'USERNAME_EXISTS') {
      return res.status(409).json({ error: 'Username already exists' });
    }
    res.status(500).json({ error: 'Registration failed' });
  }
});

// Login
app.post('/api/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = userStore.findByUsername(username);
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    const valid = await bcrypt.compare(password, user.passwordHash);
    if (!valid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    const token = signToken(username);
    res.json({
      token,
      user: {
        id: user.id,
        username: user.username,
        publicKey: user.publicKey,
        online: user.online,
      },
    });
  } catch {
    res.status(500).json({ error: 'Login failed' });
  }
});

// Get user public key for E2E key exchange
app.get('/api/users/:username/public-key', (req, res) => {
  const user = userStore.findByUsername(req.params.username);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json({ username: user.username, publicKey: user.publicKey });
});

// Sync public key after login (keeps E2E working across reinstalls)
app.post('/api/sync-public-key', (req, res) => {
  try {
    const auth = req.headers.authorization?.replace('Bearer ', '');
    const payload = auth ? jwt.verify(auth, JWT_SECRET) : null;
    if (!payload?.username) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    const { publicKey } = req.body;
    if (!publicKey) {
      return res.status(400).json({ error: 'publicKey required' });
    }
    const user = userStore.updatePublicKey(payload.username, publicKey);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    res.json({ user });
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
});

// Explicitly no message endpoints - privacy by design
app.all('/api/messages*', (_req, res) => {
  res.status(404).json({
    error: 'Message storage is not supported. Messages are P2P encrypted only.',
  });
});

registerSocketHandlers(io);

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`\nPort ${PORT} đang được dùng. Chạy lệnh sau rồi thử lại:\n`);
    console.error(`  kill $(lsof -t -i:${PORT})`);
    console.error(`\nHoặc dùng port khác: PORT=3001 npm start\n`);
    process.exit(1);
  }
  throw err;
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Signaling server running on http://0.0.0.0:${PORT}`);
  console.log('Policy: NO message content is stored on this server.');
});
