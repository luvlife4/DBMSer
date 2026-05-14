const msgs = document.getElementById('messages');
const input = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
}

function append(role, text) {
  const div = document.createElement('div');
  div.className = 'bubble ' + role;
  div.innerHTML = role === 'assistant' ? marked.parse(text) : text;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}

async function send() {
  const msg = input.value.trim();
  if (!msg) return;
  removeWelcome();
  append('user', msg);
  input.value = '';
  sendBtn.disabled = true;
  const replyDiv = append('assistant', '<span class="loading"></span>');

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    replyDiv.innerHTML = marked.parse(data.reply);
  } catch (e) {
    replyDiv.innerHTML = '请求失败: ' + e.message;
  }
  sendBtn.disabled = false;
  input.focus();
}

function removeWelcome() {
  const w = document.querySelector('.welcome');
  if (w) w.remove();
}

function newChat() {
  msgs.innerHTML = '<div class="welcome"><h2>DBMSer</h2><p>我是你的数据库课程学伴，可以问我任何数据库相关的问题</p></div>';
  fetch('/new-chat', { method: 'POST' }).catch(() => {});
}

async function openPortrait() {
  const overlay = document.getElementById('portraitOverlay');
  const body = document.getElementById('portraitBody');
  overlay.classList.add('show');
  body.innerHTML = '<div class="portrait-loading">生成中...</div>';
  try {
    const res = await fetch('/learning-portrait', { method: 'POST' });
    const data = await res.json();
    body.innerHTML = marked.parse(data.report);
  } catch (e) {
    body.innerHTML = '<div class="portrait-loading">加载失败: ' + e.message + '</div>';
  }
}

function closePortrait(e) {
  if (e && e.target !== document.getElementById('portraitOverlay')) return;
  document.getElementById('portraitOverlay').classList.remove('show');
}

async function openSchedule() {
  const overlay = document.getElementById('scheduleOverlay');
  const body = document.getElementById('scheduleBody');
  overlay.classList.add('show');
  body.innerHTML = '<div class="portrait-loading">提取中...</div>';
  try {
    const res = await fetch('/learning-schedule', { method: 'POST' });
    const data = await res.json();
    body.innerHTML = marked.parse(data.schedule);
  } catch (e) {
    body.innerHTML = '<div class="portrait-loading">加载失败: ' + e.message + '</div>';
  }
}

function closeSchedule(e) {
  if (e && e.target !== document.getElementById('scheduleOverlay')) return;
  document.getElementById('scheduleOverlay').classList.remove('show');
}
