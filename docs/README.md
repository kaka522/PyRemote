# PyRemote - 轻量级跨平台远程控制工具

 

PyRemote 是一个基于 Python 开发的开源远程控制工具，旨在提供 **轻量、安全、易用** 的跨平台远程控制体验。支持 Windows、macOS、Linux 系统，可通过桌面GUI、Web界面或简化的长辈模式进行远程操作。


## 核心特性
- **跨平台兼容**：完美支持 Windows/macOS/Linux，最小安装包仅 3.2MB
- **零配置连接**：内置 P2P 穿透（STUN 协议），无需手动设置端口映射
- **银行级安全**：采用 RSA 非对称加密 + 数据校验，防止拦截与篡改
- **多模式控制**：
  - 桌面GUI：适合常规用户
  - Web界面：支持移动端临时控制
  - 长辈模式：简化界面 + 语音提示，适合非技术用户
- **核心功能**：屏幕捕获、鼠标控制、键盘输入、文件传输（规划中）


## 快速开始
### 1. 安装方式
#### 方式1：通过 pip 安装（推荐）
```bash
pip install pyremote
```

#### 方式 2：源码安装

```bash
# 克隆仓库
git clone git@github.com:kaka522/PyRemote.git
cd PyRemote

# 安装依赖
pip install -r requirements.txt

# 安装项目
pip install -e .
```

### 2. 运行 PyRemote

#### 启动服务端（被控制端）

```bash
# 桌面GUI模式（默认）
pyremote --mode gui --host 0.0.0.0 --port 9999

# 或 Web 模式（支持移动端访问）
pyremote --mode web --host 0.0.0.0 --port 9999
```



#### 启动客户端（控制端）

```bash
# 桌面GUI模式，连接远程服务端
pyremote --mode gui --client 192.168.1.100:9999

# 或 长辈模式（简化界面+语音）
pyremote --mode elderly --client 192.168.1.100:9999
```



#### Web 模式访问

启动 Web 模式后，在浏览器中访问：



```plaintext
http://服务端IP:9999
```

## 功能详解

### 1. 长辈模式

专为非技术用户设计：



- 放大按钮（14 号字体），避免误触
- 语音提示（操作反馈、连接状态）
- 简化控制：仅保留核心功能（鼠标移动、点击、常用按键）

### 2. P2P 穿透

当控制端与服务端处于不同局域网时（如家里和公司），PyRemote 会自动通过 STUN 协议获取公网 IP / 端口，无需手动配置路由器端口映射。



**注意**：对称 NAT 类型暂不支持 P2P 穿透，此时需使用中继服务（规划中）。

### 3. 安全机制

- **双向认证**：客户端与服务端交换 RSA 公钥，确保身份合法
- **数据加密**：所有传输数据采用 RSA 非对称加密
- **防篡改**：每个数据包包含 SHA-256 校验和
- **防重放**：时间戳有效期 30 秒，拒绝过期数据包

## 开发指南

### 项目结构

```plaintext
PyRemote/
├── pyremote/          # 核心代码
│   ├── core/          # 核心模块（通信、加密、屏幕捕获、输入控制）
│   ├── ui/            # 界面模块（CLI、GUI、Web）
│   ├── platform/      # 平台适配（Windows/macOS/Linux）
│   ├── utils/         # 工具类（P2P、配置、日志）
│   └── 长辈模式/      # 长辈模式模块
├── tests/             # 单元测试
├── docs/              # 文档
└── setup.py           # 打包配置
```

### 贡献代码

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/xxx`）
3. 提交代码（`git commit -m "add feature xxx"`）
4. 推送分支（`git push origin feature/xxx`）
5. 发起 Pull Request

## 许可证

本项目采用 **MIT 许可证**，详见 [LICENSE](https://www.doubao.com/chat/LICENSE) 文件。