# DarkKnight Token 生成器设置指南

## 概述

ZaiBridge 现在集成了基于 Playwright 的浏览器自动化功能，可以自动生成有效的 `x-zai-darkknight` token，从而解决 503 错误问题。

## 工作原理

1. **浏览器自动化**：使用 Playwright 启动真实的 Chromium 浏览器
2. **注入脚本**：将 zai.is 的 `BLRNmSar.js` 脚本注入到浏览器中
3. **生成指纹**：脚本自动生成 Canvas 和 WebGL 指纹
4. **签名验证**：使用 ECDSA P-256 算法签名请求
5. **获取 Token**：从浏览器中提取有效的 DarkKnight token

## 部署步骤

### 1. 更新代码

确保你已经拉取了最新的代码：

```bash
git pull origin main
```

### 2. 重新构建 Docker 镜像

由于添加了新的依赖和系统库，需要重新构建镜像：

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**注意**：构建过程可能需要 5-10 分钟，因为需要下载 Chromium 浏览器（约 300MB）。

### 3. 验证安装

查看容器日志，确认 Playwright 浏览器已正确安装：

```bash
docker-compose logs -f zaibridge
```

你应该看到类似以下的日志：

```
[信息] 浏览器启动成功
[信息] 访问 zai.is 首页...
[信息] 等待 DarkKnight 对象初始化...
[信息] 获取 DarkKnight token...
[信息] 成功获取 DarkKnight token: eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 配置选项

### 资源限制

由于 Playwright 浏览器需要较多资源，`docker-compose.yml` 中的资源限制已更新：

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # 最大 4 个 CPU 核心
      memory: 2G       # 最大 2GB 内存
    reservations:
      cpus: '1.0'      # 保留 1 个 CPU 核心
      memory: 512M     # 保留 512MB 内存
```

如果你的服务器资源有限，可以适当调整这些值。

### 无头模式

默认情况下，浏览器以无头模式运行（不显示 GUI）。如果需要调试，可以修改 `darkknight_generator.py` 中的 `headless` 参数：

```python
# 在 darkknight_generator.py 中
darkknight_token = generate_darkknight_sync(headless=False, max_retries=2)
```

## 使用方法

### 自动生成（推荐）

当添加 Discord Token 时，系统会自动：

1. 启动 Playwright 浏览器
2. 访问 zai.is 网站
3. 生成 DarkKnight token
4. 将 token 添加到请求头中
5. 完成 OAuth 登录

整个过程完全自动化，无需手动干预。

### 手动测试

如果你想手动测试 DarkKnight 生成器：

```bash
# 进入容器
docker-compose exec zaibridge bash

# 运行测试脚本
python darkknight_generator.py
```

如果成功，你会看到：

```
开始生成 DarkKnight token...
[信息] 浏览器启动成功
[信息] 访问 zai.is 首页...
[信息] 等待 DarkKnight 对象初始化...
[信息] 获取 DarkKnight token...
[信息] 成功获取 DarkKnight token: eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...

成功获取 DarkKnight token:
eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 故障排除

### 问题 1：构建失败 - 内存不足

**错误信息**：
```
ERROR: failed to solve: process "/bin/sh -c playwright install chromium" did not complete successfully: exit code: 137
```

**解决方案**：
- 增加 Docker 的内存限制（至少 4GB）
- 或者使用预构建的镜像

### 问题 2：运行时错误 - 浏览器启动失败

**错误信息**：
```
[错误] 启动浏览器失败: Executable doesn't exist at /root/.cache/ms-playwright/chromium-...
```

**解决方案**：
```bash
# 进入容器
docker-compose exec zaibridge bash

# 手动安装浏览器
playwright install chromium
```

### 问题 3：503 错误仍然存在

**可能原因**：
1. DarkKnight token 生成失败
2. Token 已过期
3. 网络连接问题

**解决方案**：
1. 查看容器日志，确认 DarkKnight token 是否成功生成
2. 尝试手动刷新 Token
3. 检查服务器网络连接

### 问题 4：性能问题

**症状**：
- Token 刷新速度慢
- 容器 CPU 使用率高

**解决方案**：
1. 减少 Token 刷新频率（在管理面板中调整）
2. 增加 CPU 资源限制
3. 使用缓存机制

## 性能优化

### 1. Token 缓存

DarkKnight token 有一定的有效期（通常 1 小时），可以缓存使用：

```python
# 在 app.py 中
DARKKNIGHT_CACHE = {
    'token': None,
    'expiry': 0
}

def get_cached_darkknight():
    if time.time() < DARKKNIGHT_CACHE['expiry']:
        return DARKKNIGHT_CACHE['token']
    
    # 生成新 token
    token = generate_darkknight_sync()
    DARKKNIGHT_CACHE['token'] = token
    DARKKNIGHT_CACHE['expiry'] = time.time() + 3600  # 1 小时后过期
    return token
```

### 2. 异步生成

使用后台任务异步生成 token，避免阻塞主流程：

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def refresh_darkknight():
    """后台任务：定期刷新 DarkKnight token"""
    token = generate_darkknight_sync()
    # 保存到数据库或缓存

# 每 50 分钟刷新一次
scheduler.add_job(refresh_darkknight, 'interval', minutes=50)
scheduler.start()
```

## 安全建议

1. **限制访问**：确保管理面板只能通过 VPN 或 IP 白名单访问
2. **定期更新**：及时更新 Playwright 和依赖库
3. **监控日志**：定期检查容器日志，发现异常及时处理
4. **资源监控**：监控 CPU 和内存使用情况，避免资源耗尽

## 常见问题

### Q: 为什么需要浏览器自动化？

A: zai.is 使用了复杂的浏览器指纹检测（Canvas、WebGL 等），普通的 HTTP 请求无法通过验证。使用真实的浏览器可以生成有效的指纹和签名。

### Q: 会增加多少资源消耗？

A: 
- 内存：约 300-500MB（Chromium 浏览器）
- CPU：生成 token 时约 10-30 秒的高 CPU 使用
- 磁盘：约 300MB（浏览器文件）

### Q: 可以禁用这个功能吗？

A: 可以，但可能会导致 503 错误。如果禁用，需要手动输入 darkknight 值。

### Q: Token 的有效期是多久？

A: 通常为 1 小时，但 zai.is 可能会随时调整。建议设置自动刷新机制。

## 更新日志

### v2.2 - 2026-01-03
- ✅ 集成 Playwright 浏览器自动化
- ✅ 自动生成 DarkKnight token
- ✅ 解决 503 错误问题
- ✅ 更新 Docker 资源限制
- ✅ 添加详细的日志记录

## 技术支持

如果遇到问题，请：

1. 查看容器日志：`docker-compose logs -f zaibridge`
2. 检查系统资源：`docker stats`
3. 提交 Issue：https://github.com/EraAsh/ZaiBridge/issues

## 免责声明

本功能仅供学习和研究使用。使用者应自行承担使用本工具产生的所有风险和责任。请遵守相关服务条款。