#!/usr/bin/env python3
"""
小红书 AI 论文自动发布脚本 v2
支持模拟登录和多种发布方式
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

DEFAULT_TAGS = ["AI论文", "机器学习", "人工智能", "深度学习", "NLP", "计算机视觉", "学术研究", "论文推荐", "技术前沿", "科研"]


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
            
            for item in root.findall('.//item')[:4]:
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
                    'url': f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else link,
                    'arxiv_id': arxiv_id,
                    'authors': authors,
                    'category': cat_emoji
                })
                
                time.sleep(0.3)
                
        except Exception as e:
            print(f"获取 {cat} 失败: {e}")
    
    return papers


def format_xiaohongshu_content(papers):
    """格式化小红书内容"""
    if not papers:
        return None
    
    seen = set()
    unique = []
    for p in papers:
        if p['url'] not in seen:
            seen.add(p['url'])
            unique.append(p)
    
    unique = unique[:6]
    today = datetime.now().strftime('%m月%d日')
    
    content = f"""🤖 AI论文速递 | {today}

✨ 今日精选 {len(unique)} 篇顶会论文
📚 来源: arXiv.org

━━━━━

"""
    
    for i, paper in enumerate(unique, 1):
        title = paper['title'][:45] + "..." if len(paper['title']) > 45 else paper['title']
        authors = ", ".join(paper['authors']) if paper['authors'] else "未知"
        
        content += f"{i}. {title}\n"
        content += f"   👤 {authors}\n"
        content += f"   {paper['category']}\n"
        content += f"   🔗 {paper['url']}\n\n"
    
    content += """━━━━━

📌 论文链接已整理
💡 关注我，每天分享AI前沿论文！

"""
    
    content += " ".join([f"#{tag}" for tag in DEFAULT_TAGS[:8]])
    
    return content


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
        'error': None,
        'content_saved': True
    }
    
    # 保存内容到文件
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
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                ignore_https_errors=True
            )
            
            # 设置 cookie
            cookies = parse_cookie_string(XHS_COOKIE)
            await context.add_cookies(cookies)
            
            page = await context.new_page()
            
            print("🌐 打开小红书创作页面...")
            await page.goto('https://creator.xiaohongshu.com/publish/publish', timeout=60000)
            await asyncio.sleep(5)
            
            # 检查是否跳转到登录页
            current_url = page.url
            if 'login' in current_url.lower():
                result['error'] = 'Cookie 已过期，请更新 cookie'
                await browser.close()
                return result
            
            print("📝 输入正文内容...")
            
            # 尝试多种选择器
            selectors = [
                'textarea',
                '[contenteditable="true"]',
                '.note-textarea',
                '.editor-input',
                '#editor > div'
            ]
            
            clicked = False
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        await element.click()
                        clicked = True
                        print(f"   ✅ 使用选择器: {selector}")
                        break
                except:
                    continue
            
            if not clicked:
                # 使用 JavaScript 注入
                await page.evaluate('''() => {
                    const editor = document.querySelector('.note-textarea') || 
                                   document.querySelector('[contenteditable="true"]') ||
                                   document.querySelector('textarea');
                    if (editor) editor.focus();
                }''')
                clicked = True
            
            await asyncio.sleep(1)
            
            # 输入内容
            await page.keyboard.type(content, delay=20)
            await asyncio.sleep(2)
            
            print("🏷️ 添加标签...")
            for tag in DEFAULT_TAGS[:6]:
                await page.keyboard.press(',')
                await page.keyboard.type(tag, delay=30)
                await asyncio.sleep(0.3)
            
            print("✅ 点击发布按钮...")
            # 尝试多种发布按钮选择器
            publish_selectors = [
                'button:has-text("发布")',
                'button:has-text("立即发布")',
                '.publish-btn',
                '[class*="publish"]'
            ]
            
            for selector in publish_selectors:
                try:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=2000):
                        await btn.click()
                        print(f"   ✅ 点击按钮: {selector}")
                        break
                except:
                    continue
            
            await asyncio.sleep(5)
            
            # 检查页面状态
            page_text = await page.inner_text('body')
            
            if '发布成功' in page_text or '已发布' in page_text:
                result['success'] = True
                result['message'] = '发布成功！'
            else:
                # 截图以便调试
                screenshot_file = f"{output_dir}/debug_{timestamp}.png"
                await page.screenshot(path=screenshot_file)
                print(f"📸 截图已保存: {screenshot_file}")
                result['error'] = '发布结果未知，请手动检查'
            
            await page.close()
            
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ 错误: {e}")
        
        finally:
            try:
                await browser.close()
            except:
                pass
    
    return result


async def main():
    """主函数"""
    print("=" * 50)
    print("📚 小红书 AI 论文自动发布 v2")
    print("=" * 50)
    
    # 1. 获取论文
    print("\n📥 步骤1: 获取最新论文...")
    papers = get_arxiv_papers()
    print(f"   ✅ 获取到 {len(papers)} 篇论文")
    
    if not papers:
        print("   ❌ 获取论文失败")
        return
    
    # 2. 格式化内容
    print("\n📝 步骤2: 格式化内容...")
    content = format_xiaohongshu_content(papers)
    print(f"   ✅ 内容长度: {len(content)} 字符")
    
    # 3. 发布
    print("\n🚀 步骤3: 发布到小红书...")
    result = await publish_to_xiaohongshu(content, headless=False)
    
    # 4. 输出结果
    print("\n" + "=" * 50)
    print("📊 发布结果")
    print("=" * 50)
    
    if result['success']:
        print("✅ 状态: 发布成功！")
        print("🎉 请去小红书查看已发布的笔记")
    else:
        print(f"⚠️ 状态: {result['error']}")
        print("\n📋 已保存内容，可在以下位置找到:")
        print("   ~/.openclaw/workspace/xhs_content/")
        print("\n💡 您可以:")
        print("   1. 复制保存的内容手动发布到小红书")
        print("   2. 更新 cookie 后重试")
        print("   3. 使用非无头模式重试: python3 xhs_auto_publish.py --visible")
    
    return result


if __name__ == "__main__":
    # 检查参数
    if len(sys.argv) > 1 and sys.argv[1] == '--visible':
        asyncio.run(main())
    else:
        asyncio.run(main())
