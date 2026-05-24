#!/usr/bin/env python3
"""
并发批量获取所有芒格思维模型
使用线程池并发请求以提高效率
"""

import requests
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://mungermodels.com"
OUTPUT_DIR = Path(__file__).parent / "models"
OUTPUT_DIR.mkdir(exist_ok=True)

MODELS_TO_FETCH = [
    ("003", "避免意识形态偏见", "avoiding-ideology"),
    ("004", "跨学科思维", "multidisciplinary-approach"),
    ("005", "铁锤人倾向", "man-with-a-hammer-syndrome"),
    ("006", "二阶效应", "second-order-thinking"),
    ("007", "奥卡姆剃刀", "occams-razor"),
    ("008", "避蠢优于求智", "avoiding-stupidity-over-seeking-brilliance"),
    ("009", "多元思维模型框架", "latticework-of-mental-models"),
    ("010", "达尔文式客观态度", "darwinian-objectivity"),
    ("026", "避免不一致性倾向", "inconsistency-avoidance-tendency"),
    ("027", "社会认同倾向", "social-proof-tendency"),
    ("028", "Lollapalooza倾向", "lollapalooza-tendency"),
    ("029", "奖励和惩罚超级反应倾向", "reward-and-punishment-superresponse-tendency"),
    ("030", "自视过高的倾向", "excessive-self-regard-tendency"),
    ("057", "复利效应", "compound-interest"),
    ("058", "概率思维与期望值", "probabilistic-thinking-expected-value"),
    ("059", "贝叶斯定理", "bayes-theorem"),
    ("077", "激励机制", "incentives-economic-view"),
    ("078", "规模优势", "economies-of-scale"),
    ("079", "竞争性毁灭", "competitive-destruction"),
    ("080", "机会成本", "opportunity-cost"),
    ("100", "反馈环", "feedback-loops"),
    ("101", "临界质量", "critical-mass"),
    ("118", "进化论", "modern-darwinian-synthesis"),
    ("119", "生态系统思维", "ecosystem-thinking"),
    ("138", "冗余备份系统", "redundancy"),
    ("139", "断裂点", "breakpoints"),
    ("148", "系统思维", "systems-thinking"),
    ("155", "脆弱性与反脆弱性", "fragility-antifragility"),
    ("160", "复杂系统", "complex-systems"),
    ("163", "护城河（Moat）", "moat"),
    ("164", "网络效应", "network-effects"),
    ("166", "转换成本", "switching-costs"),
    ("171", "激励结构设计", "incentive-structure-design"),
    ("182", "安全边际", "margin-of-safety"),
    ("183", "能力圈", "circle-of-competence"),
    ("184", "市场先生", "mr-market"),
    ("187", "少下注下大注", "bet-seldom-bet-big"),
    ("189", "内在价值", "intrinsic-value"),
    ("191", "会计作为商业语言及其局限", "accounting-as-language-and-its-limits"),
    ("192", "现金流量vs利润", "cash-flow-vs-earnings"),
    ("202", "激励结构与代理问题", "incentive-structure-agency-problem"),
    ("203", "对抗制与辩证过程", "adversarial-system"),
    ("204", "信托责任", "fiduciary-duty"),
    ("215", "认知谦逊", "intellectual-humility"),
    ("216", "以史为鉴", "lessons-of-history"),
    ("228", "知识谦逊", "intellectual-humility-investing"),
    ("229", "风险优先", "risk-first"),
    ("230", "终身学习", "lifelong-learning"),
    ("231", "独立思考", "independence"),
    ("232", "耐心与纪律", "patience-and-discipline"),
]

def fetch_model(model_num, model_name, slug):
    """获取单个模型"""
    url = f"{BASE_URL}/models/{slug}/"
    output_file = OUTPUT_DIR / f"{model_num}-{slug}.md"
    
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            if len(content) > 500 and "（待完善" not in content:
                return True, "已有完整内容", model_num, model_name
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        html = response.text
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {model_name}\n\n")
            f.write(f"> **编号**：{model_num}  \n")
            f.write(f"> **学科**：待分类  \n")
            f.write(f"> **来源**：[mungermodels.com]({url})  \n\n")
            f.write("---\n\n")
            f.write(f"## 核心概念\n\n")
            f.write(f"（待完善）\n\n")
            f.write(f"## 正文\n\n")
            f.write(f"（待完善）\n\n")
            f.write(f"## 关联模型\n\n")
            f.write(f"- （待完善）\n\n")
            f.write(f"## 实践检查清单\n\n")
            f.write(f"- （待完善）\n")
        
        return True, "成功", model_num, model_name
        
    except Exception as e:
        return False, str(e), model_num, model_name

def main():
    print(f"🚀 并发获取 {len(MODELS_TO_FETCH)} 个高优先级模型...")
    
    results = {"success": [], "failed": []}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_model, m[0], m[1], m[2]): m 
            for m in MODELS_TO_FETCH
        }
        
        for future in as_completed(futures):
            success, msg, num, name = future.result()
            if success:
                print(f"✅ {num} {name}")
                results["success"].append(num)
            else:
                print(f"❌ {num} {name}: {msg}")
                results["failed"].append({"num": num, "name": name, "error": msg})
            
            time.sleep(0.3)
    
    print(f"\n📊 完成！成功: {len(results['success'])}, 失败: {len(results['failed'])}")
    if results["failed"]:
        print("\n失败列表:")
        for item in results["failed"]:
            print(f"  - {item['num']} {item['name']}: {item['error']}")

if __name__ == "__main__":
    main()
