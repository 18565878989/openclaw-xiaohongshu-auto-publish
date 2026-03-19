---
name: xiaohongshu-auto-publish
description: 小红书自动发布技能。自动获取最新内容（如AI论文）、格式化为小红书风格、并尝试自动发布。当用户想要自动发布内容到小红书、设置定时发布任务、或需要小红书内容格式化时使用此技能。
---

# 小红书自动发布技能 (Xiaohongshu Auto Publish)

让 AI 助手自动获取内容并发布到小红书，支持定时发布！

## 功能特点

- 📚 自动获取最新内容（arXiv 论文等）
- ✨ 格式化为小红书风格（震惊体/揭秘体）
- 🤖 自动发布到小红书（使用 Playwright）
- 💾 本地备份（发布失败时保存内容）
- ⏰ 支持定时发布

## 安装

### 1. 安装依赖

```bash
# 安装 Playwright
pip install playwright
playwright install chromium
```

### 2. 复制脚本到 scripts 目录

```bash
mkdir -p ~/.openclaw/workspace/scripts
# 脚本内容见下方
```

### 3. 配置 Cookie

在脚本中替换 `XHS_COOKIE` 为您的小红书 Cookie：
1. 登录小红书网页版 (creator.xiaohongshu.com)
2. 打开开发者工具 > Application > Cookies
3. 复制所有 Cookie 字符串

## 使用方法

### 手动触发发布

```
发布今日AI论文到小红书
```

### 定时发布设置

在 OpenClaw 中设置 cron 任务：

```json
{
  "schedule": "0 8,18 * * *",
  "timezone": "Asia/Shanghai",
  "task": "运行 xhs_auto_publish.py"
}
```

## 脚本说明

### xhs_auto_publish.py

主脚本，自动完成以下步骤：

1. **获取内容** - 从 arXiv 获取最新论文
2. **格式化** - 转换为小红书风格
3. **发布** - 使用 Playwright 自动发布
4. **备份** - 保存内容到本地目录

### 内容格式化规则

```
标题：🤖 AI论文速递 | XX月XX日

开头：姐妹们/宝子们 引入
正文：
- 使用表情符号 🚀💡🔥
- 短句分行，避免大段文字
- 强调实际影响

结尾：互动引导 + 标签
```

### 默认配置

```python
TAGS = ["AI论文", "机器学习", "人工智能", "深度学习", 
        "NLP", "计算机视觉", "学术研究", "论文推荐"]

CATEGORY = "知识"
```

## 文件结构

```
~/.openclaw/workspace/
├── scripts/
│   └── xhs_auto_publish.py    # 主发布脚本
└── xhs_content/               # 发布内容备份
    └── content_YYYYMMDD_HHMMSS.txt
```

## 发布流程

1. 启动 Chromium 浏览器（无头模式）
2. 设置 Cookie 模拟登录
3. 打开创作页面
4. 填写正文内容
5. 添加标签
6. 点击发布

## 注意事项

1. **Cookie 有效期** - Cookie 可能随时过期，需要定期更新
2. **反爬虫检测** - 小红书可能会检测自动化操作
3. **备份机制** - 即使发布失败，内容也会保存到本地

## 常见问题

### Q: Cookie 过期了怎么办？
A: 重新登录小红书网页版，获取新的 Cookie 并更新脚本。

### Q: 发布失败怎么办？
A: 检查 `~/.openclaw/workspace/xhs_content/` 目录，手动复制内容发布。

### Q: 如何添加图片？
A: 目前版本仅支持文字发布，需要可扩展图片功能。

## 相关脚本

| 脚本 | 说明 |
|------|------|
| `xhs_auto_publish.py` | 自动获取+发布 |
| `xhs_publish.py` | 仅发布（需手动提供内容） |
| `daily_tech_papers_xhs.py` | 仅生成小红书格式内容 |

## License

MIT License

## 作者

- GitHub: [18565878989](https://github.com/18565878989)
- OpenClaw Directory: [OpenClaw Directory](https://openclawdirectory.co.uk/)

## 相关项目

- [openclaw-daily-tech-papers](https://github.com/18565878989/openclaw-daily-tech-papers) - 每日技术论文推送
- [OpenClaw](https://openclaw.ai/) - AI 个人助手框架
