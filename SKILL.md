---
name: xiaohongshu-auto-publish
description: 小红书自动发布技能。自动获取最新内容（如AI论文）、格式化为小红书风格、并尝试自动发布。当用户想要自动发布内容到小红书、设置定时发布任务、或需要小红书内容格式化时使用此技能。
---

# 小红书自动发布技能 (Xiaohongshu Auto Publish) 🚀

让 AI 助手自动获取内容并发布到小红书，支持定时发布！

## 功能特点

- 📚 自动获取最新内容（arXiv 论文等）
- ✨ 格式化为小红书风格（震惊体/揭秘体）
- 🤖 自动发布到小红书（使用 Playwright）
- 💾 本地备份（发布失败时保存内容）
- ⏰ 支持定时发布

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/18565878989/openclaw-xiaohongshu-auto-publish.git
cd openclaw-xiaohongshu-auto-publish
```

### 2. 安装依赖

```bash
# 安装 Playwright
pip install playwright

# 安装浏览器
playwright install chromium
```

### 3. 配置 Cookie

编辑 `scripts/xhs_auto_publish.py`，替换 `XHS_COOKIE` 为您的小红书 Cookie：

1. 登录小红书网页版 https://creator.xiaohongshu.com
2. 打开开发者工具 (F12) > Application > Cookies
3. 复制所有 Cookie 字符串
4. 替换脚本中的 `XHS_COOKIE` 变量

## 使用方法

### 方式 1: 直接运行

```bash
python3 scripts/xhs_auto_publish.py
```

### 方式 2: OpenClaw 触发

在 OpenClaw 中说：
```
发布今日AI论文到小红书
```

### 方式 3: 定时发布

在 OpenClaw 中设置 cron 任务：
- 时间: `0 8,18 * * *` (每天 8:00 和 18:00)
- 时区: Asia/Shanghai
- 脚本: `python3 scripts/xhs_auto_publish.py`

## 内容格式

发布内容自动格式化为小红书风格：

```
🤖 AI论文速递 | 03月19日

✨ 今日精选 6 篇顶会论文
📚 来源: arXiv.org

━━━━━

1. Transformers are Bayesian Networks
   👤 Gregory Coppola
   🤖 AI
   🔗 https://arxiv.org/abs/...

...

━━━━━

#AI论文 #机器学习 #人工智能 #深度学习 
#NLP #计算机视觉 #学术研究 #论文推荐

━━━━━
📌 论文链接已整理
💡 关注我，每天分享AI前沿论文！
```

## 文件结构

```
openclaw-xiaohongshu-auto-publish/
├── SKILL.md                      # 本文件
└── scripts/
    └── xhs_auto_publish.py       # 主发布脚本

# 运行时生成
~/.openclaw/workspace/xhs_content/   # 发布内容备份
```

## 工作原理

1. **启动浏览器** - Playwright 控制 Chromium
2. **模拟登录** - 使用 Cookie 设置登录状态
3. **打开创作页** - 访问小红书创作平台
4. **填写内容** - 自动填充正文和标签
5. **点击发布** - 提交笔记
6. **备份内容** - 保存到本地目录

## 配置选项

编辑脚本中的配置：

```python
# 小红书 Cookie
XHS_COOKIE = "your_cookie_here"

# 默认标签
DEFAULT_TAGS = [
    "AI论文", "机器学习", "人工智能", "深度学习",
    "NLP", "计算机视觉", "学术研究", "论文推荐"
]

# 默认分类
DEFAULT_CATEGORY = "知识"
```

## 注意事项

| 问题 | 解决方案 |
|------|----------|
| Cookie 过期 | 重新获取并更新 |
| 发布失败 | 内容已保存到本地，可手动发布 |
| 被检测 | 可能需要更换 Cookie 或使用代理 |

## 常见问题

### Q: Cookie 怎么获取？
A: 登录小红书网页版，打开开发者工具，在 Application > Cookies 中复制。

### Q: 发布失败怎么办？
A: 检查 `~/.openclaw/workspace/xhs_content/` 目录，复制内容手动发布。

### Q: 支持图片吗？
A: 当前版本仅支持文字，图片功能待开发。

## License

MIT License

## 作者

- GitHub: [18565878989](https://github.com/18565878989)
- OpenClaw Directory: [OpenClaw Directory](https://openclawdirectory.co.uk/)

## 相关项目

| 项目 | 说明 |
|------|------|
| [openclaw-daily-tech-papers](https://github.com/18565878989/openclaw-daily-tech-papers) | 每日技术论文推送 |
| [OpenClaw](https://openclaw.ai/) | AI 个人助手框架 |
| [CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 让任何软件都能被 AI 控制 |
