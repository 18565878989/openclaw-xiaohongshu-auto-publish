#!/usr/bin/env python3
"""
小红书 AI 论文自动发布脚本 v4
支持：小红书风格改写 + 字数控制 + 配图生成 + 发布频率保护
"""

import asyncio
import sys
import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re
import time
import random
import hashlib

# ============ 配置 ============
XHS_COOKIE = """abRequestId=32882dce-eea4-5adc-94f4-1a5ef638b832; webBuild=6.1.0; xsecappid=xhs-pc-web; a1=19d04d371a9mdz5y8fdub5kq79rj2ik6p4rvgjb3m30000235958; webId=04bc6d18b45ea41a0c0f1dca66931e15; acw_tc=0a50885617739024597153633e2e5fe0053f22c63e6d5f01bb4a7709b32325; websectiga=984412fef754c018e472127b8effd174be8a5d51061c991aadd200c69a2801d6; sec_poison_id=8bcb6a34-f419-46e8-96e8-319e56c59b2c; gid=yjf84fqY8JU0yjf84fqWy4VD0j6fu2vYif7DFq62TAWjFhq8VJ3TKk888Jq2j2Y8qJ8ddWif; web_session=04006951ed7f0c302ca2f3d28e3b4b688a580a; id_token=VjEAAGJse5ch5LkIk4Sx6on2Pp5wAthCWRws+G0dsCMgXGfjfc0ulIwm206PtDaDxAa7avryO43Osy+yPn2Tt/cViYX1sse9jVF3IZpq4wqJqK3y0gB28eYDzSnL+6EJZz/gIU44; unread={%22ub%22:%2269b8faa5000000001a02f70e%22%2C%22ue%22:%2269b95d8a000000001b0235e7%22%2C%22uc%22:4}; loadts=1773902534867"""

# 发布频率控制
publishInterval = 3600      # 每次发布间隔（秒）- 至少1小时
maxPerDay = 3              # 每天最多发布数

# 内容配置
maxContentLength = 800     # 正文最大字数（小红书图文模式建议800字以内）
imageRatio = "3:4"        # 图片比例
defaultCategory = "知识"   # 默认分类

# 标签配置
DEFAULT_TAGS = [
    "论文摘要", "AI前沿", "科研", "科技资讯",
    "人工智能", "机器学习", "深度学习", "ChatGPT"
]

# 震惊体标题模板
TITLE_TEMPLATES = [
    "🔥 重磅！{}传来新消息！",
    "震惊！AI竟然能{}",
    "揭秘：{}领域大突破！",
    "沸腾！{}实现重大进展",
    "炸裂！{}刷新技术边界",
    "突发！{}引爆科技圈",
    "重磅！{}震撼发布",
]

# 状态文件
STATE_FILE = "/Users/wangfeng/.openclaw/workspace/xhs_content/publish_state.json"
CONTENT_DIR = "/Users/wangfeng/.openclaw/workspace/xhs_content"
IMAGES_DIR = "/Users/wangfeng/.openclaw/workspace/xhs_images"


# ============ 状态管理 ============

def load_state():
    """加载发布状态"""
    os.makedirs(CONTENT_DIR, exist_ok=True)
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'lastPublishTime': None,
        'todayCount': 0,
        'lastPublishDate': None
    }


def save_state(state):
    """保存发布状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def can_publish():
    """检查是否可以发布（频率控制）"""
    state = load_state()
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    
    # 检查今天发布数量
    if state.get('lastPublishDate') == today:
        if state.get('todayCount', 0) >= maxPerDay:
            print(f"⚠️ 今天已发布 {state['todayCount']} 篇，达到上限 {maxPerDay} 篇")
            return False, "今日发布已达上限"
    
    # 检查发布间隔
    if state.get('lastPublishTime'):
        last_time = datetime.fromisoformat(state['lastPublishTime'])
        elapsed = (now - last_time).total_seconds()
        if elapsed < publishInterval:
            remaining = int(publishInterval - elapsed)
            print(f"⚠️ 距离上次发布还有 {remaining} 秒")
            return False, f"需间隔 {publishInterval//60} 分钟"
    
    return True, "可以发布"


def record_publish():
    """记录发布"""
    state = load_state()
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    
    if state.get('lastPublishDate') != today:
        state['todayCount'] = 0
    
    state['lastPublishTime'] = now.isoformat()
    state['lastPublishDate'] = today
    state['todayCount'] = state.get('todayCount', 0) + 1
    save_state(state)
    print(f"📊 今日已发布 {state['todayCount']} 篇")


# ============ 内容获取 ============

def get_arxiv_papers():
    """获取 arXiv 最新论文"""
    papers = []
    categories = [
        ('cs.AI', '🤖 AI'),
        ('cs.LG', '🧠 机器学习'),
        ('cs.CL', '💬 NLP'),
    ]
    
    for cat, cat_emoji in categories:
        try:
            rss_url = f"http://export.arxiv.org/rss/{cat}"
            req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read().decode('utf-8')
            
            root = ET.fromstring(data)
            
            for item in root.findall('.//item')[:2]:
                title = item.find('title').text.strip().replace('\n', ' ') if item.find('title') is not None else ""
                guid = item.find('guid')
                arxiv_id = ""
                if guid is not None and guid.text:
                    match = re.search(r'(\d+\.\d+)', guid.text)
                    if match:
                        arxiv_id = match.group(1)
                
                creator = item.find('.//{http://purl.org/dc/elements/1.1/}creator')
                authors = creator.text if creator is not None else "未知"
                authors = [a.strip() for a in authors.split(',')][:2]
                
                papers.append({
                    'title': title,
                    'arxiv_id': arxiv_id,
                    'authors': authors,
                    'category': cat_emoji,
                    'url': f"https://arxiv.org/abs/{arxiv_id}"
                })
                time.sleep(0.3)
                
        except Exception as e:
            print(f"获取 {cat} 失败: {e}")
    
    return papers


def get_arxiv_paper_detail(arxiv_id):
    """获取单篇论文详情"""
    try:
        url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read().decode('utf-8')
        
        root = ET.fromstring(data)
        entry = root.find('entry')
        
        if entry is None:
            return None
        
        title = entry.find('title').text.strip().replace('\n', ' ') if entry.find('title') is not None else ""
        summary = entry.find('summary').text.strip() if entry.find('summary') is not None else ""
        authors = [a.find('name').text for a in entry.findall('author')][:3]
        published = entry.find('published').text[:10] if entry.find('published') is not None else ""
        
        return {
            'title': title,
            'summary': summary,
            'authors': authors,
            'published': published,
            'url': f"https://arxiv.org/abs/{arxiv_id}"
        }
    except Exception as e:
        print(f"获取论文详情失败: {e}")
        return None


# ============ 小红书风格改写 ============

def extract_keywords(title):
    """从标题提取关键词"""
    stop_words = ['A', 'An', 'The', 'for', 'with', 'using', 'based', 'via', 
                  '一种', '基于', '研究', '方法', '系统']
    
    words = re.findall(r'[A-Za-z]{4,}', title)
    words = [w for w in words if w.lower() not in [s.lower() for s in stop_words]]
    
    if words:
        return words[0].title()
    
    cn_words = re.findall(r'[\u4e00-\u9fa5]{2,}', title)
    cn_words = [w for w in cn_words if w not in stop_words]
    
    return cn_words[0] if cn_words else "AI"


def simplify_summary(summary, max_chars=300):
    """简化摘要"""
    summary = re.sub(r'\s+', ' ', summary)
    summary = summary[:max_chars]
    
    replacements = [
        ("本研究", "这篇论文"),
        ("本文", "这篇论文"),
        ("实验结果表明", "实测数据表明"),
        ("提出了", "搞出了"),
        ("方法", "黑科技"),
        ("显著提升", "效果炸裂"),
        ("SOTA", "刷新世界纪录"),
    ]
    
    for old, new in replacements:
        summary = summary.replace(old, new)
    
    return summary


def get_practical_impacts(summary):
    """提取实际影响"""
    impacts = []
    keywords = {
        'chat': '聊天更自然，AI助手更好用',
        'write': '自动写文案、总结',
        'image': '描述词生成图片',
        'video': 'AI生成视频',
        'code': '编程效率提升',
        'search': '搜索结果更精准',
        'translate': '翻译又快又准',
        'learn': '个性化学习更高效',
    }
    
    summary_lower = summary.lower()
    for kw, impact in keywords.items():
        if kw in summary_lower:
            impacts.append(impact)
    
    return impacts[:2] if impacts else ['让AI助手更聪明', '改变生活方式']


def rewrite_to_xiaohongshu(paper):
    """
    将论文改写为小红书风格（800字以内）
    """
    title = paper.get('title', '')
    summary = paper.get('summary', paper.get('title', ''))
    authors = paper.get('authors', [])
    url = paper.get('url', '')
    
    lines = []
    char_count = 0
    
    # 标题
    keywords = extract_keywords(title)
    title_template = random.choice(TITLE_TEMPLATES)
    xhs_title = title_template.format(keywords)
    lines.append(xhs_title)
    char_count += len(xhs_title) + 2
    
    # 开头
    openings = ["姐妹们！", "宝子们！", "科研人狂喜！"]
    opening = random.choice(openings)
    lines.append(opening)
    char_count += len(opening) + 1
    
    lines.append("今天刷到一篇超炸的论文，必须分享！")
    char_count += 15
    lines.append("")
    char_count += 1
    
    # 论文信息
    lines.append(f"📖 {title[:40]}...")
    char_count += len(title[:40]) + 4
    
    if authors:
        author_str = "、".join(authors[:2])
        lines.append(f"👨‍🔬 {author_str}")
        char_count += len(author_str) + 4
    
    lines.append(f"🔗 {url}")
    char_count += len(url) + 4
    lines.append("")
    char_count += 1
    
    # 检查字数，超了就截断
    if char_count > maxContentLength - 100:
        # 简短版
        lines.append("━━━")
        lines.append("")
        lines.append("🚀 核心技术：")
        summary_short = simplify_summary(summary, 150)
        lines.append(f"· {summary_short}")
        lines.append("")
        lines.append("💡 实际影响：")
        impacts = get_practical_impacts(summary)
        for impact in impacts[:2]:
            lines.append(f"· {impact}")
    else:
        # 完整版
        lines.append("━━━")
        lines.append("")
        lines.append("🚀 核心技术：")
        summary_parts = simplify_summary(summary, 200).split('. ')
        for part in summary_parts[:2]:
            if part and len(part) > 5:
                lines.append(f"· {part}")
        
        lines.append("")
        lines.append("━━━")
        lines.append("")
        lines.append("💡 对普通人的影响：")
        impacts = get_practical_impacts(summary)
        for impact in impacts[:2]:
            lines.append(f"· {impact}")
        
        lines.append("")
        lines.append("💼 对行业的影响：")
        lines.append("· 推动AI技术向前发展")
    
    lines.append("")
    lines.append("━━━")
    lines.append("")
    
    # 检查总字数
    full_content = "\n".join(lines)
    if len(full_content) > maxContentLength:
        # 截断到限制字数
        while len("\n".join(lines)) > maxContentLength - 50:
            lines.pop()
        lines.append("...")
    
    # 结尾
    lines.append("你觉得这个技术牛不牛？")
    lines.append("评论区聊聊~ 🙋‍♀️")
    lines.append("")
    
    # 标签（限制数量）
    tags_str = " ".join([f"#{tag}" for tag in DEFAULT_TAGS[:6]])
    lines.append(tags_str)
    
    return "\n".join(lines)


# ============ 配图生成 ============

def generate_image_prompt(title):
    """根据标题生成配图提示词"""
    keywords = extract_keywords(title)
    
    prompt = f"""A clean, modern tech illustration for "{keywords}",
bright gradient background (blue to purple),
minimalist design with neural network elements,
no text, clean aesthetic,
3:4 vertical aspect ratio,
high quality digital art style"""
    
    return prompt


def save_image_prompt(title):
    """保存配图提示词（供后续生成）"""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    prompt = generate_image_prompt(title)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"image_prompt_{timestamp}.txt"
    filepath = os.path.join(IMAGES_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"标题: {title}\n")
        f.write(f"提示词:\n{prompt}\n")
    
    print(f"📝 配图提示词已保存: {filepath}")
    print(f"提示词: {prompt}")
    
    return filepath


# ============ 发布 ============

def parse_cookie_string(cookie_string):
    """解析 cookie"""
    cookies = []
    for item in cookie_string.split(';'):
        item = item.strip()
        if '=' in item:
            name, value = item.split('=', 1)
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.xiaohongshu.com',
                'path': '/'
            })
    return cookies


async def publish_to_xiaohongshu(content, image_path=None, headless=True):
    """发布到小红书"""
    from playwright.async_api import async_playwright
    
    result = {
        'success': False,
        'message': '',
        'error': None
    }
    
    # 记录发布
    record_publish()
    
    async with async_playwright() as p:
        try:
            print("🚀 启动浏览器...")
            browser = await p.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            cookies = parse_cookie_string(XHS_COOKIE)
            await context.add_cookies(cookies)
            
            page = await context.new_page()
            
            print("🌐 打开小红书...")
            await page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=60000)
            await asyncio.sleep(5)
            
            if 'login' in page.url.lower():
                result['error'] = 'Cookie 已过期'
                await browser.close()
                return result
            
            print("📝 输入内容...")
            
            # 点击输入框
            for selector in ['textarea', '[contenteditable="true"]', '.note-textarea']:
                try:
                    await page.locator(selector).first.click(timeout=2000)
                    break
                except:
                    continue
            
            await asyncio.sleep(1)
            
            # 输入内容
            await page.keyboard.type(content, delay=20)
            await asyncio.sleep(2)
            
            # 如果有图片，先上传图片
            # if image_path and os.path.exists(image_path):
            #     print("🖼️ 上传配图...")
            #     await page.set_input_files('input[type="file"]', image_path)
            #     await asyncio.sleep(3)
            
            print("🏷️ 添加标签...")
            for tag in DEFAULT_TAGS[:5]:
                await page.keyboard.press(',')
                await page.keyboard.type(tag, delay=30)
                await asyncio.sleep(0.3)
            
            print("✅ 点击发布...")
            for selector in ['button:has-text("发布")', '.publish-btn']:
                try:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=2000):
                        await btn.click()
                        break
                except:
                    continue
            
            await asyncio.sleep(5)
            
            page_text = await page.inner_text('body')
            if '发布成功' in page_text or '已发布' in page_text:
                result['success'] = True
                result['message'] = '发布成功！'
            else:
                result['error'] = '发布结果未知'
            
            await page.close()
            
        except Exception as e:
            result['error'] = str(e)
        
        finally:
            try:
                await browser.close()
            except:
                pass
    
    return result


# ============ 主函数 ============

async def main():
    """主函数"""
    print("=" * 50)
    print("📚 小红书 AI 论文自动发布 v4")
    print("   (字数控制 + 发布频率保护)")
    print("=" * 50)
    
    # 检查是否可以发布
    can, reason = can_publish()
    if not can:
        print(f"\n⚠️ {reason}")
        print("💡 建议：等待一段时间后再试")
        return {'success': False, 'error': reason}
    
    print(f"\n✅ {reason}，开始发布...")
    
    # 获取论文
    print("\n📥 获取最新论文...")
    papers = get_arxiv_papers()
    print(f"   获取到 {len(papers)} 篇论文")
    
    if not papers:
        print("❌ 获取论文失败")
        return {'success': False, 'error': '获取论文失败'}
    
    # 选择第一篇论文获取详情
    paper = papers[0]
    print(f"\n📖 论文: {paper['title'][:50]}...")
    
    paper_detail = get_arxiv_paper_detail(paper['arxiv_id'])
    if paper_detail:
        paper.update(paper_detail)
    
    # 改写为小红书风格
    print("\n✍️ 改写为小红书风格...")
    content = rewrite_to_xiaohongshu(paper)
    
    # 检查字数
    content_length = len(content)
    print(f"📊 内容字数: {content_length} 字")
    if content_length > maxContentLength:
        print(f"⚠️ 超过限制 ({maxContentLength} 字)，已自动截断")
    
    # 生成配图提示词
    print("\n🎨 生成配图提示词...")
    save_image_prompt(paper['title'])
    
    # 保存内容
    os.makedirs(CONTENT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    content_file = f"{CONTENT_DIR}/content_{timestamp}.txt"
    
    with open(content_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 内容已保存: {content_file}")
    
    # 显示内容预览
    print("\n📄 内容预览:")
    print("-" * 30)
    print(content[:600] + "...")
    print("-" * 30)
    
    # 尝试发布
    print("\n🚀 尝试发布到小红书...")
    result = await publish_to_xiaohongshu(content, headless=False)
    
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ 发布成功！")
        print("🎉 请去小红书查看")
    else:
        print(f"⚠️ 发布失败: {result['error']}")
        print(f"💾 内容已保存，可手动发布")
    
    return result


if __name__ == "__main__":
    asyncio.run(main())
