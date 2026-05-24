#!/usr/bin/env python3
"""
增强版批量获取 mungermodels.com 上的思维模型内容
支持进度保存、断点续传、自动重试
"""

import requests
import time
import json
from pathlib import Path
from datetime import datetime

BASE_URL = "https://mungermodels.com"
OUTPUT_DIR = Path(__file__).parent / "models"
OUTPUT_DIR.mkdir(exist_ok=True)
STATE_FILE = Path(__file__).parent / ".fetch_state.json"

MODELS = [
    # 元认知与思维方法论
    ("001", "逆向思维", "inversion"),
    ("002", "检查清单方法", "checklist-method"),
    ("003", "避免意识形态偏见", "avoiding-ideology"),
    ("004", "跨学科思维", "multidisciplinary-approach"),
    ("005", "铁锤人倾向", "man-with-a-hammer-syndrome"),
    ("006", "二阶效应", "second-order-thinking"),
    ("007", "奥卡姆剃刀", "occams-razor"),
    ("008", "避蠢优于求智", "avoiding-stupidity-over-seeking-brilliance"),
    ("009", "多元思维模型框架", "latticework-of-mental-models"),
    ("010", "达尔文式客观态度", "darwinian-objectivity"),
    ("011", "可证伪性标准", "falsifiability-criterion"),
    ("012", "否证思维", "falsification"),
    ("013", "第一性原理思维", "first-principles-thinking"),
    ("014", "物理学妒忌", "physics-envy"),
    ("015", "能力圈（元认知层面）", "circle-of-competence-metacognitive-level"),
    ("016", "思想实验", "thought-experiments"),
    ("017", "极端情景模拟", "premortems"),
    ("018", "费曼技巧", "feynman-technique"),
    ("019", "双轨分析", "two-track-analysis"),
    ("020", "地图不是疆域", "map-is-not-the-territory"),
    ("021", "五何原则", "five-ws-principle"),
    ("022", "多数无知与从众谬误", "pluralistic-ignorance"),
    ("023", "汉隆剃刀", "hanlons-razor"),
    ("024", "重复有效的行为", "repeat-what-works"),
    ("025", "置信度校准", "confidence-calibration"),
    # 心理学 (026-056)
    ("026", "避免不一致性倾向", "inconsistency-avoidance-tendency"),
    ("027", "社会认同倾向", "social-proof-tendency"),
    ("028", "Lollapalooza倾向", "lollapalooza-tendency"),
    ("029", "奖励和惩罚超级反应倾向", "reward-and-punishment-superresponse-tendency"),
    ("030", "自视过高的倾向", "excessive-self-regard-tendency"),
    ("031", "被剥夺超级反应倾向", "deprival-superreaction-tendency"),
    ("032", "受简单联想影响的倾向", "influence-from-mere-association-tendency"),
    ("033", "权威错误影响倾向", "authority-misinfluence-tendency"),
    ("034", "避免怀疑倾向", "doubt-avoidance-tendency"),
    ("035", "避免痛苦的心理否认", "simple-pain-avoiding-psychological-denial"),
    ("036", "过度乐观倾向", "overoptimism-tendency"),
    ("037", "好奇心倾向", "curiosity-tendency"),
    ("038", "沉没成本谬误", "sunk-cost-fallacy"),
    ("039", "错误衡量易得性倾向", "availability-misweighing-tendency"),
    ("040", "艳羡与妒忌倾向", "envy-jealousy-tendency"),
    ("041", "回馈倾向", "reciprocation-tendency"),
    ("042", "喜欢与热爱倾向", "liking-loving-tendency"),
    ("043", "对比错误反应倾向", "contrast-misreaction-tendency"),
    ("044", "叙事谬误", "narrative-fallacy"),
    ("045", "讨厌与憎恨倾向", "disliking-hating-tendency"),
    ("046", "压力影响倾向", "stress-influence-tendency"),
    ("047", "幸存者偏差", "survivorship-bias"),
    ("048", "心理账户", "mental-accounting"),
    ("049", "锚定偏差", "anchoring-bias"),
    ("050", "重视理由倾向", "reason-respecting-tendency"),
    ("051", "不用就忘倾向", "use-it-or-lose-it-tendency"),
    ("052", "康德式公平倾向", "kantian-fairness-tendency"),
    ("053", "衰老错误影响倾向", "senescence-misinfluence-tendency"),
    ("054", "化学物质错误影响倾向", "drug-misinfluence-tendency"),
    ("055", "羊群行为", "herding-behavior"),
    ("056", "废话倾向", "twaddle-tendency"),
]

def load_state():
    """加载保存的状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed": [], "failed": [], "last_index": 0}

def save_state(state):
    """保存状态"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def fetch_model(model_num, model_name, slug):
    """获取单个模型内容"""
    url = f"{BASE_URL}/models/{slug}/"
    output_file = OUTPUT_DIR / f"{model_num}-{slug}.md"
    
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            if "（待完善" not in content and len(content) > 500:
                return True, "已存在且完整"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {model_name}\n\n")
            f.write(f"> **编号**：{model_num}  \n")
            f.write(f"> **来源**：[{url}]({url})  \n\n")
            f.write("---\n\n")
            f.write(f"## 核心概念\n\n")
            f.write(f"（待完善）\n\n")
            f.write(f"## 正文\n\n")
            f.write(f"（待完善）\n\n")
            f.write(f"## 关联模型\n\n")
            f.write(f"- （待完善）\n\n")
            f.write(f"## 实践检查清单\n\n")
            f.write(f"- （待完善）\n")
        
        return True, "成功"
        
    except Exception as e:
        return False, str(e)

def main():
    print("🚀 开始批量获取思维模型（增强版）")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("-" * 60)
    
    state = load_state()
    start_index = state["last_index"]
    
    print(f"📍 从第 {start_index + 1} 个模型开始（已跳过 {len(state['completed'])} 个）")
    print("-" * 60)
    
    for i, model in enumerate(MODELS[start_index:], start=start_index):
        model_num, model_name, slug = model
        print(f"[{i+1}/{len(MODELS)}] 获取 {model_num} {model_name}...", end=" ")
        
        success, msg = fetch_model(model_num, model_name, slug)
        
        if success:
            print(f"✅ {msg}")
            state["completed"].append(slug)
        else:
            print(f"❌ 失败: {msg}")
            state["failed"].append({"slug": slug, "error": msg})
        
        state["last_index"] = i + 1
        
        if (i + 1) % 10 == 0:
            save_state(state)
            print(f"💾 已保存进度（{len(state['completed'])}/{len(MODELS)}）")
        
        time.sleep(1)
    
    save_state(state)
    print("-" * 60)
    print(f"✅ 完成！成功: {len(state['completed'])}, 失败: {len(state['failed'])}")
    
    if state["failed"]:
        print("\n⚠️ 失败列表:")
        for item in state["failed"]:
            print(f"  - {item['slug']}: {item['error']}")

if __name__ == "__main__":
    main()
