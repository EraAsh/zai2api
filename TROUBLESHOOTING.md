# ZaiBridge 故障排查指南

## 常见问题

### 1. OAuth 登录失败

#### 症状
- Token 刷新失败，显示 "无法获取授权 URL"
- 容器日志中只有 `[*] 开始后端 OAuth 登录流程...` 但没有后续输出

#### 诊断步骤

1. **查看容器日志**
```bash
docker-compose logs -f zaibridge
```

2. **查找调试信息**
日志中应该包含以下详细信息：
```
[*] 开始后端 OAuth 登录流程...
[*] Discord Token: MTQ0OTQ0NzYwMTkwNzgz...vhPBu2GvN8
[1/5] 获取 Discord 授权 URL...
    [*] 请求 OAuth 登录 URL: https://zai.is/oauth/discord/login
    [*] 响应状态码: 301
    [*] 最终 URL: https://zai.is/oauth/discord/login
    [*] 收到重定向 Location: /oauth/discord/authorize
    [*] Location 不是 Discord URL，尝试跟随重定向...
    [*] 第二次请求最终 URL: https://discord.com/oauth2/authorize?...
    [+] 第二次请求成功重定向到 Discord
    Client ID: xxx
    Redirect URI: xxx
    Scope: xxx
```

3. **常见原因**

**原因 1：网络连接问题**
- 检查容器是否能访问外网
- 检查是否需要配置代理

**解决方案**：
```bash
# 在 docker-compose.yml 中配置代理
environment:
  - PROXY_ENABLED=true
  - PROXY_URL=http://your-proxy:port
```

**原因 2：Discord Token 无效**
- Token 可能已过期
- Token 格式不正确

**解决方案**：
- 重新获取 Discord Token
- 确保复制完整的 Token

**原因 3：zai.is 服务变更**
- zai.is 可能更改了 OAuth 流程
- 需要更新代码

**解决方案**：
- 查看最新的 GitHub 仓库
- 拉取最新代码：`git pull origin main`
- 重新构建容器：`docker-compose up -d --build`

### 2. 健康检查失败

#### 症状
- 容器日志显示：`"GET /health HTTP/1.1" 404 207`
- Docker 健康检查失败

#### 解决方案
- 确保使用最新版本的代码（已包含 `/health` 端点）
- 重新构建容器：
```bash
docker-compose down
docker-compose up -d --build
```

### 3. Token 刷新失败

#### 症状
- Token 刷新失败，显示各种错误信息

#### 诊断步骤

1. **手动测试 Token**
```bash
# 进入容器
docker-compose exec zaibridge bash

# 测试 OAuth 登录
python zai_token.py backend-login --discord-token "你的discord_token"
```

2. **查看详细错误**
- 检查容器日志中的完整错误信息
- 查看是否有网络超时、连接拒绝等错误

3. **检查数据库**
```bash
# 进入容器
docker-compose exec zaibridge bash

# 查看数据库
sqlite3 instance/zai2api.db
.tables
SELECT * FROM token;
```

### 4. API 调用失败

#### 症状
- API 调用返回 401 或 403 错误
- 无法调用 zai.is 的模型

#### 诊断步骤

1. **检查 API Key**
```bash
# 在管理面板中查看 API Key
# 确保客户端使用正确的 API Key
```

2. **检查 Token 状态**
- 在管理面板中查看 Token 是否活跃
- 检查 Token 是否有 zai_token 和 zai_darkknight

3. **查看请求日志**
- 在管理面板的"请求日志"中查看详细的调用记录
- 检查状态码和错误信息

### 5. 数据库问题

#### 症状
- 无法保存 Token
- 数据库初始化失败

#### 解决方案

1. **检查数据库文件权限**
```bash
# 检查 instance 目录权限
ls -la instance/

# 如果权限不正确，修复权限
chmod 755 instance
chmod 644 instance/zai2api.db
```

2. **重新初始化数据库**
```bash
# 停止容器
docker-compose down

# 删除数据库文件
rm -f instance/zai2api.db

# 重新启动
docker-compose up -d
```

## 调试技巧

### 1. 启用调试模式

在管理面板的"系统配置"中启用调试模式，可以看到更详细的日志。

### 2. 手动测试 OAuth 登录

```bash
# 进入容器
docker-compose exec zaibridge bash

# 测试后端登录
python zai_token.py backend-login --discord-token "你的discord_token"

# 测试浏览器登录
python zai_token.py backend-login --discord-token "你的discord_token" --url https://zai.is
```

### 3. 查看实时日志

```bash
# 查看所有日志
docker-compose logs -f

# 只查看 zaibridge 服务
docker-compose logs -f zaibridge

# 查看最近 100 行日志
docker-compose logs --tail=100 zaibridge
```

### 4. 检查网络连接

```bash
# 进入容器
docker-compose exec zaibridge bash

# 测试网络连接
curl -I https://zai.is
curl -I https://discord.com

# 测试 DNS 解析
nslookup zai.is
nslookup discord.com
```

## 获取帮助

如果以上方法都无法解决问题，请：

1. **收集诊断信息**
```bash
# 收集日志
docker-compose logs > zaibridge-logs.txt

# 收集配置
docker-compose config > docker-compose-config.txt

# 收集数据库结构
docker-compose exec zaibridge sqlite3 instance/zai2api.db .schema > db-schema.txt
```

2. **在 GitHub 提交 Issue**
- 仓库地址：https://github.com/EraAsh/ZaiBridge
- 包含完整的错误日志
- 描述复现步骤
- 提供环境信息（操作系统、Docker 版本等）

3. **查看文档**
- README.md：项目说明和快速开始
- DEPLOY.md：部署指南
- CHANGELOG.md：版本更新记录

## 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 重新构建
docker-compose up -d --build

# 进入容器
docker-compose exec zaibridge bash

# 查看容器状态
docker-compose ps

# 查看资源使用
docker stats
```

## 性能优化

### 1. 调整 Gunicorn 配置

在 `docker-compose.yml` 中调整 worker 数量：
```yaml
command: ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", ...]
```

### 2. 调整 Token 刷新间隔

在管理面板的"系统配置"中调整 Token 刷新间隔，避免过于频繁的刷新。

### 3. 启用缓存

在管理面板中启用缓存，减少对 zai.is 的直接调用。

## 安全建议

1. **修改默认密码**
   - 首次登录后立即修改管理员密码
   - 使用强密码

2. **配置 HTTPS**
   - 生产环境建议使用 HTTPS
   - 使用反向代理（如 Nginx）

3. **定期备份数据库**
   ```bash
   # 备份数据库
   docker-compose exec zaibridge sqlite3 instance/zai2api.db .dump > backup.sql
   
   # 恢复数据库
   docker-compose exec -T zaibridge sqlite3 instance/zai2api.db < backup.sql
   ```

4. **限制访问**
   - 使用防火墙限制访问
   - 配置 API Key 认证
   - 定期审查 Token 列表