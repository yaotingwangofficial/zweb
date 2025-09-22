// task_instance.js  —— 自动从后端检索分页数据
(function () {
  const CONFIG = {
    PAGE_SIZE: 10,

    // 后端 API 地址：请按实际端口/域名调整
    API_BASE: 'http://10.0.0.43:8012',
    API_PATH: '/api/videos',

    // 后端会从 VIDEOS_ROOT 环境变量读取根路径，这里无需再传 store
  };

  const els = {
    tbody: null,
    prevBtn: null,
    nextBtn: null,
    pageNow: null,
    pageTotal: null,
    rangeText: null,
    totalCount: null,
    jumpForm: null,
    jumpInput: null,
    errorBox: null
  };

  const state = {
    page: 1,
    total: 0,
    totalPages: 1,
    itemsOnPage: []
  };

  document.addEventListener('DOMContentLoaded', init);

  function init() {
    els.tbody = document.getElementById('listBody');
    els.prevBtn = document.getElementById('prevBtn');
    els.nextBtn = document.getElementById('nextBtn');
    els.pageNow = document.getElementById('pageNow');
    els.pageTotal = document.getElementById('pageTotal');
    els.rangeText = document.getElementById('rangeText');
    els.totalCount = document.getElementById('totalCount');
    els.jumpForm = document.getElementById('jumpForm');
    els.jumpInput = document.getElementById('jumpInput');
    els.errorBox = document.getElementById('errorBox');

    const urlPage = parseInt(new URLSearchParams(location.search).get('page'), 10);
    if (!Number.isNaN(urlPage) && urlPage > 0) state.page = urlPage;

    els.prevBtn.addEventListener('click', () => goToPage(state.page - 1));
    els.nextBtn.addEventListener('click', () => goToPage(state.page + 1));
    els.jumpForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const p = parseInt(els.jumpInput.value, 10);
      if (!Number.isNaN(p)) goToPage(p);
    });

    load();
  }

  function goToPage(p) {
    const target = clamp(p, 1, state.totalPages || 1);
    if (target === state.page) return;
    const params = new URLSearchParams(location.search);
    params.set('page', target);
    history.replaceState(null, '', `${location.pathname}?${params.toString()}`);
    state.page = target;
    load();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function load() {
    showError('');
    try {
      const { total, items } = await fetchVideos(state.page, CONFIG.PAGE_SIZE);
      state.total = total;
      state.totalPages = Math.max(1, Math.ceil(total / CONFIG.PAGE_SIZE));
      state.itemsOnPage = items;
      render();
    } catch (err) {
      console.error(err);
      showError('加载失败：' + (err.message || '未知错误'));
    }
  }

  async function fetchVideos(page, pageSize) {
    const url = `${CONFIG.API_BASE}${CONFIG.API_PATH}`;
    // const url = `${CONFIG.API_BASE}${CONFIG.API_PATH}?page=${page}&pageSize=${pageSize}`;
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    // 期望：{ total:number, items:string[] }
    if (typeof data.total !== 'number' || !Array.isArray(data.items)) {
      throw new Error('响应格式不正确');
    }
    return data;
  }

  function render() {
    els.tbody.innerHTML = '';
    const startIndex = (state.page - 1) * CONFIG.PAGE_SIZE + 1;

    state.itemsOnPage.forEach((raw, idx) => {
      const info = parseVideoPath(raw);
      const target = buildTargetHtmlPath(info.category, info.baseName);

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>
          <a class="btn btn--primary btn--sm" href="${target}">开始</a>
        </td>
        <td class="num">${startIndex + idx}</td>
        <td class="mono">${info.displayName}</td>
      `;
      els.tbody.appendChild(tr);
    });

    els.pageNow.textContent = String(state.page);
    els.pageTotal.textContent = String(state.totalPages);
    els.totalCount.textContent = String(state.total);

    const rangeEnd = Math.min(state.total, startIndex + state.itemsOnPage.length - 1);
    els.rangeText.textContent = state.itemsOnPage.length ? `${startIndex}–${rangeEnd}` : '—';

    els.prevBtn.disabled = state.page <= 1;
    els.nextBtn.disabled = state.page >= state.totalPages;
  }

  function parseVideoPath(p) {
    // 支持三种输入：
    // 1) 绝对 windows 路径: D:\SVTrack\Videos_v1\anime_Conan\1_merged.mp4
    // 2) 绝对/相对 *nix 路径: /data/SVTrack/Videos_v1/anime_Conan/1_merged.mp4
    // 3) 仅相对根的路径:     anime_Conan/1_merged.mp4
    const norm = String(p).replace(/\\/g, '/');

    let after = norm;
    const key = '/videos_v1/';
    const j = norm.toLowerCase().lastIndexOf(key);
    if (j >= 0) after = norm.slice(j + key.length);

    const parts = after.split('/').filter(Boolean);
    const filename = parts[parts.length - 1] || 'unknown.mp4';
    const category = parts.length >= 2 ? parts[parts.length - 2] : 'unknown';
    const baseName = filename.replace(/\.[^.]+$/, '');
    const displayName = `${category}\\${baseName}`;
    return { category, filename, baseName, displayName };
  }

  function buildTargetHtmlPath(category, baseName) {
    // 当前页：/SVTrack/dataset/website/frontend/task_instance.html
    // 目标：  /SVTrack/dataset/website/frontend/task_instance/<category>/<baseName>.html
    const current = window.location.pathname.replace(/\\/g, '/');
    const frontendRoot = current.replace(/\/task_instance\.html$/, '');
    return `${frontendRoot}/task_instance/${encodeURIComponent(category)}/${encodeURIComponent(baseName)}.html`;
  }

  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
  function showError(msg) {
    if (!msg) { els.errorBox.hidden = true; els.errorBox.textContent = ''; return; }
    els.errorBox.hidden = false; els.errorBox.textContent = msg;
  }
})();
