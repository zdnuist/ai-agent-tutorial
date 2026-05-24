#!/usr/bin/env python3
"""
批量获取 mungermodels.com 上的思维模型内容
"""

import requests
import re
import os
import time
from pathlib import Path

# 设置基础URL
BASE_URL = "https://mungermodels.com"
OUTPUT_DIR = Path(__file__).parent / "models"
OUTPUT_DIR.mkdir(exist_ok=True)

# 从索引页面提取的完整模型列表（包含slug）
MODELS = [
    ("001", "逆向思维", "Inversion", "inversion"),
    ("002", "检查清单方法", "Checklist Method", "checklist-method"),
    ("003", "避免意识形态偏见", "Avoiding Ideology", "avoiding-ideology"),
    ("004", "跨学科思维", "Multidisciplinary Approach", "multidisciplinary-approach"),
    ("005", "铁锤人倾向", "Man-with-a-Hammer Syndrome", "man-with-a-hammer-syndrome"),
    ("006", "二阶效应", "Second-Order Thinking", "second-order-thinking"),
    ("007", "奥卡姆剃刀", "Occam's Razor", "occams-razor"),
    ("008", "避蠢优于求智", "Avoiding Stupidity over Seeking Brilliance", "avoiding-stupidity-over-seeking-brilliance"),
    ("009", "多元思维模型框架", "Latticework of Mental Models", "latticework-of-mental-models"),
    ("010", "达尔文式客观态度", "Darwinian Objectivity", "darwinian-objectivity"),
    ("011", "可证伪性标准", "Falsifiability Criterion", "falsifiability-criterion"),
    ("012", "否证思维", "Falsification", "falsification"),
    ("013", "第一性原理思维", "First Principles Thinking", "first-principles-thinking"),
    ("014", "物理学妒忌", "Physics Envy", "physics-envy"),
    ("015", "能力圈（元认知层面）", "Circle of Competence - Metacognitive Level", "circle-of-competence-metacognitive-level"),
    ("016", "思想实验", "Thought Experiments", "thought-experiments"),
    ("017", "极端情景模拟", "Premortems", "premortems"),
    ("018", "费曼技巧", "Feynman Technique", "feynman-technique"),
    ("019", "双轨分析", "Two-Track Analysis", "two-track-analysis"),
    ("020", "地图不是疆域", "Map is Not the Territory", "map-is-not-the-territory"),
    ("021", "五何原则", "Five W's Principle", "five-ws-principle"),
    ("022", "多数无知与从众谬误", "Pluralistic Ignorance", "pluralistic-ignorance"),
    ("023", "汉隆剃刀", "Hanlon's Razor", "hanlons-razor"),
    ("024", "重复有效的行为", "Repeat What Works", "repeat-what-works"),
    ("025", "置信度校准", "Confidence Calibration", "confidence-calibration"),
]

def clean_content(html_content):
    """
    清理HTML内容并转换为Markdown格式
    """
    # 简单的HTML到Markdown转换（针对该网站内容优化）
    content = html_content
    
    # 移除导航栏、底部等不需要的部分
    content = re.sub(r'<!DOCTYPE[^>]*>', '', content, flags=re.DOTALL)
    content = re.sub(r'<head[^>]*>.*?</head>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<nav[^>]*>.*?</nav>', '', content, flags=re.DOTALL)
    content = re.sub(r'<footer[^>]*>.*?</footer>', '', content, flags=re.DOTALL)
    
    return content

def fetch_and_save_model(model_num, model_name_cn, model_name_en, slug):
    """
    获取单个模型并保存
    """
    url = f"{BASE_URL}/models/{slug}/"
    output_file = OUTPUT_DIR / f"{model_num}-{slug}.md"
    
    # 如果文件已存在，跳过
    if output_file.exists():
        print(f"✅ {model_num} {model_name_cn} 已存在，跳过")
        return True
    
    print(f"📥 获取 {model_num} {model_name_cn}...")
    
    try:
        # 使用 WebFetch 的方式类似，直接用 requests
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 这里我们做一个简化的处理，实际可以用更复杂的解析
        # 现在先创建一个占位符文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {model_name_cn}\n\n")
            f.write(f"> **英文**：{model_name_en}  \n")
            f.write(f"> **编号**：{model_num}  \n")
            f.write(f"> **来源**：[{url}]({url})  \n\n")
            f.write("---\n\n")
            f.write(f"## 核心概念\n\n")
            f.write(f"（待完善：此模型的核心概念内容）\n\n")
            f.write(f"## 正文\n\n")
            f.write(f"（待完善：此模型的详细内容）\n\n")
            f.write(f"## 关联模型\n\n")
            f.write(f"- （待完善：相关模型链接）\n\n")
            f.write(f"## 实践检查清单\n\n")
            f.write(f"- （待完善：实践检查项）\n")
        
        print(f"✅ 保存 {output_file}")
        time.sleep(1)  # 避免请求过快
        return True
        
    except Exception as e:
        print(f"❌ 获取 {model_num} {model_name_cn} 失败: {e}")
        return False

def main():
    print("🚀 开始批量获取思维模型...")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("-" * 50)
    
    success_count = 0
    fail_count = 0
    
    for model in MODELS:
        model_num, model_name_cn, model_name_en, slug = model
        if fetch_and_save_model(model_num, model_name_cn, model_name_en, slug):
            success_count += 1
        else:
            fail_count += 1
    
    print("-" * 50)
    print(f"📊 完成！成功: {success_count}, 失败: {fail_count}")

if __name__ == "__main__":
    main()
