---
name: xiaohongshu-auto-publish
description: 小红书自动发布技能。自动获取最新内容（如AI论文）、格式化为小红书风格、并尝试自动发布。当用户想要自动发布内容到小红书、设置定时发布任务、或需要将论文改写为小红书风格时使用此技能。
---

# 小红书自动发布技能 (Xiaohongshu Auto Publish) 🚀

让 AI 助手自动获取内容并发布到小红书，支持定时发布！

## 功能特点

- 📚 自动获取最新内容（arXiv 论文等）
- ✨ **改写为小红书风格**（震惊体/揭秘体）
- 🤖 自动发布到小红书（使用 Playwright）
- 💾 本地备份（发布失败时保存内容）
- ⏰ 支持定时发布

---

# 📝 小红书内容格式规范

## 改写规则

### 1. 标题格式

使用「震惊体」或「揭秘体」：

```
震惊！AI竟然能XXX
揭秘：XX领域大突破
重磅！XX传来新消息
沸腾！XX实现重大突破
```

### 2. 开头格式

使用口语化称呼引入：

```
姐妹们！/ 宝子们！
科研人狂喜！
友友们！
```

### 3. 正文改写规则

| 原表述 | 改写为 |
|--------|--------|
| 本研究 / 本文提出 | 这篇论文发现 |
| 实验结果表明 | 实测数据表明 |
| 提出了 XX 方法 | 搞出了 XX 黑科技 |
| 取得了 SOTA | 刷新了世界纪录 |
| 显著提升 | 效果炸裂 |

### 4. 排版要求

- 加入表情符号：🚀 💡 🔥 ✨ ⭐ 📌 👇 🙋‍♀️
- 多换行，避免大段文字
- 每段控制在 2-3 行
- 使用「·」或「——」分隔重点

### 5. 强调影响

不要只说学术价值，要强调**对普通人/行业的影响**：

```
🔥 对普通人的影响：
   · XXX 人直接受益
   · 可以用来做 XX

💼 对行业的影响：
   · 将颠覆 XX 行业
   · 预计带来 XX 亿市场
```

### 6. 结尾互动引导

```
你觉得这个技术有用吗？
评论区聊聊~ 🙋‍♀️

点赞 + 关注，持续分享 AI 前沿！

#标签1 #标签2 #标签3
```

### 7. 推荐标签

```
#论文摘要 #AI前沿 #科研 #科技资讯
#人工智能 #机器学习 #深度学习 #ChatGPT
#大模型 #科技 #学术研究 #技术突破
```

---

# 📄 改写示例

## 输入（原始摘要）

```
本研究提出了一种基于 Transformer 架构的大语言模型，
通过预训练和微调的方式，在多个 NLP 任务上取得了 SOTA 效果。
实验结果表明，该方法相比基线模型有显著提升。
```

## 输出（小红书风格）

```
🔥 重磅！ChatGPT 背后技术大揭秘！

姐妹们！科研人狂喜！

今天刷到一篇超炸的论文，必须分享给你们！

这篇论文发现了一种新方法，可以让 AI 更懂人话！

🚀 核心技术：
· 基于 Transformer 架构
· 预训练 + 微调
· 刷新多项世界纪录

💡 对普通人的影响：
· 聊天更自然，AI 助手更好用
· 自动写文案、打总结，一键搞定

💼 对行业的影响：
· 客服、教育、医疗都要被颠覆
· 预计市场规模超百亿

实测数据表明，效果直接炸裂！

你觉得 AI 越来越聪明是好事吗？
评论区聊聊~ 🙋‍♀️

点赞 + 关注，持续分享 AI 前沿！

#论文摘要 #AI前沿 #ChatGPT #大模型 #深度学习 #人工智能 #技术突破
```

---

# 安装

## 1. 克隆仓库

```bash
git clone https://github.com/18565878989/openclaw-xiaohongshu-auto-publish.git
cd openclaw-xiaohongshu-auto-publish
```

## 2. 安装依赖

```bash
# 安装 Playwright
pip install playwright

# 安装浏览器
playwright install chromium
```

## 3. 配置 Cookie

编辑 `scripts/xhs_auto_publish.py`，替换 `XHS_COOKIE` 为您的小红书 Cookie。

## 使用方法

### 方式 1: 直接运行

```bash
python3 scripts/xhs_auto_publish.py
```

### 方式 2: OpenClaw 触发

```
发布今日AI论文到小红书
改写这篇论文为小红书风格：https://arxiv.org/abs/xxx
```

### 方式 3: 定时发布

在 OpenClaw 中设置 cron 任务：
- 时间: `0 8,18 * * *` (每天 8:00 和 18:00)
- 时区: Asia/Shanghai

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

1. **获取论文** - 从 arXiv RSS 获取最新论文
2. **智能改写** - 按上述规则转换为小红书风格
3. **浏览器发布** - Playwright 控制 Chromium 自动发布
4. **本地备份** - 保存内容到本地目录

## 配置选项

```python
# 小红书 Cookie
XHS_COOKIE = "your_cookie_here"

# 默认标签
DEFAULT_TAGS = [
    "论文摘要", "AI前沿", "科研", "科技资讯",
    "人工智能", "机器学习", "深度学习", "ChatGPT"
]
```

## 注意事项

| 问题 | 解决方案 |
|------|----------|
| Cookie 过期 | 重新获取并更新 |
| 发布失败 | 内容已保存到本地，可手动发布 |
| 被检测 | 可能需要更换 Cookie 或使用代理 |

## License

MIT License

## 作者

- GitHub: [18565878989](https://github.com/18565878989)
- OpenClaw Directory: [OpenClaw Directory](https://openclawdirectory.co.uk/)
