---
name: xiaohongshu-auto-publish
description: 小红书自动发布技能。自动获取最新内容（如AI论文）、格式化为小红书风格、生成配图、并尝试自动发布。当用户想要自动发布内容到小红书、设置定时发布任务、或需要将论文改写为小红书风格时使用此技能。
---

# 小红书自动发布技能 (Xiaohongshu Auto Publish) 🚀

让 AI 助手自动获取内容并发布到小红书，支持定时发布和配图生成！

## 功能特点

- ✍️ **智能改写** - 将论文改写为小红书风格（震惊体）
- 🎨 **配图生成** - 根据标题自动生成封面图
- 📝 **字数控制** - 控制在 800 字以内，符合图文模式
- 🤖 **自动发布** - 使用 Playwright 发布
- 💾 **本地备份** - 发布失败时保存内容
- ⏰ **定时发布** - 每天 8:30 和 18:30 自动发布
- 🛡️ **账号保护** - 间隔发布，防止风控

---

# 📝 小红书内容格式规范

## 字数限制

| 模式 | 字数限制 | 说明 |
|------|----------|------|
| 图文模式 | **800 字以内** | 推荐，便于阅读 |
| 长文模式 | 无限制 | 需要申请 |

⚠️ **重要**：正文控制在 **800 字以内**，避免发布失败！

## 改写规则

### 1. 标题格式（震惊体）

```
🔥 重磅！[关键词]传来新消息！
震惊！AI竟然能[动词]
揭秘：[领域]领域大突破！
沸腾！[技术]实现重大进展
```

### 2. 开头格式

```
姐妹们！/ 宝子们！/ 科研人狂喜！
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
- 多换行，每段 2-3 行
- 使用「·」分隔重点

### 5. 强调影响

```
💡 对普通人的影响：
   · XX 人直接受益
   · 可以用来做 XX

💼 对行业的影响：
   · 将颠覆 XX 行业
```

### 6. 结尾互动引导

```
你觉得这个技术牛不牛？
评论区聊聊~ 🙋‍♀️

点赞 + 关注，持续分享 AI 前沿！
```

### 7. 推荐标签

```
#论文摘要 #AI前沿 #科研 #科技资讯
#人工智能 #机器学习 #深度学习 #ChatGPT
```

---

# 🎨 配图生成规范

## 图片要求

| 参数 | 要求 |
|------|------|
| 尺寸 | 3:4（小红书黄金比例） |
| 分辨率 | 1080x1440 或更高 |
| 色调 | 明亮、清新、科技感 |
| 风格 | 简约现代，突出关键词 |

## 提示词模板

```
A clean, modern tech illustration for [论文标题关键词],
bright colors, gradient background, minimalist design,
text overlay-friendly, no people, 3:4 aspect ratio,
high quality, digital art style
```

## 生成示例

论文标题：「Transformers are Bayesian Networks」

生成提示词：
```
A clean, modern illustration for "Transformers and AI",
bright blue and purple gradient background,
neural network patterns, minimalist design,
text overlay-friendly, 3:4 aspect ratio
```

---

# 🛡️ 账号安全规范

## 发布频率控制

| 时间段 | 建议 | 说明 |
|--------|------|------|
| 1 小时内 | **不超过 1 篇** | 高频发布易被风控 |
| 每天 | **2-3 篇** | 最佳频率 |
| 每周 | **10-15 篇** | 保持活跃度 |

## publishInterval 配置

```python
# 发布间隔（秒）
publishInterval = 3600  # 至少间隔 1 小时
```

## 安全建议

1. **固定时间发布** - 早晚各一篇最安全
2. **间隔发布** - 不要连续发布多篇
3. **内容原创** - 避免搬运和重复
4. **正常互动** - 发布后适当互动

---

# 📄 改写示例

## 输入（原始摘要）

```
本研究提出了一种基于 Transformer 架构的大语言模型，
通过预训练和微调的方式，在多个 NLP 任务上取得了 SOTA 效果。
实验结果表明，该方法相比基线模型有显著提升。
```

## 输出（小红书风格，800字以内）

```
🔥 重磅！ChatGPT 背后技术大揭秘！

姐妹们！科研人狂喜！

今天刷到一篇超炸的论文，必须分享！

🚀 核心技术：
· 基于 Transformer 架构
· 预训练 + 微调
· 刷新多项世界纪录

💡 对普通人的影响：
· 聊天更自然，AI 助手更好用
· 自动写文案，一键搞定

💼 对行业的影响：
· 客服、教育将被颠覆
· 预计市场超百亿

实测数据表明，效果直接炸裂！

你怎么看？评论区聊聊~ 🙋‍♀️

#论文摘要 #AI前沿 #ChatGPT #大模型
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
pip install playwright
playwright install chromium
```

## 3. 配置

编辑脚本配置：
```python
XHS_COOKIE = "your_cookie_here"
publishInterval = 3600  # 间隔 1 小时
maxContentLength = 800   # 最大字数
```

## 使用方法

### 手动触发

```
发布今日AI论文到小红书
生成配图并发布
```

### OpenClaw Skill 调用

当需要生成配图时，使用 `ai-image-generator` 技能：
```
使用 ai-image-generator 生成封面图
主题：[论文标题]
比例：3:4
风格：明亮、科技感
```

---

# ⏰ 定时任务配置

## 推荐时间表

| 时间 | 任务 | 间隔 |
|------|------|------|
| 08:30 | 早间发布 | - |
| 18:30 | 晚间发布 | 10 小时 |

## cron 表达式

```
# 早间发布
30 8 * * *

# 晚间发布
30 18 * * *
```

---

# 文件结构

```
openclaw-xiaohongshu-auto-publish/
├── SKILL.md                      # 本文件
└── scripts/
    └── xhs_auto_publish.py       # 主发布脚本

# 运行时生成
~/.openclaw/workspace/xhs_content/   # 发布内容备份
~/.openclaw/workspace/xhs_images/    # 生成配图
```

---

# ⚙️ 配置选项

```python
# === 小红书配置 ===
XHS_COOKIE = "your_cookie_here"

# === 发布频率控制 ===
publishInterval = 3600      # 每次发布间隔（秒）
maxPerDay = 3               # 每天最多发布数

# === 内容配置 ===
maxContentLength = 800      # 正文最大字数
imageRatio = "3:4"          # 图片比例
defaultCategory = "知识"     # 默认分类

# === 标签配置 ===
DEFAULT_TAGS = [
    "论文摘要", "AI前沿", "科研", "科技资讯",
    "人工智能", "机器学习", "深度学习", "ChatGPT"
]
```

---

# 常见问题

| 问题 | 解决方案 |
|------|----------|
| 内容超长 | 启用自动截断，保持 800 字以内 |
| Cookie 过期 | 重新获取并更新 |
| 发布失败 | 内容已保存，可手动发布 |
| 被风控 | 降低发布频率，每天不超过 3 篇 |
| 图片生成失败 | 使用默认封面图 |

## 注意事项

1. **字数控制** - 始终保持在 800 字以内
2. **间隔发布** - 每次发布间隔至少 1 小时
3. **内容质量** - 保持原创，避免重复
4. **账号维护** - 定期互动，保持活跃

---

# License

MIT License

## 作者

- GitHub: [18565878989](https://github.com/18565878989)
- OpenClaw Directory: [OpenClaw Directory](https://openclawdirectory.co.uk/)
