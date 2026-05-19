# Web 技术基础速览

## HTTP 协议

HTTP（HyperText Transfer Protocol）是 Web 通信的应用层协议，建立在 TCP/IP 之上。
最常用版本是 HTTP/1.1 和 HTTP/2。

HTTP 是**无状态的请求-响应协议**：
- 客户端（浏览器）发出 Request
- 服务器返回 Response
- 每次请求之间默认不保留状态

要在多次请求间保留状态，需要 Cookie / Session / Token 等机制。

## HTTP 方法

| 方法 | 用途 | 幂等性 |
|---|---|---|
| GET | 获取资源 | ✓ |
| POST | 创建资源 / 提交数据 | ✗ |
| PUT | 完整更新资源 | ✓ |
| PATCH | 部分更新资源 | ✗ |
| DELETE | 删除资源 | ✓ |

## REST 风格

REST（Representational State Transfer）是一种 API 设计风格：
- URL 表示**资源**（名词），如 `/users/123`
- HTTP 方法表示**动作**（动词），如 GET /users/123 = "查看用户 123"
- 状态用 HTTP status code 表达：200 成功、404 找不到、500 服务器错

## Cookie vs Session

- **Cookie**：存在浏览器端的小文本片段，每次请求自动带上
- **Session**：存在服务器端的状态，通过一个 session ID（写在 cookie 里）关联

现代 Web 应用越来越多用 **JWT（JSON Web Token）** 替代传统 session——把状态编码到 token 里，
服务器不需要保留 session 表，方便水平扩展。
