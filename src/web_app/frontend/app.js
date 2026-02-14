/**
 * Comic-Crawler Web App - Frontend Logic
 * Kavita Style UI
 */

const API_BASE = 'http://127.0.0.1:8765';

const state = {
    currentPage: 'download',
    downloadTaskId: null,
    packTaskId: null,
    browserCallback: null,
    settings: {}
};

const elements = {};

function initElements() {
    elements.sidebar = document.getElementById('sidebar');
    elements.sidebarOverlay = document.getElementById('sidebar-overlay');
    elements.menuToggle = document.getElementById('menu-toggle');
    elements.navItems = document.querySelectorAll('.nav-item');
    elements.pageTitle = document.getElementById('page-title');
    elements.pageContents = document.querySelectorAll('.page-content');
    elements.apiStatus = document.getElementById('api-status');
    elements.connectionIndicator = document.getElementById('connection-indicator');
    
    elements.albumIds = document.getElementById('album-ids');
    elements.btnDownload = document.getElementById('btn-download');
    elements.btnClear = document.getElementById('btn-clear');
    elements.downloadPath = document.getElementById('download-path');
    elements.btnBrowseDownload = document.getElementById('btn-browse-download');
    elements.threadCount = document.getElementById('thread-count');
    elements.threadValue = document.getElementById('thread-value');
    elements.imageFormat = document.getElementById('image-format');
    elements.clientType = document.getElementById('client-type');
    elements.downloadProgress = document.getElementById('download-progress');
    elements.downloadProgressBar = document.getElementById('download-progress-bar');
    elements.downloadStatus = document.getElementById('download-status');
    elements.downloadTotal = document.getElementById('download-total');
    elements.downloadCompleted = document.getElementById('download-completed');
    elements.downloadFailed = document.getElementById('download-failed');
    elements.downloadLog = document.getElementById('download-log');
    elements.downloadTerminal = document.getElementById('download-terminal');
    
    elements.packSource = document.getElementById('pack-source');
    elements.packOutput = document.getElementById('pack-output');
    elements.btnBrowseSource = document.getElementById('btn-browse-source');
    elements.btnBrowseOutput = document.getElementById('btn-browse-output');
    elements.packOverwrite = document.getElementById('pack-overwrite');
    elements.compressLevel = document.getElementById('compress-level');
    elements.compressValue = document.getElementById('compress-value');
    elements.btnPack = document.getElementById('btn-pack');
    elements.btnSaveKavita = document.getElementById('btn-save-kavita');
    elements.packProgress = document.getElementById('pack-progress');
    elements.packProgressBar = document.getElementById('pack-progress-bar');
    elements.packStatus = document.getElementById('pack-status');
    elements.packTotal = document.getElementById('pack-total');
    elements.packSuccess = document.getElementById('pack-success');
    elements.packFailed = document.getElementById('pack-failed');
    elements.packLog = document.getElementById('pack-log');
    elements.packTerminal = document.getElementById('pack-terminal');
    
    elements.settingsDownloadPath = document.getElementById('settings-download-path');
    elements.settingsThreadCount = document.getElementById('settings-thread-count');
    elements.settingsImageFormat = document.getElementById('settings-image-format');
    elements.settingsClientType = document.getElementById('settings-client-type');
    elements.settingsKavitaOutput = document.getElementById('settings-kavita-output');
    elements.btnSaveSettings = document.getElementById('btn-save-settings');
    elements.btnResetSettings = document.getElementById('btn-reset-settings');
    elements.btnBrowseSettingsDownload = document.getElementById('btn-browse-settings-download');
    elements.btnBrowseSettingsKavita = document.getElementById('btn-browse-settings-kavita');
    
    elements.browserModal = document.getElementById('browser-modal');
    elements.browserCurrentPath = document.getElementById('browser-current-path');
    elements.browserPathIcon = document.getElementById('browser-path-icon');
    elements.browserList = document.getElementById('browser-list');
    elements.closeBrowser = document.getElementById('close-browser');
    elements.browserCancel = document.getElementById('browser-cancel');
    elements.browserSelect = document.getElementById('browser-select');
    elements.browserBack = document.getElementById('browser-back');
    elements.browserHome = document.getElementById('browser-home');
    elements.browserCurrentData = null;
    
    elements.btnStopService = document.getElementById('btn-stop-service');
}

function initEventListeners() {
    elements.menuToggle.addEventListener('click', toggleSidebar);
    elements.sidebarOverlay.addEventListener('click', toggleSidebar);
    
    elements.navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            switchPage(page);
        });
    });
    
    elements.btnDownload.addEventListener('click', startDownload);
    elements.btnClear.addEventListener('click', () => {
        elements.albumIds.value = '';
        addLog(elements.downloadLog, 'info', '已清空专辑列表');
    });
    
    elements.btnBrowseDownload.addEventListener('click', () => {
        openBrowser(elements.downloadPath.value, (path) => {
            elements.downloadPath.value = path;
        });
    });
    
    elements.threadCount.addEventListener('input', () => {
        elements.threadValue.textContent = elements.threadCount.value;
    });
    
    elements.btnBrowseSource.addEventListener('click', () => {
        openBrowser(elements.packSource.value, (path) => {
            elements.packSource.value = path;
        });
    });
    
    elements.btnBrowseOutput.addEventListener('click', () => {
        openBrowser(elements.packOutput.value, (path) => {
            elements.packOutput.value = path;
        });
    });
    
    elements.compressLevel.addEventListener('input', () => {
        elements.compressValue.textContent = elements.compressLevel.value;
    });
    
    elements.btnPack.addEventListener('click', startPack);
    elements.btnSaveKavita.addEventListener('click', saveKavitaSettings);
    elements.btnSaveSettings.addEventListener('click', saveSettings);
    elements.btnResetSettings.addEventListener('click', resetSettings);
    
    elements.btnBrowseSettingsDownload.addEventListener('click', () => {
        openBrowser(elements.settingsDownloadPath.value, (path) => {
            elements.settingsDownloadPath.value = path;
        });
    });
    
    elements.btnBrowseSettingsKavita.addEventListener('click', () => {
        openBrowser(elements.settingsKavitaOutput.value, (path) => {
            elements.settingsKavitaOutput.value = path;
        });
    });
    
    elements.browserBack.addEventListener('click', goBackDirectory);
    elements.browserHome.addEventListener('click', () => {
        browseDirectory('');
    });
    
    elements.closeBrowser.addEventListener('click', closeBrowser);
    elements.browserCancel.addEventListener('click', closeBrowser);
    elements.browserSelect.addEventListener('click', () => {
        const selectedPath = elements.browserCurrentPath.textContent;
        if (!selectedPath || selectedPath === '此电脑' || selectedPath === '') {
            alert('请先选择一个目录');
            return;
        }
        if (state.browserCallback) {
            state.browserCallback(selectedPath);
        }
        closeBrowser();
    });
    
    elements.btnStopService.addEventListener('click', stopService);
}

function toggleSidebar() {
    elements.sidebar.classList.toggle('open');
    elements.sidebarOverlay.classList.toggle('open');
}

function switchPage(page) {
    state.currentPage = page;
    
    elements.navItems.forEach(item => {
        if (item.dataset.page === page) {
            item.classList.add('active');
            item.classList.remove('text-gray-400');
            item.classList.add('text-gray-200');
        } else {
            item.classList.remove('active');
            item.classList.add('text-gray-400');
            item.classList.remove('text-gray-200');
        }
    });
    
    const titles = {
        'download': '下载管理',
        'kavita': 'Kavita 打包',
        'settings': '设置'
    };
    elements.pageTitle.textContent = titles[page] || page;
    
    elements.pageContents.forEach(content => {
        if (content.id === `page-${page}`) {
            content.classList.remove('hidden');
            content.classList.add('fade-in');
        } else {
            content.classList.add('hidden');
            content.classList.remove('fade-in');
        }
    });
    
    if (page === 'settings') {
        loadSettings();
    }
    
    if (window.innerWidth < 768) {
        elements.sidebar.classList.remove('open');
        elements.sidebarOverlay.classList.remove('open');
    }
}

async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE}/`);
        if (response.ok) {
            elements.apiStatus.textContent = '已连接';
            elements.apiStatus.classList.remove('text-red-500');
            elements.apiStatus.classList.add('text-primary');
            elements.connectionIndicator.innerHTML = '<i class="fas fa-circle text-green-500 text-xs"></i> 已连接';
            return true;
        }
    } catch (error) {
        elements.apiStatus.textContent = '未连接';
        elements.apiStatus.classList.add('text-red-500');
        elements.apiStatus.classList.remove('text-primary');
        elements.connectionIndicator.innerHTML = '<i class="fas fa-circle text-red-500 text-xs"></i> 未连接';
    }
    return false;
}

async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE}/api/settings`);
        if (response.ok) {
            state.settings = await response.json();
            applySettings();
        }
    } catch (error) {
        console.log('Using default settings');
    }
}

function applySettings() {
    const s = state.settings;
    if (s.download_path) {
        elements.downloadPath.value = s.download_path;
        elements.settingsDownloadPath.value = s.download_path;
    }
    if (s.thread_count) {
        elements.threadCount.value = s.thread_count;
        elements.threadValue.textContent = s.thread_count;
        elements.settingsThreadCount.value = s.thread_count;
    }
    if (s.image_format) {
        elements.imageFormat.value = s.image_format;
        elements.settingsImageFormat.value = s.image_format;
    }
    if (s.client_type) {
        elements.clientType.value = s.client_type;
        elements.settingsClientType.value = s.client_type;
    }
    if (s.kavita_output_dir) {
        elements.packOutput.value = s.kavita_output_dir;
        elements.settingsKavitaOutput.value = s.kavita_output_dir;
    }
}

async function saveSettings() {
    const settings = {
        download_path: elements.settingsDownloadPath.value,
        thread_count: parseInt(elements.settingsThreadCount.value),
        image_format: elements.settingsImageFormat.value,
        client_type: elements.settingsClientType.value,
        kavita_output_dir: elements.settingsKavitaOutput.value
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            state.settings = settings;
            applySettings();
            alert('设置已保存！');
        } else {
            alert('保存失败，请检查API连接');
        }
    } catch (error) {
        alert('保存失败: ' + error.message);
    }
}

async function saveKavitaSettings() {
    state.settings.kavita_output_dir = elements.packOutput.value;
    await saveSettings();
}

function resetSettings() {
    elements.settingsDownloadPath.value = '';
    elements.settingsThreadCount.value = 5;
    elements.settingsImageFormat.value = '.jpg';
    elements.settingsClientType.value = 'html';
    elements.settingsKavitaOutput.value = '';
}

async function startDownload() {
    const albumIdsText = elements.albumIds.value.trim();
    if (!albumIdsText) {
        alert('请输入专辑ID');
        return;
    }
    
    const albumIds = albumIdsText.split('\n')
        .map(id => id.trim())
        .filter(id => id.length > 0);
    
    if (albumIds.length === 0) {
        alert('请输入有效的专辑ID');
        return;
    }
    
    const request = {
        album_ids: albumIds,
        download_path: elements.downloadPath.value,
        thread_count: parseInt(elements.threadCount.value),
        image_format: elements.imageFormat.value,
        client_type: elements.clientType.value
    };
    
    elements.btnDownload.disabled = true;
    elements.btnDownload.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 下载中...';
    elements.downloadProgress.classList.remove('hidden');
    
    clearLog(elements.downloadLog);
    clearTerminal(elements.downloadTerminal);
    addLog(elements.downloadLog, 'info', `开始下载 ${albumIds.length} 个专辑...`);
    
    try {
        const response = await fetch(`${API_BASE}/api/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });
        
        if (response.ok) {
            const data = await response.json();
            state.downloadTaskId = data.task_id;
            pollDownloadStatus();
        } else {
            throw new Error('下载请求失败');
        }
    } catch (error) {
        addLog(elements.downloadLog, 'error', `启动下载失败: ${error.message}`);
        resetDownloadButton();
    }
}

async function pollDownloadStatus() {
    if (!state.downloadTaskId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/download/${state.downloadTaskId}`);
        if (!response.ok) {
            setTimeout(pollDownloadStatus, 2000);
            return;
        }
        
        const data = await response.json();
        updateDownloadProgress(data);
        
        await loadTerminalOutput(state.downloadTaskId, elements.downloadTerminal);
        
        if (data.status === 'running' || data.status === 'pending') {
            setTimeout(pollDownloadStatus, 1000);
        } else {
            resetDownloadButton();
            if (data.status === 'completed') {
                addLog(elements.downloadLog, 'success', '所有下载任务已完成！');
            } else {
                addLog(elements.downloadLog, 'error', '下载任务异常终止');
            }
        }
    } catch (error) {
        setTimeout(pollDownloadStatus, 2000);
    }
}

function updateDownloadProgress(data) {
    const total = data.album_ids.length;
    const completed = data.completed.length;
    const failed = data.failed.length;
    const progress = total > 0 ? Math.round((completed + failed) / total * 100) : 0;
    
    elements.downloadTotal.textContent = total;
    elements.downloadCompleted.textContent = completed;
    elements.downloadFailed.textContent = failed;
    elements.downloadProgressBar.style.width = `${progress}%`;
    elements.downloadStatus.textContent = data.status === 'running' ? '下载中...' : data.status;
    
    data.logs.slice(-5).forEach(log => {
        if (!elements.downloadLog.innerHTML.includes(log.message)) {
            addLog(elements.downloadLog, log.level, log.message);
        }
    });
}

function resetDownloadButton() {
    elements.btnDownload.disabled = false;
    elements.btnDownload.innerHTML = '<i class="fas fa-download"></i> 开始下载';
}

async function startPack() {
    const sourceDir = elements.packSource.value.trim();
    const outputDir = elements.packOutput.value.trim();
    
    if (!sourceDir) {
        alert('请选择源目录');
        return;
    }
    if (!outputDir) {
        alert('请选择输出目录');
        return;
    }
    
    const request = {
        source_dir: sourceDir,
        output_dir: outputDir,
        overwrite: elements.packOverwrite.checked,
        compress_level: parseInt(elements.compressLevel.value)
    };
    
    elements.btnPack.disabled = true;
    elements.btnPack.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 打包中...';
    elements.packProgress.classList.remove('hidden');
    
    clearLog(elements.packLog);
    clearTerminal(elements.packTerminal);
    addLog(elements.packLog, 'info', '开始扫描目录...');
    
    try {
        const response = await fetch(`${API_BASE}/api/pack`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });
        
        if (response.ok) {
            const data = await response.json();
            state.packTaskId = data.task_id;
            pollPackStatus();
        } else {
            throw new Error('打包请求失败');
        }
    } catch (error) {
        addLog(elements.packLog, 'error', `启动打包失败: ${error.message}`);
        resetPackButton();
    }
}

async function pollPackStatus() {
    if (!state.packTaskId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/pack/${state.packTaskId}`);
        if (!response.ok) {
            setTimeout(pollPackStatus, 2000);
            return;
        }
        
        const data = await response.json();
        updatePackProgress(data);
        
        await loadTerminalOutput(state.packTaskId, elements.packTerminal);
        
        if (data.status === 'running' || data.status === 'pending') {
            setTimeout(pollPackStatus, 1000);
        } else {
            resetPackButton();
            if (data.status === 'completed') {
                addLog(elements.packLog, 'success', `打包完成！成功: ${data.stats.success}, 失败: ${data.stats.failed}`);
            } else {
                addLog(elements.packLog, 'error', '打包任务异常终止');
            }
        }
    } catch (error) {
        setTimeout(pollPackStatus, 2000);
    }
}

function updatePackProgress(data) {
    const stats = data.stats;
    const progress = stats.total > 0 ? Math.round((stats.success + stats.failed) / stats.total * 100) : 0;
    
    elements.packTotal.textContent = stats.total;
    elements.packSuccess.textContent = stats.success;
    elements.packFailed.textContent = stats.failed;
    elements.packProgressBar.style.width = `${progress}%`;
    elements.packStatus.textContent = data.status === 'running' ? '打包中...' : data.status;
    
    data.logs.slice(-5).forEach(log => {
        if (!elements.packLog.innerHTML.includes(log.message)) {
            addLog(elements.packLog, log.level, log.message);
        }
    });
}

function resetPackButton() {
    elements.btnPack.disabled = false;
    elements.btnPack.innerHTML = '<i class="fas fa-box-archive"></i> 开始打包';
}

async function loadTerminalOutput(taskId, terminalElement) {
    try {
        const response = await fetch(`${API_BASE}/api/terminal/${taskId}`);
        if (!response.ok) {
            return;
        }
        
        const data = await response.json();
        updateTerminalOutput(data.output, terminalElement);
    } catch (error) {
        console.error('加载终端输出失败:', error);
    }
}

function updateTerminalOutput(lines, terminalElement) {
    terminalElement.innerHTML = '';
    lines.forEach(line => {
        const escapedLine = line
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        const div = document.createElement('div');
        div.className = 'log-item text-green-400';
        div.innerHTML = `&gt; ${escapedLine}`;
        terminalElement.appendChild(div);
    });
    terminalElement.scrollTop = terminalElement.scrollHeight;
}

function clearTerminal(terminalElement) {
    terminalElement.innerHTML = '<div class="log-item text-green-400">&gt; 等待执行任务...</div>';
}

function goBackDirectory() {
    if (!elements.browserCurrentData) {
        return;
    }
    if (elements.browserCurrentData.is_root) {
        return;
    }
    if (elements.browserCurrentData.parent) {
        browseDirectory(elements.browserCurrentData.parent);
    } else {
        browseDirectory('');
    }
}

async function openBrowser(currentPath, callback) {
    state.browserCallback = callback;
    elements.browserModal.classList.remove('hidden');
    await browseDirectory(currentPath || '');
}

async function browseDirectory(path) {
    try {
        if (path === '此电脑' || path === '') {
            path = '';
        }
        const response = await fetch(`${API_BASE}/api/browse?path=${encodeURIComponent(path)}`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || '浏览失败');
        }
        
        const data = await response.json();
        elements.browserCurrentData = data;
        
        if (data.is_root) {
            elements.browserCurrentPath.textContent = '此电脑';
            elements.browserPathIcon.className = 'fas fa-desktop text-primary';
            elements.browserBack.disabled = true;
        } else {
            elements.browserCurrentPath.textContent = data.current;
            elements.browserPathIcon.className = 'fas fa-folder text-primary';
            elements.browserBack.disabled = !data.parent;
        }
        
        let html = '';
        
        if (data.is_root) {
            html += `
                <div class="flex items-center gap-3 p-3 bg-surface rounded-lg mb-2">
                    <i class="fas fa-desktop text-primary"></i>
                    <span class="font-semibold">此电脑</span>
                </div>
            `;
        }
        
        data.items.filter(item => item.is_dir).forEach(item => {
            const icon = data.is_root ? 'fa-hdd' : 'fa-folder';
            const escapedPath = item.path.replace(/\\/g, '\\\\');
            html += `
                <div class="flex items-center gap-3 p-3 hover:bg-surface-lighter rounded-lg cursor-pointer browser-item" data-path="${escapedPath}">
                    <i class="fas ${icon} text-primary"></i>
                    <span>${item.name}</span>
                </div>
            `;
        });
        
        elements.browserList.innerHTML = html || '<div class="text-center text-gray-400 py-8">空目录</div>';
        
        elements.browserList.querySelectorAll('.browser-item').forEach(item => {
            item.addEventListener('click', () => {
                const itemPath = item.dataset.path;
                browseDirectory(itemPath);
            });
        });
        
    } catch (error) {
        elements.browserList.innerHTML = `<div class="text-center text-red-400 py-8">${error.message}</div>`;
    }
}

function closeBrowser() {
    elements.browserModal.classList.add('hidden');
    state.browserCallback = null;
}

function addLog(container, level, message) {
    const time = new Date().toLocaleTimeString();
    const levelClass = `log-${level}`;
    const levelText = level.toUpperCase();
    
    const html = `
        <div class="log-item ${levelClass}">
            <span class="text-gray-500">[${time}]</span>
            <span class="text-gray-400">[${levelText}]</span>
            ${message}
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', html);
    container.scrollTop = container.scrollHeight;
}

function clearLog(container) {
    container.innerHTML = '';
}

async function stopService() {
    if (!confirm('确定要停止后端和前端服务吗？\n停止后需要重新运行 start.bat 才能再次使用。')) {
        return;
    }
    
    try {
        elements.btnStopService.disabled = true;
        elements.btnStopService.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 正在停止...';
        
        await fetch(`${API_BASE}/api/shutdown`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        alert('服务正在停止中...\n\n请运行 end.bat 来停止所有服务，或手动关闭相关进程。\n\n如需重新使用，请运行 start.bat');
        
        elements.btnStopService.innerHTML = '<i class="fas fa-check"></i> 已发送停止请求';
        
    } catch (error) {
        elements.btnStopService.disabled = false;
        elements.btnStopService.innerHTML = '<i class="fas fa-stop-circle"></i> 停止服务';
        alert('停止服务请求发送失败，请手动运行 end.bat');
    }
}

window.browseDirectory = browseDirectory;

document.addEventListener('DOMContentLoaded', () => {
    initElements();
    initEventListeners();
    checkApiStatus();
    loadSettings();
    
    setInterval(checkApiStatus, 30000);
});
