/**
 * 前端 HTML（内嵌在 Worker 中）
 */

export const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CPA 账号管理系统</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
    }

    .header {
      background: white;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .header h1 {
      color: #333;
      font-size: 28px;
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.3s;
    }

    .btn-primary {
      background: #667eea;
      color: white;
    }

    .btn-primary:hover {
      background: #5568d3;
    }

    .btn-danger {
      background: #f56565;
      color: white;
    }

    .btn-danger:hover {
      background: #e53e3e;
    }

    .btn-success {
      background: #48bb78;
      color: white;
    }

    .btn-success:hover {
      background: #38a169;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 24px;
    }

    .stat-card {
      background: white;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .stat-card h3 {
      color: #666;
      font-size: 14px;
      margin-bottom: 8px;
    }

    .stat-card .value {
      color: #333;
      font-size: 32px;
      font-weight: bold;
    }

    .main-content {
      background: white;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
      border-bottom: 2px solid #e2e8f0;
    }

    .tab {
      padding: 12px 24px;
      background: none;
      border: none;
      cursor: pointer;
      font-size: 16px;
      color: #666;
      border-bottom: 3px solid transparent;
      transition: all 0.3s;
    }

    .tab.active {
      color: #667eea;
      border-bottom-color: #667eea;
    }

    .tab-content {
      display: none;
    }

    .tab-content.active {
      display: block;
    }

    .server-list {
      display: grid;
      gap: 16px;
    }

    .server-card {
      border: 2px solid #e2e8f0;
      border-radius: 8px;
      padding: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: all 0.3s;
    }

    .server-card:hover {
      border-color: #667eea;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
    }

    .server-info h3 {
      color: #333;
      margin-bottom: 8px;
    }

    .server-info p {
      color: #666;
      font-size: 14px;
    }

    .server-actions {
      display: flex;
      gap: 8px;
    }

    .account-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 16px;
    }

    .account-table th,
    .account-table td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #e2e8f0;
    }

    .account-table th {
      background: #f7fafc;
      color: #666;
      font-weight: 600;
    }

    .account-table tr:hover {
      background: #f7fafc;
    }

    .status-badge {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
    }

    .status-ready {
      background: #c6f6d5;
      color: #22543d;
    }

    .status-error {
      background: #fed7d7;
      color: #742a2a;
    }

    .status-disabled {
      background: #e2e8f0;
      color: #4a5568;
    }

    .login-container {
      max-width: 400px;
      margin: 100px auto;
      background: white;
      border-radius: 12px;
      padding: 40px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .login-container h2 {
      text-align: center;
      color: #333;
      margin-bottom: 32px;
    }

    .form-group {
      margin-bottom: 20px;
    }

    .form-group label {
      display: block;
      color: #666;
      margin-bottom: 8px;
      font-weight: 500;
    }

    .form-group input {
      width: 100%;
      padding: 12px;
      border: 2px solid #e2e8f0;
      border-radius: 6px;
      font-size: 14px;
      transition: border-color 0.3s;
    }

    .form-group input:focus {
      outline: none;
      border-color: #667eea;
    }

    .loading {
      text-align: center;
      padding: 40px;
      color: #666;
    }

    .modal {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      z-index: 1000;
      align-items: center;
      justify-content: center;
    }

    .modal.active {
      display: flex;
    }

    .modal-content {
      background: white;
      border-radius: 12px;
      padding: 32px;
      max-width: 500px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
    }

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .modal-header h2 {
      color: #333;
    }

    .close-btn {
      background: none;
      border: none;
      font-size: 24px;
      cursor: pointer;
      color: #666;
    }

    .hidden {
      display: none !important;
    }
  </style>
</head>
<body>
  <!-- 登录页面 -->
  <div id="loginPage" class="login-container">
    <h2>🔐 CPA 管理系统</h2>
    <form id="loginForm">
      <div class="form-group">
        <label>用户名</label>
        <input type="text" id="username" required>
      </div>
      <div class="form-group">
        <label>密码</label>
        <input type="password" id="password" required>
      </div>
      <button type="submit" class="btn btn-primary" style="width: 100%;">登录</button>
    </form>
  </div>

  <!-- 主页面 -->
  <div id="mainPage" class="hidden">
    <div class="container">
      <!-- 头部 -->
      <div class="header">
        <h1>🚀 CPA 账号管理系统</h1>
        <div class="user-info">
          <span id="username-display"></span>
          <button class="btn btn-danger" onclick="logout()">退出</button>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <h3>总服务器数</h3>
          <div class="value" id="stat-servers">0</div>
        </div>
        <div class="stat-card">
          <h3>总账号数</h3>
          <div class="value" id="stat-accounts">0</div>
        </div>
        <div class="stat-card">
          <h3>活跃账号</h3>
          <div class="value" id="stat-active">0</div>
        </div>
        <div class="stat-card">
          <h3>禁用账号</h3>
          <div class="value" id="stat-disabled">0</div>
        </div>
      </div>

      <!-- 主内容 -->
      <div class="main-content">
        <div class="tabs">
          <button class="tab active" onclick="switchTab('servers')">服务器管理</button>
          <button class="tab" onclick="switchTab('accounts')">账号管理</button>
          <button class="tab" onclick="switchTab('operations')">批量操作</button>
        </div>

        <!-- 服务器管理 -->
        <div id="tab-servers" class="tab-content active">
          <button class="btn btn-primary" onclick="showAddServerModal()">➕ 添加服务器</button>
          <div id="server-list" class="server-list" style="margin-top: 20px;"></div>
        </div>

        <!-- 账号管理 -->
        <div id="tab-accounts" class="tab-content">
          <div class="form-group">
            <label>选择服务器</label>
            <select id="account-server-select" onchange="loadAccounts()">
              <option value="">请选择服务器</option>
            </select>
          </div>
          <div id="accounts-container"></div>
        </div>

        <!-- 批量操作 -->
        <div id="tab-operations" class="tab-content">
          <div class="form-group">
            <label>选择服务器</label>
            <select id="operation-server-select">
              <option value="">请选择服务器</option>
            </select>
          </div>
          <div style="display: flex; gap: 12px; margin-top: 20px;">
            <button class="btn btn-primary" onclick="checkUsage()">检查使用情况</button>
            <button class="btn btn-success" onclick="downloadPack()">下载打包</button>
            <button class="btn btn-primary" onclick="showUploadModal()">批量上传</button>
          </div>
          <div id="operation-result" style="margin-top: 20px;"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- 添加服务器模态框 -->
  <div id="addServerModal" class="modal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>添加 CPA 服务器</h2>
        <button class="close-btn" onclick="closeModal('addServerModal')">&times;</button>
      </div>
      <form id="addServerForm">
        <div class="form-group">
          <label>服务器名称</label>
          <input type="text" id="server-name" required>
        </div>
        <div class="form-group">
          <label>Base URL</label>
          <input type="url" id="server-url" required placeholder="https://example.com">
        </div>
        <div class="form-group">
          <label>管理 Token</label>
          <input type="text" id="server-token" required>
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" id="server-revive" checked>
            启用 Token 自动复活
          </label>
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%;">添加</button>
      </form>
    </div>
  </div>

  <script>
    let token = localStorage.getItem('token');
    let currentServers = [];

    // 初始化
    if (token) {
      document.getElementById('loginPage').classList.add('hidden');
      document.getElementById('mainPage').classList.remove('hidden');
      init();
    }

    // 登录
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });

        const data = await res.json();
        if (data.token) {
          token = data.token;
          localStorage.setItem('token', token);
          document.getElementById('loginPage').classList.add('hidden');
          document.getElementById('mainPage').classList.remove('hidden');
          init();
        } else {
          alert('登录失败：' + (data.error || '未知错误'));
        }
      } catch (error) {
        alert('登录失败：' + error.message);
      }
    });

    // 登出
    function logout() {
      localStorage.removeItem('token');
      location.reload();
    }

    // 初始化
    async function init() {
      await loadStats();
      await loadServers();
    }

    // 加载统计
    async function loadStats() {
      try {
        const res = await fetch('/api/stats/overview', {
          headers: { 'Authorization': \`Bearer \${token}\` }
        });
        const data = await res.json();
        
        if (data.success) {
          document.getElementById('stat-servers').textContent = data.overview.total_servers;
          document.getElementById('stat-accounts').textContent = data.overview.total_accounts;
          document.getElementById('stat-active').textContent = data.overview.total_active;
          document.getElementById('stat-disabled').textContent = data.overview.total_disabled;
        }
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
    }

    // 加载服务器列表
    async function loadServers() {
      try {
        const res = await fetch('/api/servers', {
          headers: { 'Authorization': \`Bearer \${token}\` }
        });
        const data = await res.json();
        
        if (data.success) {
          currentServers = data.servers;
          renderServers(data.servers);
          updateServerSelects(data.servers);
        }
      } catch (error) {
        console.error('Failed to load servers:', error);
      }
    }

    // 渲染服务器列表
    function renderServers(servers) {
      const container = document.getElementById('server-list');
      container.innerHTML = servers.map(server => \`
        <div class="server-card">
          <div class="server-info">
            <h3>\${server.name}</h3>
            <p>\${server.base_url}</p>
            <p style="font-size: 12px; color: #999;">Token 复活: \${server.enable_token_revive ? '✅ 已启用' : '❌ 已禁用'}</p>
          </div>
          <div class="server-actions">
            <button class="btn btn-primary" onclick="testServer('\${server.id}')">测试连接</button>
            <button class="btn btn-danger" onclick="deleteServer('\${server.id}')">删除</button>
          </div>
        </div>
      \`).join('');
    }

    // 更新服务器下拉框
    function updateServerSelects(servers) {
      const selects = ['account-server-select', 'operation-server-select'];
      selects.forEach(id => {
        const select = document.getElementById(id);
        select.innerHTML = '<option value="">请选择服务器</option>' +
          servers.map(s => \`<option value="\${s.id}">\${s.name}</option>\`).join('');
      });
    }

    // 切换标签
    function switchTab(tab) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(\`tab-\${tab}\`).classList.add('active');
    }

    // 显示添加服务器模态框
    function showAddServerModal() {
      document.getElementById('addServerModal').classList.add('active');
    }

    // 关闭模态框
    function closeModal(id) {
      document.getElementById(id).classList.remove('active');
    }

    // 添加服务器
    document.getElementById('addServerForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const serverData = {
        name: document.getElementById('server-name').value,
        base_url: document.getElementById('server-url').value,
        token: document.getElementById('server-token').value,
        enable_token_revive: document.getElementById('server-revive').checked
      };

      try {
        const res = await fetch('/api/servers', {
          method: 'POST',
          headers: {
            'Authorization': \`Bearer \${token}\`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(serverData)
        });

        const data = await res.json();
        if (data.success) {
          alert('服务器添加成功！');
          closeModal('addServerModal');
          loadServers();
          loadStats();
        } else {
          alert('添加失败：' + (data.error || '未知错误'));
        }
      } catch (error) {
        alert('添加失败：' + error.message);
      }
    });

    // 测试服务器
    async function testServer(id) {
      try {
        const res = await fetch(\`/api/servers/\${id}/test\`, {
          method: 'POST',
          headers: { 'Authorization': \`Bearer \${token}\` }
        });
        const data = await res.json();
        
        if (data.success) {
          alert(\`连接成功！\\n账号数量: \${data.accounts_count}\`);
        } else {
          alert(\`连接失败：\${data.error}\`);
        }
      } catch (error) {
        alert('测试失败：' + error.message);
      }
    }

    // 删除服务器
    async function deleteServer(id) {
      if (!confirm('确定要删除这个服务器吗？')) return;

      try {
        const res = await fetch(\`/api/servers/\${id}\`, {
          method: 'DELETE',
          headers: { 'Authorization': \`Bearer \${token}\` }
        });
        const data = await res.json();
        
        if (data.success) {
          alert('删除成功！');
          loadServers();
          loadStats();
        } else {
          alert('删除失败：' + (data.error || '未知错误'));
        }
      } catch (error) {
        alert('删除失败：' + error.message);
      }
    }

    // 加载账号列表
    async function loadAccounts() {
      const serverId = document.getElementById('account-server-select').value;
      if (!serverId) return;

      const container = document.getElementById('accounts-container');
      container.innerHTML = '<div class="loading">加载中...</div>';

      try {
        const res = await fetch(\`/api/accounts?server_id=\${serverId}\`, {
          headers: { 'Authorization': \`Bearer \${token}\` }
        });
        const data = await res.json();
        
        if (data.success) {
          container.innerHTML = \`
            <table class="account-table">
              <thead>
                <tr>
                  <th>邮箱</th>
                  <th>文件名</th>
                  <th>状态</th>
                  <th>最后刷新</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                \${data.accounts.map(acc => \`
                  <tr>
                    <td>\${acc.email || '-'}</td>
                    <td>\${acc.name}</td>
                    <td><span class="status-badge status-\${acc.status}">\${acc.status}</span></td>
                    <td>\${acc.last_refresh ? new Date(acc.last_refresh).toLocaleString() : '-'}</td>
                    <td>
                      <button class="btn btn-\${acc.disabled ? 'success' : 'danger'}" 
                              onclick="toggleAccount('\${serverId}', '\${acc.name}', \${acc.disabled})">
                        \${acc.disabled ? '启用' : '禁用'}
                      </button>
                    </td>
                  </tr>
                \`).join('')}
              </tbody>
            </table>
          \`;
        }
      } catch (error) {
        container.innerHTML = \`<div class="loading">加载失败：\${error.message}</div>\`;
      }
    }

    // 切换账号状态
    async function toggleAccount(serverId, filename, currentDisabled) {
      try {
        const res = await fetch(\`/api/accounts/\${filename}/status\`, {
          method: 'PATCH',
          headers: {
            'Authorization': \`Bearer \${token}\`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            server_id: serverId,
            disabled: !currentDisabled
          })
        });

        const data = await res.json();
        if (data.success) {
          loadAccounts();
        } else {
          alert('操作失败：' + (data.error || '未知错误'));
        }
      } catch (error) {
        alert('操作失败：' + error.message);
      }
    }

    // 检查使用情况
    async function checkUsage() {
      const serverId = document.getElementById('operation-server-select').value;
      if (!serverId) {
        alert('请先选择服务器');
        return;
      }

      const resultDiv = document.getElementById('operation-result');
      resultDiv.innerHTML = '<div class="loading">检查中...</div>';

      try {
        const res = await fetch('/api/operations/check-usage', {
          method: 'POST',
          headers: {
            'Authorization': \`Bearer \${token}\`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ server_id: serverId })
        });

        const data = await res.json();
        if (data.success) {
          resultDiv.innerHTML = \`
            <h3>检查结果</h3>
            <p>总计: \${data.summary.total} | 成功: \${data.summary.success} | 失败: \${data.summary.error} | 禁用: \${data.summary.disabled}</p>
          \`;
        }
      } catch (error) {
        resultDiv.innerHTML = \`<div class="loading">检查失败：\${error.message}</div>\`;
      }
    }

    // 下载打包
    async function downloadPack() {
      const serverId = document.getElementById('operation-server-select').value;
      if (!serverId) {
        alert('请先选择服务器');
        return;
      }

      try {
        const res = await fetch('/api/operations/download-pack', {
          method: 'POST',
          headers: {
            'Authorization': \`Bearer \${token}\`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ server_id: serverId })
        });

        const data = await res.json();
        if (data.success) {
          alert(\`打包成功！\\n文件数: \${data.count}\\n下载链接: \${data.download_url}\`);
        }
      } catch (error) {
        alert('打包失败：' + error.message);
      }
    }
  </script>
</body>
</html>
`;
