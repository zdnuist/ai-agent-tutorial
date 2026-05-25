#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin

def extract_models_from_list_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    models = []

    # 查找所有包含模型链接的元素
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/models/' in href:
            # 提取slug
            match = re.search(r'/models/([^/]+)', href)
            if match:
                slug = match.group(1)
                # 查找标题 - 尝试在链接或其父元素中查找
                title = link.get_text(strip=True)
                if title:
                    models.append({'slug': slug, 'title': title})

    return models

def fetch_model_content(slug, session):
    url = f'https://mungermodels.com/models/{slug}'
    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            print(f"404 or error for {slug}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {slug}: {e}")
        return None

def parse_model_page(html_content, slug):
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取标题 - 查找h1标签
    title = ""
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text(strip=True)
    else:
        # 尝试从meta标签或title标签获取
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            title = meta_title['content']

    # 提取描述 - 查找meta description
    description = ""
    meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', property='og:description')
    if meta_desc and meta_desc.get('content'):
        description = meta_desc['content']

    # 提取主要内容 - 查找article或main标签
    content = ""
    article = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('content|article|main'))
    if article:
        # 获取所有标题和段落
        for element in article.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'blockquote', 'pre']):
            if element.name.startswith('h'):
                content += f"## {element.get_text(strip=True)}\n\n"
            elif element.name == 'p':
                text = element.get_text(strip=True)
                if text:
                    content += f"{text}\n\n"
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    content += f"- {li.get_text(strip=True)}\n"
                content += "\n"
            elif element.name == 'blockquote':
                content += f"> {element.get_text(strip=True)}\n\n"
            elif element.name == 'pre':
                content += f"```\n{element.get_text()}\n```\n\n"

    # 如果没有找到主要内容，尝试body
    if not content or len(content) < 100:
        body = soup.find('body')
        if body:
            for element in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'blockquote', 'pre']):
                if element.name.startswith('h') and element.name != 'h1':
                    content += f"## {element.get_text(strip=True)}\n\n"
                elif element.name == 'p':
                    text = element.get_text(strip=True)
                    if text and not text.startswith('#'):
                        content += f"{text}\n\n"
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li'):
                        content += f"- {li.get_text(strip=True)}\n"
                    content += "\n"

    return {
        'title': title,
        'description': description,
        'content': content
    }

def save_model_markdown(model_num, slug, data, output_dir):
    filename = f"{model_num:03d}-{slug}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        # YAML front matter
        f.write('---\n')
        f.write(f'title: "{data["title"]}"\n')
        if data['description']:
            f.write(f'description: "{data["description"]}"\n')
        f.write(f'slug: {slug}\n')
        f.write(f'model_number: {model_num}\n')
        f.write('---\n\n')

        # 内容
        if data['content']:
            f.write(data['content'])

    return filepath

def main():
    # 定义所有232个模型的slug列表（基于已知的模型列表）
    # 这里我需要从列表页面提取完整列表
    # 让我先尝试获取列表页面

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    output_dir = '/workspace/munger-models/models/'
    os.makedirs(output_dir, exist_ok=True)

    # 获取列表页面
    list_url = 'https://mungermodels.com/all'
    print(f"Fetching list page: {list_url}")

    try:
        response = session.get(list_url, timeout=30)
        if response.status_code == 200:
            models = extract_models_from_list_page(response.text)
            print(f"Found {len(models)} models in list")

            if len(models) < 232:
                print(f"Warning: Only found {len(models)} models, expected 232")
                # 继续处理已找到的模型
        else:
            print(f"Failed to fetch list page: {response.status_code}")
            return
    except Exception as e:
        print(f"Error fetching list page: {e}")
        return

    # 批量获取每个模型
    success_count = 0
    for idx, model in enumerate(models, 1):
        slug = model['slug']
        model_num = idx

        print(f"[{model_num}/232] Fetching {slug}...")

        html_content = fetch_model_content(slug, session)
        if html_content:
            data = parse_model_page(html_content, slug)
            filepath = save_model_markdown(model_num, slug, data, output_dir)
            print(f"  -> Saved: {filepath}")
            success_count += 1
        else:
            print(f"  -> Skipped (404 or error)")

        # 礼貌延迟
        time.sleep(0.5)

    print(f"\nCompleted: {success_count}/232 models saved successfully")

if __name__ == '__main__':
    main()
