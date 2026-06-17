const messageStore = require('./messageStore');
const demoSettings = require('./demoSettings');
const userStore = require('./userStore');

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function truncate(text, max = 80) {
  const s = String(text ?? '');
  return s.length > max ? `${s.slice(0, max)}…` : s;
}

function buildHealthHtml() {
  const demo = demoSettings.getSettings();
  const users = userStore.getStats();
  const msg = messageStore.getStats();
  const rows = msg.messages
    .map(
      (m, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${escapeHtml(m.from)}</td>
        <td>${escapeHtml(m.to)}</td>
        <td>${escapeHtml(new Date(m.timestamp).toLocaleString('vi-VN'))}</td>
        <td><code>${escapeHtml(truncate(m.content))}</code></td>
        <td>${m.encrypted ? '❌ Không (E2E)' : '⚠️ Có (plaintext demo)'}</td>
      </tr>`
    )
    .join('');

  const emptyRow =
    msg.messages.length === 0
      ? '<tr><td colspan="6" style="text-align:center;color:#666">Chưa có tin nhắn nào được lưu trên server</td></tr>'
      : '';

  return `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Secure P2P Chat — Health / Demo</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 24px; background: #f5f7fb; color: #1a1a1a; }
    h1 { margin-bottom: 4px; }
    .sub { color: #555; margin-bottom: 20px; }
    .cards { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
    .card { background: #fff; border-radius: 10px; padding: 14px 18px; box-shadow: 0 1px 4px rgba(0,0,0,.08); min-width: 160px; }
    .card b { display: block; font-size: 24px; }
    table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
    th, td { padding: 10px 12px; border-bottom: 1px solid #eee; text-align: left; vertical-align: top; }
    th { background: #1565C0; color: #fff; }
    code { font-size: 12px; word-break: break-all; }
    .badge { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 13px; }
    .on { background: #ffebee; color: #c62828; }
    .off { background: #e8f5e9; color: #2e7d32; }
    .note { background: #fff8e1; border-left: 4px solid #fbc02d; padding: 12px 14px; border-radius: 6px; margin: 16px 0; }
  </style>
</head>
<body>
  <h1>Secure P2P Chat — Server Health</h1>
  <p class="sub">Trang demo cho hội đồng — kiểm tra dữ liệu server đang lưu</p>

  <div class="cards">
    <div class="card">Trạng thái<b style="color:#2e7d32">OK</b></div>
    <div class="card">Tài khoản<b>${users.totalUsers}</b></div>
    <div class="card">Đang online<b>${users.onlineUsers}</b></div>
    <div class="card">Tin nhắn lưu trên server<b>${msg.messagesStored}</b></div>
  </div>

  <p>
    Lưu tin nhắn (demo):
    <span class="badge ${demo.storeMessagesOnServer ? 'on' : 'off'}">
      ${demo.storeMessagesOnServer ? 'BẬT' : 'TẮT'}
    </span>
    &nbsp;|&nbsp;
    Lưu plaintext (demo không an toàn):
    <span class="badge ${demo.storePlaintextOnServer ? 'on' : 'off'}">
      ${demo.storePlaintextOnServer ? 'BẬT' : 'TẮT'}
    </span>
  </p>

  <div class="note">
    <b>Chế độ mặc định (E2E):</b> Server <u>không lưu</u> tin nhắn — hacker lấy DB server cũng không có nội dung chat.<br/>
    <b>Bật lưu bản mã hóa:</b> Server chỉ thấy ciphertext — không đọc được nội dung.<br/>
    <b>Bật lưu plaintext (demo):</b> Mô phỏng chat server truyền thống — hacker đọc được nội dung.
  </div>

  <h2>Bảng tin nhắn trên server</h2>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Từ</th>
        <th>Đến</th>
        <th>Thời gian</th>
        <th>Nội dung server thấy</th>
        <th>Đọc được?</th>
      </tr>
    </thead>
    <tbody>
      ${rows}${emptyRow}
    </tbody>
  </table>

  <p class="sub" style="margin-top:20px">API JSON: <code>/health?format=json</code> · Cài đặt demo: <code>POST /api/demo/settings</code></p>
</body>
</html>`;
}

function buildHealthJson() {
  const demo = demoSettings.getSettings();
  const users = userStore.getStats();
  const msg = messageStore.getStats();
  return {
    status: 'ok',
    ...users,
    messagesStored: demo.storeMessagesOnServer ? msg.messagesStored : 0,
    demo,
    messages: demo.storeMessagesOnServer ? msg.messages : [],
  };
}

module.exports = { buildHealthHtml, buildHealthJson };
