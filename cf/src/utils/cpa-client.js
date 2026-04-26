/**
 * CPA 客户端工具类
 */

export class CPAClient {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.token = token;
  }

  /**
   * 获取认证文件列表
   */
  async getAuthFiles() {
    const response = await fetch(`${this.baseUrl}/v0/management/auth-files`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to get auth files: ${response.status}`);
    }

    const data = await response.json();
    return data.files || [];
  }

  /**
   * 下载认证文件
   */
  async downloadAuthFile(filename) {
    const response = await fetch(
      `${this.baseUrl}/v0/management/auth-files/download?name=${encodeURIComponent(filename)}`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to download auth file: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * 上传认证文件
   */
  async uploadAuthFile(authData, filename) {
    const formData = new FormData();
    const blob = new Blob([JSON.stringify(authData)], { type: 'application/json' });
    formData.append('file', blob, filename);

    const response = await fetch(`${this.baseUrl}/v0/management/auth-files`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Failed to upload auth file: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * 删除认证文件
   */
  async deleteAuthFile(filename) {
    const response = await fetch(
      `${this.baseUrl}/v0/management/auth-files?name=${encodeURIComponent(filename)}`,
      {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to delete auth file: ${response.status}`);
    }

    return true;
  }

  /**
   * 禁用认证文件
   */
  async disableAuthFile(filename) {
    const response = await fetch(`${this.baseUrl}/v0/management/auth-files/status`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: filename,
        disabled: true
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to disable auth file: ${response.status}`);
    }

    return true;
  }

  /**
   * 启用认证文件
   */
  async enableAuthFile(filename) {
    const response = await fetch(`${this.baseUrl}/v0/management/auth-files/status`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: filename,
        disabled: false
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to enable auth file: ${response.status}`);
    }

    return true;
  }

  /**
   * 检查账号使用情况
   */
  async checkUsage(authIndex, email) {
    const response = await fetch(`${this.baseUrl}/v0/management/api-call`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        authIndex: authIndex,
        method: 'GET',
        url: 'https://chatgpt.com/backend-api/wham/usage',
        header: {
          'Authorization': 'Bearer $TOKEN$',
          'Content-Type': 'application/json',
          'User-Agent': 'codex_cli_rs/0.76.0'
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to check usage: ${response.status}`);
    }

    return await response.json();
  }
}
