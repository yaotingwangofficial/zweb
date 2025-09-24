// task_instance.js  —— 自动从后端检索分页数据
(function () {
  let CONFIG = {
    PAGE_SIZE: 10,
    API_BASE: '',
    API_PATH: '/api/videos'
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

  async function init() {
    try {
      // Fetch configuration from backend
      const configResponse = await fetch('/api/config');
      if (configResponse.ok) {
        CONFIG = {...CONFIG, ...await configResponse.json()};
      }
    } catch (error) {
      console.warn('Failed to load config from server, using defaults:', error);
    }
    
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
      console.log('Loading page:', state.page);
      const { total, items } = await fetchVideos(state.page, CONFIG.PAGE_SIZE);
      console.log('Fetched items:', items);
      state.total = total;
      state.totalPages = Math.max(1, Math.ceil(total / CONFIG.PAGE_SIZE));
      
      // Filter out already annotated tasks
      console.log('Filtering items...');
      const unannotatedItems = [];
      for (const item of items) {
        const videoInfo = parseVideoPath(item);
        console.log('Checking item:', videoInfo);
        const isAnnotated = await checkIfAnnotated(videoInfo.category, videoInfo.baseName);
        console.log('Is annotated:', isAnnotated, 'for', videoInfo.category, videoInfo.baseName);
        if (!isAnnotated) {
          unannotatedItems.push(item);
        }
      }
      
      console.log('Unannotated items:', unannotatedItems);
      state.itemsOnPage = unannotatedItems;
      render();
    } catch (err) {
      console.error(err);
      showError('加载失败：' + (err.message || '未知错误'));
    }
  }

  async function checkIfAnnotated(category, baseName) {
    try {
      // Construct the expected annotation filename
      const fileName = `${category}+${baseName}.json`;
      console.log('Checking annotation file:', fileName);
      
      // Check if annotation file exists
      const url = `${CONFIG.API_BASE}/api/videos/check-annotation-exists?file=${encodeURIComponent(fileName)}`;
      console.log('Request URL:', url);
      
      const response = await fetch(url);
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const result = await response.json();
        console.log('Check result:', result);
        return result.exists;
      }
      console.log('Response not OK');
      return false;
    } catch (error) {
      console.error('Error checking annotation status:', error);
      return false; // If we can't check, assume it's not annotated
    }
  }

  async function fetchVideos(page, pageSize) {
    const url = `${CONFIG.API_BASE}${CONFIG.API_PATH}?page=${page}&page_size=${pageSize}`;
    console.log('Fetching videos from:', url);
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    console.log('Videos data:', data);

    // 期望：{ total:number, items:string[] }
    if (typeof data.total !== 'number' || !Array.isArray(data.items)) {
      throw new Error('响应格式不正确');
    }
    return data;
  }

  function render() {
    console.log('Rendering items:', state.itemsOnPage);
    els.tbody.innerHTML = '';
    const startIndex = (state.page - 1) * CONFIG.PAGE_SIZE + 1;

    // Check if there are no unannotated tasks
    if (state.itemsOnPage.length === 0) {
      console.log('No unannotated items to display');
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td colspan="3" class="muted tc">暂无未标注的任务</td>
      `;
      els.tbody.appendChild(tr);
    } else {
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
    }

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
    // 目标：  /SVTrack/dataset/website/frontend/task_instance/annotate.html?category=<category>&basename=<baseName>.html
    const current = window.location.pathname.replace(/\\/g, '/');
    const frontendRoot = current.replace(/\/task_instance\.html$/, '');
    return `${frontendRoot}/task_instance/annotate.html?category=${encodeURIComponent(category)}&baseName=${encodeURIComponent(baseName)}`;
  }

  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }
  function showError(msg) {
    if (!msg) { els.errorBox.hidden = true; els.errorBox.textContent = ''; return; }
    els.errorBox.hidden = false; els.errorBox.textContent = msg;
  }
})();