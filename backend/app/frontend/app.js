// 简易“登录态”工具（仅演示；生产应改为后端会话/令牌）:
const AUTH = {
  key: 'dl_user',
  getUser() {
    try { return JSON.parse(localStorage.getItem(this.key)); } catch { return null; }
  },
  login(username) {
    localStorage.setItem(this.key, JSON.stringify({ username, ts: Date.now() }));
  },
  logout() {
    localStorage.removeItem(this.key);
    // 返回登录页
    window.location.href = 'index.html';
  },
  isAuthed() {
    return !!this.getUser();
  },
  requireAuth() {
    if (!this.isAuthed()) {
      // 未登录则跳回首页
      window.location.replace('index.html');
    }
  }
};

const UI = {
  mountUserHeader(nameElId, logoutBtnId) {
    const user = AUTH.getUser();
    const nameEl = document.getElementById(nameElId);
    const btn = document.getElementById(logoutBtnId);

    if (user && nameEl) {
      nameEl.textContent = `${user.username}`;
    }
    if (btn) {
      btn.addEventListener('click', AUTH.logout.bind(AUTH));
    }
  }
};
