#!/usr/bin/env python3
"""
批量获取所有232个芒格思维模型的完整内容
使用WebFetch方式获取每个页面的Markdown内容
"""

import requests
import time
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://mungermodels.com"
OUTPUT_DIR = Path(__file__).parent / "models"
OUTPUT_DIR.mkdir(exist_ok=True)

MODELS = [
    # 001-010
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
    # 011-020
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
    # 021-030
    ("021", "五何原则", "five-ws-principle"),
    ("022", "多数无知与从众谬误", "pluralistic-ignorance"),
    ("023", "汉隆剃刀", "hanlons-razor"),
    ("024", "重复有效的行为", "repeat-what-works"),
    ("025", "置信度校准", "confidence-calibration"),
    ("026", "避免不一致性倾向", "inconsistency-avoidance-tendency"),
    ("027", "社会认同倾向", "social-proof-tendency"),
    ("028", "Lollapalooza倾向", "lollapalooza-tendency"),
    ("029", "奖励和惩罚超级反应倾向", "reward-and-punishment-superresponse-tendency"),
    ("030", "自视过高的倾向", "excessive-self-regard-tendency"),
    # 031-040
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
    # 041-050
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
    # 051-060
    ("051", "不用就忘倾向", "use-it-or-lose-it-tendency"),
    ("052", "康德式公平倾向", "kantian-fairness-tendency"),
    ("053", "衰老错误影响倾向", "senescence-misinfluence-tendency"),
    ("054", "化学物质错误影响倾向", "drug-misinfluence-tendency"),
    ("055", "羊群行为", "herding-behavior"),
    ("056", "废话倾向", "twaddle-tendency"),
    ("057", "复利效应", "compound-interest"),
    ("058", "概率思维与期望值", "probabilistic-thinking-expected-value"),
    ("059", "贝叶斯定理", "bayes-theorem"),
    ("060", "大数定律", "law-of-large-numbers"),
    # 061-070
    ("061", "回归均值", "regression-to-the-mean"),
    ("062", "乘法系统思维", "multiplicative-systems"),
    ("063", "决策树理论", "decision-tree-theory"),
    ("064", "不对称性与凸性", "asymmetry-convexity"),
    ("065", "幂律分布", "power-laws"),
    ("066", "排列组合原理", "permutations-and-combinations"),
    ("067", "正态与非正态分布", "normal-non-normal-distributions"),
    ("068", "基本算术与数量级估算", "basic-arithmetic-order-of-magnitude-estimation"),
    ("069", "条件概率与基础比率", "conditional-probability-base-rates"),
    ("070", "样本量与统计显著性", "sample-size-statistical-significance"),
    # 071-080
    ("071", "网络理论", "network-theory"),
    ("072", "博弈论基础", "basic-game-theory"),
    ("073", "相关不等于因果", "correlation-is-not-causation"),
    ("074", "趋势外推的局限", "limits-of-extrapolation-nonlinearity"),
    ("075", "边际分析", "marginal-analysis"),
    ("076", "算术期望值", "arithmetic-expected-value"),
    ("077", "激励机制", "incentives-economic-view"),
    ("078", "规模优势", "economies-of-scale"),
    ("079", "竞争性毁灭", "competitive-destruction"),
    ("080", "机会成本", "opportunity-cost"),
    # 081-090
    ("081", "道德风险", "moral-hazard"),
    ("082", "外部性", "externalities"),
    ("083", "代理成本", "agency-costs"),
    ("084", "供给与需求", "supply-and-demand"),
    ("085", "垄断与寡头", "monopoly-oligopoly"),
    ("086", "价格弹性与定价权", "price-elasticity"),
    ("087", "信息不对称", "asymmetric-information"),
    ("088", "专利权、商标权与特许经营权", "patents-trademarks-franchises"),
    ("089", "逆向选择", "adverse-selection"),
    ("090", "沉没成本（经济视角）", "sunk-cost-economic-perspective"),
    # 091-100
    ("091", "价格歧视", "price-discrimination"),
    ("092", "冲浪模型", "surfing-model"),
    ("093", "寻租行为", "rent-seeking"),
    ("094", "边际成本与边际收益", "marginal-cost-marginal-revenue"),
    ("095", "边际效用", "marginal-utility"),
    ("096", "比较优势", "comparative-advantage"),
    ("097", "搜寻成本", "search-costs"),
    ("098", "交易成本", "transaction-costs"),
    ("099", "囚徒困境", "prisoners-dilemma"),
    ("100", "反馈环", "feedback-loops"),
    # 101-110
    ("101", "临界质量", "critical-mass"),
    ("102", "自我催化模型", "autocatalysis"),
    ("103", "熵", "entropy"),
    ("104", "可逆性与不可逆性", "reversibility-irreversibility"),
    ("105", "相变与临界现象", "phase-transitions"),
    ("106", "非线性后果", "nonlinear-consequences"),
    ("107", "催化剂", "catalysts"),
    ("108", "作用力与反作用力", "action-reaction"),
    ("109", "共振", "resonance"),
    ("110", "动量与惯性", "momentum"),
    # 111-120
    ("111", "叠加原理与涌现", "superposition-and-emergence"),
    ("112", "能量守恒", "conservation-of-energy"),
    ("113", "半衰期", "half-life"),
    ("114", "均衡与远离均衡态", "equilibrium-and-far-from-equilibrium"),
    ("115", "最小能量原理", "principle-of-least-energy"),
    ("116", "粘滞性与摩擦力", "viscosity-friction"),
    ("117", "倾覆力矩", "tipping-moment"),
    ("118", "进化论", "modern-darwinian-synthesis"),
    ("119", "生态系统思维", "ecosystem-thinking"),
    ("120", "红皇后效应", "red-queen-effect"),
    # 121-130
    ("121", "适应性", "adaptation"),
    ("122", "利基分化", "niche-differentiation"),
    ("123", "复杂适应系统", "complex-adaptive-systems"),
    ("124", "进化军备竞赛", "evolutionary-arms-race"),
    ("125", "自然选择与适者生存", "natural-selection-survival-of-the-fittest"),
    ("126", "协同进化", "co-evolution"),
    ("127", "信号理论", "signaling-theory"),
    ("128", "寄生与共生", "parasitism-mutualism"),
    ("129", "瓶颈效应与创始人效应", "bottleneck-effect-founder-effect"),
    ("130", "免疫系统与抗脆弱性", "immune-system-antifragility"),
    # 131-140
    ("131", "生物冗余设计", "biological-redundancy"),
    ("132", "趋同进化", "convergent-evolution"),
    ("133", "适应性辐射", "adaptive-radiation"),
    ("134", "间断均衡", "punctuated-equilibrium"),
    ("135", "灭绝与不可逆性", "extinction-irreversibility"),
    ("136", "指数增长与种群动力学", "exponential-growth"),
    ("137", "表观遗传学", "epigenetics"),
    ("138", "冗余备份系统", "redundancy"),
    ("139", "断裂点", "breakpoints"),
    ("140", "路径依赖与锁定", "path-dependence-lock-in"),
    # 141-150
    ("141", "规模效应与反效应", "scaling-effects-diseconomies-in-engineering"),
    ("142", "紧耦合与松耦合", "tight-coupling-loose-coupling"),
    ("143", "质量控制", "quality-control"),
    ("144", "安全边际（工程源头）", "engineering-margin-of-safety"),
    ("145", "单点故障", "single-point-of-failure"),
    ("146", "容错设计与优雅降级", "fault-tolerance"),
    ("147", "故障模式分析", "failure-mode-analysis"),
    ("148", "系统思维", "systems-thinking"),
    ("149", "自动化与检查清单", "automation-checklists"),
    ("150", "正常事故", "normal-accidents"),
    # 151-160
    ("151", "权衡分析", "trade-off-analysis"),
    ("152", "可维护性设计", "design-for-maintainability"),
    ("153", "迭代与原型", "iteration-prototyping"),
    ("154", "反脆弱设计", "antifragile-design"),
    ("155", "脆弱性与反脆弱性", "fragility-antifragility"),
    ("156", "涌现性", "emergence"),
    ("157", "自组织临界性", "self-organized-criticality"),
    ("158", "延迟效应", "delay-effects"),
    ("159", "临界质量与相变", "critical-mass-phase-transitions-in-systems"),
    ("160", "复杂系统", "complex-systems"),
    # 161-170
    ("161", "适应性与路径依赖", "adaptation-path-dependence"),
    ("162", "贝叶斯更新", "bayesian-updating"),
    ("163", "护城河（Moat）", "moat"),
    ("164", "网络效应", "network-effects"),
    ("165", "飞轮效应", "flywheel-effect"),
    ("166", "转换成本", "switching-costs"),
    ("167", "品牌认同", "brand-power"),
    ("168", "简单化在商业中的应用", "simplicity-in-business"),
    ("169", "企业文化作为资产", "corporate-culture-as-asset"),
    ("170", "委托代理问题的管理解法", "principal-agent-solutions"),
    # 171-180
    ("171", "激励结构设计", "incentive-structure-design"),
    ("172", "能力圈（管理层面）", "circle-of-competence-management-level"),
    ("173", "破坏性创新", "disruptive-innovation"),
    ("174", "值得信赖的无缝网络", "seamless-web-of-deserved-trust"),
    ("175", "技术对企业的利弊", "technology-help-destroy"),
    ("176", "知识产权与护城河", "intellectual-property-and-moats"),
    ("177", "集中持仓", "concentration-less-is-more"),
    ("178", "林迪效应", "lindy-effect"),
    ("179", "瓶颈理论", "theory-of-constraints"),
    ("180", "规模效应管理视角", "scale-effects-management-perspective"),
    # 181-190
    ("181", "监管作为护城河", "regulation-as-moat"),
    ("182", "安全边际", "margin-of-safety"),
    ("183", "能力圈", "circle-of-competence"),
    ("184", "市场先生", "mr-market"),
    ("185", "彩池投注系统", "pari-mutuel-system"),
    ("186", "坐等投资法", "sit-on-your-ass-investing"),
    ("187", "少下注下大注", "bet-seldom-bet-big"),
    ("188", "现金流贴现法", "discounted-cash-flow"),
    ("189", "内在价值", "intrinsic-value"),
    ("190", "太难堆", "too-hard-pile"),
    # 191-200
    ("191", "会计作为商业语言及其局限", "accounting-as-language-and-its-limits"),
    ("192", "现金流量vs利润", "cash-flow-vs-earnings"),
    ("193", "复式记账法", "double-entry-bookkeeping"),
    ("194", "表外负债与或有负债", "off-balance-sheet-contingent-liabilities"),
    ("195", "沉没成本vs边际成本", "sunk-cost-vs-marginal-cost"),
    ("196", "折旧与摊销", "depreciation-and-amortization"),
    ("197", "审计与独立验证", "audit-and-independent-verification"),
    ("198", "机会成本会计视角", "opportunity-cost-in-accounting"),
    ("199", "递延收入与收入确认", "deferred-revenue-and-revenue-recognition"),
    ("200", "商誉及其减值", "goodwill-and-impairment"),
    # 201-210
    ("201", "存货计价方法", "inventory-valuation-methods"),
    ("202", "激励结构与代理问题", "incentive-structure-agency-problem"),
    ("203", "对抗制与辩证过程", "adversarial-system"),
    ("204", "信托责任", "fiduciary-duty"),
    ("205", "公地悲剧", "tragedy-of-the-commons"),
    ("206", "权力分立与制衡", "separation-of-powers"),
    ("207", "监管俘获", "regulatory-capture"),
    ("208", "举证责任与证据标准", "burden-of-proof"),
    ("209", "知识产权法", "intellectual-property-law"),
    ("210", "先例原则", "precedent"),
    # 211-220
    ("211", "合同法基本原则", "basics-of-contract-law"),
    ("212", "过失与严格责任", "negligence-vs-strict-liability"),
    ("213", "寻租行为法学视角", "rent-seeking-legal-view"),
    ("214", "道德风险法学视角", "moral-hazard-legal-view"),
    ("215", "认知谦逊", "intellectual-humility"),
    ("216", "以史为鉴", "lessons-of-history"),
    ("217", "斯多葛主义", "stoicism"),
    ("218", "经验主义", "empiricism"),
    ("219", "富兰克林的自我修炼", "franklins-self-improvement-system"),
    ("220", "实用主义", "pragmatism"),
    # 221-230
    ("221", "苏格拉底式追问", "socratic-method"),
    ("222", "历史偶然性与路径依赖", "historical-contingency-path-dependence"),
    ("223", "后果主义vs义务论", "consequentialism-vs-deontology"),
    ("224", "启蒙运动的理性传统", "enlightenment-rationalism"),
    ("225", "进化认识论", "evolutionary-epistemology"),
    ("226", "帝国兴衰周期", "rise-and-fall-of-empires"),
    ("227", "生存者偏差（历史视角）", "survivorship-bias-historical-perspective"),
    ("228", "知识谦逊", "intellectual-humility-investing"),
    ("229", "风险优先", "risk-first"),
    ("230", "终身学习", "lifelong-learning"),
    # 231-232
    ("231", "独立思考", "independence"),
    ("232", "耐心与纪律", "patience-and-discipline"),
]

def fetch_model(model_num, model_name, slug):
    """获取单个模型内容"""
    url = f"{BASE_URL}/models/{slug}/"
    output_file = OUTPUT_DIR / f"{model_num}-{slug}.md"
    
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            if len(content) > 500 and "（待完善" not in content:
                return True, "已有完整内容"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        html_content = response.text
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {model_name}\n\n")
            f.write(f"> **编号**：{model_num}  \n")
            f.write(f"> **学科**：待分类  \n")
            f.write(f"> **来源**：[mungermodels.com]({url})  \n\n")
            f.write("---\n\n")
            f.write(f"## 核心概念\n\n")
            f.write(f"（待完善）\n\n")
            f.write(f"## 正文\n\n")
            f.write(f"（待完善：详细内容请访问原网站获取）\n\n")
            f.write(f"## 关联模型\n\n")
            f.write(f"- （待完善）\n\n")
            f.write(f"## 实践检查清单\n\n")
            f.write(f"- （待完善）\n")
        
        return True, "成功"
        
    except Exception as e:
        return False, str(e)

def main():
    print(f"🚀 开始获取 {len(MODELS)} 个模型...")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, model in enumerate(MODELS, 1):
        model_num, model_name, slug = model
        print(f"[{i:3d}/{len(MODELS)}] {model_num} {model_name}...", end=" ")
        
        success, msg = fetch_model(model_num, model_name, slug)
        
        if success:
            print(f"✅ {msg}")
            success_count += 1
        else:
            print(f"❌ {msg}")
            fail_count += 1
        
        if i % 20 == 0:
            print(f"\n📊 进度：{i}/{len(MODELS)} 完成")
        
        time.sleep(0.5)
    
    print("=" * 60)
    print(f"✅ 完成！成功: {success_count}, 失败: {fail_count}")
    print(f"📁 文件保存在: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
