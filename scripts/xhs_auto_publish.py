#!/usr/bin/env python3
"""
小红书 AI 论文自动发布脚本 v3
支持小红书风格改写 + 自动发布
"""

import asyncio
import sys
import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import time

# 小红书 cookie
XHS_COOKIE = """abRequestId=32882dce-eea4-5adc-94f4-1a5ef638b832; webBuild=6.1.0; xsecappid=xhs-pc-web; a1=19d04d371a9mdz5y8fdub5kq79rj2ik6p4rvgjb3m30000235958; webId=04bc6d18b45ea41a0c0f1dca66931e15; acw_tc=0a50885617739024597153633e2e5fe0053f22c63e6d5f01bb4a7709b32325; websectiga=984412fef754c018e472127b8effd174be8a5d51061c991aadd200c69a2801d6; sec_poison_id=8bcb6a34-f419-46e8-96e8-319e56c59b2c; gid=yjf84fqY8JU0yjf84fqWy4VD0j6fu2vYif7DFq62TAWjFhq8VJ3TKk888Jq2j2Y8qJ8ddWif; web_session=04006951ed7f0c302ca2f3d28e3b4b688a580a; id_token=VjEAAGJse5ch5LkIk4Sx6on2Pp5wAthCWRws+G0dsCMgXGfjfc0ulIwm206PtDaDxAa7avryO43Osy+yPn2Tt/cViYX1sse9jVF3IZpq4wqJqK3y0gB28eYDzSnL+6EJZz/gIU44; unread={%22ub%22:%2269b8faa5000000001a02f70e%22%2C%22ue%22:%2269b95d8a000000001b0235e7%22%2C%22uc%22:4}; loadts=1773902534867"""

# 小红书风格标签
DEFAULT_TAGS = [
    "论文摘要", "AI前沿", "科研", "科技资讯",
    "人工智能", "机器学习", "深度学习", "ChatGPT",
    "大模型", "技术突破", "学术研究"
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
    "刚刚！{}传来大消息",
]


def get_arxiv_paper_detail(arxiv_id):
    """获取单篇 arXiv 论文详情"""
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
            
            for item in root.findall('.//item')[:3]:
                title = item.find('title').text.strip().replace('\n', ' ') if item.find('title') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                
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
                    'category': cat_emoji
                })
                
                time.sleep(0.3)
                
        except Exception as e:
            print(f"获取 {cat} 失败: {e}")
    
    return papers


def rewrite_to_xiaohongshu_style(paper):
    """
    将论文改写为小红书风格
    
    规则：
    1. 标题：震惊体/揭秘体
    2. 开头：口语化称呼
    3. 正文：表情符号、换行、强调影响
    4. 结尾：互动引导
    5. 标签：小红书风格标签
    """
    
    title = paper.get('title', '')
    summary = paper.get('summary', '')
    authors = paper.get('authors', [])
    url = paper.get('url', '')
    category = paper.get('category', '🤖 AI')
    
    # 生成震惊体标题
    title_keywords = extract_keywords(title)
    if title_keywords:
        import random
        title_template = random.choice(TITLE_TEMPLATES)
        xhs_title = title_template.format(title_keywords)
    else:
        xhs_title = f"🔥 AI领域重大突破！{title[:20]}..."
    
    # 改写正文
    content_lines = []
    
    # 开头
    openings = ["姐妹们！", "宝子们！", "科研人狂喜！", "友友们！", "小伙伴们！"]
    import random
    opening = random.choice(openings)
    content_lines.append(opening)
    content_lines.append("")
    
    # 论文介绍
    content_lines.append(f"今天刷到一篇超炸的论文，必须分享给你们！")
    content_lines.append("")
    content_lines.append(f"📖 论文：{title[:50]}...")
    if authors:
        author_str = "、".join(authors[:2])
        content_lines.append(f"👨‍🔬 作者：{author_str}")
    content_lines.append(f"🔗 {url}")
    content_lines.append("")
    
    # 核心技术（从摘要中提取）
    content_lines.append("━━━")
    content_lines.append("")
    content_lines.append("🚀 核心技术：")
    
    # 简化摘要，添加表情
    summary_points = simplify_summary(summary)
    for point in summary_points[:3]:
        content_lines.append(f"· {point}")
    
    content_lines.append("")
    content_lines.append("━━━")
    content_lines.append("")
    
    # 对普通人的影响
    content_lines.append("💡 对普通人的影响：")
    impacts = get_practical_impacts(summary)
    for impact in impacts[:3]:
        content_lines.append(f"· {impact}")
    
    content_lines.append("")
    
    # 对行业的影响
    content_lines.append("💼 对行业的影响：")
    industry_impacts = get_industry_impacts(summary)
    for impact in industry_impacts[:2]:
        content_lines.append(f"· {impact}")
    
    content_lines.append("")
    content_lines.append("━━━")
    content_lines.append("")
    
    # 结尾互动
    content_lines.append("你觉得这个技术牛不牛？")
    content_lines.append("评论区聊聊~ 🙋‍♀️")
    content_lines.append("")
    
    # 标签
    tags_str = " ".join([f"#{tag}" for tag in DEFAULT_TAGS[:8]])
    content_lines.append(tags_str)
    
    # 组合完整内容
    full_content = "\n".join(content_lines)
    
    return {
        'title': xhs_title,
        'content': full_content,
        'url': url,
        'tags': DEFAULT_TAGS[:10]
    }


def extract_keywords(title):
    """从标题提取关键词"""
    # 移除常见词
    stop_words = ['A', 'An', 'The', 'for', 'with', 'using', 'based', 'via', 
                  '一种', '基于', '使用', '通过', '研究', '方法', '系统']
    
    words = re.findall(r'[A-Za-z]+', title)
    words = [w for w in words if len(w) > 3 and w.lower() not in [s.lower() for s in stop_words]]
    
    if words:
        return words[0].title()
    
    # 中文关键词
    cn_words = re.findall(r'[\u4e00-\u9fa5]{2,}', title)
    cn_words = [w for w in cn_words if w not in stop_words]
    
    if cn_words:
        return cn_words[0]
    
    return "AI"


def simplify_summary(summary):
    """简化摘要，提取关键点"""
    points = []
    
    # 移除多余空白
    summary = re.sub(r'\s+', ' ', summary)
    
    # 截取前500字符
    summary = summary[:500]
    
    # 分割成句子
    sentences = re.split(r'[.。]', summary)
    
    for sent in sentences[:3]:
        sent = sent.strip()
        if len(sent) > 20:
            # 改写表述
            sent = sent.replace("本研究", "这篇论文")
            sent = sent.replace("本文", "这篇论文")
            sent = sent.replace("实验结果表明", "实测数据表明")
            sent = sent.replace("提出了", "搞出了")
            sent = sent.replace("方法", "黑科技")
            sent = sent.replace("显著提升", "效果炸裂")
            sent = sent.replace("SOTA", "刷新世界纪录")
            points.append(sent)
    
    return points if points else ["AI 技术取得重大突破"]


def get_practical_impacts(summary):
    """提取对普通人的影响"""
    impacts = []
    
    keywords = {
        'chat': '聊天更自然，AI助手更好用',
        'write': '自动写文案、总结，一键搞定',
        'image': '生成图片只需描述词',
        'video': 'AI 生成视频成为可能',
        'code': '编程效率提升 10 倍',
        'search': '搜索结果更精准',
        'translate': '翻译又快又准',
        'learn': '个性化学习更高效',
        'medical': '辅助诊断更准确',
        'finance': '智能投顾更靠谱'
    }
    
    summary_lower = summary.lower()
    for kw, impact in keywords.items():
        if kw in summary_lower:
            impacts.append(impact)
    
    if not impacts:
        impacts = ['让 AI 助手更聪明更好用', '改变我们的生活方式']
    
    return impacts[:3]


def get_industry_impacts(summary):
    """提取对行业的影响"""
    impacts = []
    
    keywords = {
        'health': '医疗健康行业将被颠覆',
        'finance': '金融行业迎来智能升级',
        'educat': '教育行业迎来变革',
        'manufactur': '制造业智能化加速',
        'retail': '零售行业体验升级',
        'media': '内容创作行业被改变',
        'legal': '法律行业效率提升'
    }
    
    summary_lower = summary.lower()
    for kw, impact in keywords.items():
        if kw in summary_lower:
            impacts.append(impact)
    
    if not impacts:
        impacts = ['推动 AI 技术向前发展', '预计市场规模超百亿']
    
    return impacts[:2]


def format_xiaohongshu_for_batch(papers):
    """批量论文的小红书格式（多条合并）"""
    if not papers:
        return None
    
    today = datetime.now().strftime('%m月%d日')
    
    content_lines = []
    
    # 标题
    content_lines.append(f"🤖 AI论文速递 | {today}")
    content_lines.append("")
    content_lines.append(f"✨ 今日精选 {len(papers)} 篇顶会论文")
    content_lines.append("📚 来源: arXiv.org")
    content_lines.append("")
    content_lines.append("━━━")
    content_lines.append("")
    
    # 论文列表
    for i, paper in enumerate(papers[:6], 1):
        title = paper.get('title', '')[:50]
        authors = "、".join(paper.get('authors', ['未知'])[:2])
        category = paper.get('category', '🤖 AI')
        
        content_lines.append(f"{i}. {title}...")
        content_lines.append(f"   👤 {authors}")
        content_lines.append(f"   {category}")
        content_lines.append("")
    
    content_lines.append("━━━")
    content_lines.append("")
    
    # 结尾
    content_lines.append("📌 论文链接已整理")
    content_lines.append("💡 关注我，每天分享 AI 前沿论文！")
    content_lines.append("")
    
    # 标签
    tags_str = " ".join([f"#{tag}" for tag in DEFAULT_TAGS[:8]])
    content_lines.append(tags_str)
    
    return "\n".join(content_lines)


def parse_cookie_string(cookie_string):
    """解析 cookie 字符串"""
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


async def publish_to_xiaohongshu(content, headless=True):
    """发布到小红书"""
    from playwright.async_api import async_playwright
    
    result = {
        'success': False,
        'message': '',
        'error': None
    }
    
    # 保存内容
    output_dir = "/Users/wangfeng/.openclaw/workspace/xhs_content"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    content_file = f"{output_dir}/content_{timestamp}.txt"
    
    with open(content_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📁 内容已保存到: {content_file}")
    
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
            
            print("🌐 打开小红书创作页面...")
            await page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=60000)
            await asyncio.sleep(5)
            
            if 'login' in page.url.lower():
                result['error'] = 'Cookie 已过期，请更新 cookie'
                await browser.close()
                return result
            
            print("📝 输入内容...")
            
            # 点击输入框
            selectors = ['textarea', '[contenteditable="true"]', '.note-textarea']
            for selector in selectors:
                try:
                    await page.locator(selector).first.click(timeout=2000)
                    break
                except:
                    continue
            
            await asyncio.sleep(1)
            
            # 输入内容
            await page.keyboard.type(content, delay=20)
            await asyncio.sleep(2)
            
            print("🏷️ 添加标签...")
            for tag in DEFAULT_TAGS[:6]:
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
                result['error'] = '发布结果未知，请手动检查'
            
            await page.close()
            
        except Exception as e:
            result['error'] = str(e)
        
        finally:
            try:
                await browser.close()
            except:
                pass
    
    return result


async def main():
    """主函数"""
    print("=" * 50)
    print("📚 小红书 AI 论文自动发布 v3")
    print("   (小红书风格改写版)")
    print("=" * 50)
    
    mode = 'rewrite'  # 默认使用改写模式
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--batch':
            mode = 'batch'
        elif sys.argv[1] == '--arxiv':
            mode = 'single'
            arxiv_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    if mode == 'single' and 'arxiv_id' in dir():
        # 获取单篇论文并改写
        print(f"\n📥 获取 arXiv 论文: {arxiv_id}")
        paper = get_arxiv_paper_detail(arxiv_id)
        if paper:
            print("\n✍️ 改写为小红书风格...")
            result = rewrite_to_xiaohongshu_style(paper)
            content = f"{result['title']}\n\n{result['content']}"
            print("\n📄 改写结果:")
            print("-" * 30)
            print(content[:800] + "...")
            print("-" * 30)
    else:
        # 获取多篇论文
        print("\n📥 获取最新论文...")
        papers = get_arxiv_papers()
        print(f"   获取到 {len(papers)} 篇论文")
        
        if not papers:
            print("   获取论文失败")
            return
        
        if mode == 'rewrite':
            # 改写第一篇
            print("\n✍️ 改写第一篇为小红书风格...")
            paper_detail = get_arxiv_paper_detail(papers[0]['arxiv_id'])
            if paper_detail:
                paper_detail.update(papers[0])
                result = rewrite_to_xiaohongshu_style(paper_detail)
                content = f"{result['title']}\n\n{result['content']}"
                print("\n📄 改写结果:")
                print("-" * 30)
                print(content[:800] + "...")
                print("-" * 30)
            else:
                content = format_xiaohongshu_for_batch(papers)
        else:
            # 批量格式
            content = format_xiaohongshu_for_batch(papers)
    
    # 保存内容
    output_dir = "/Users/wangfeng/.openclaw/workspace/xhs_content"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    content_file = f"{output_dir}/content_{timestamp}.txt"
    
    with open(content_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n💾 内容已保存: {content_file}")
    
    # 尝试发布
    print("\n🚀 尝试发布到小红书...")
    publish_result = await publish_to_xiaohongshu(content, headless=False)
    
    print("\n" + "=" * 50)
    if publish_result['success']:
        print("✅ 发布成功！")
    else:
        print(f"⚠️ 发布失败: {publish_result['error']}")
        print("\n📋 您可以:")
        print("   1. 查看保存的内容文件手动发布")
        print("   2. 更新 cookie 后重试")
    
    return publish_result


if __name__ == "__main__":
    asyncio.run(main())
