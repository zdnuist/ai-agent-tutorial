# 09 - GitHub Bounty 实战：用技术赚钱

> **AI Agent 开发教程 第 09 课**  
> 📅 2026 年 3 月 | 👨‍💻 [@Gale2World](https://github.com/zdnuist)

---

## 📋 课程目标

学完本课后，你将能够：
- ✅ 了解 GitHub Bounty 赚钱模式
- ✅ 掌握任务筛选技巧
- ✅ 学会高效完成任务
- ✅ 建立个人品牌

---

## 一、什么是 GitHub Bounty？

### 1.1 定义

**GitHub Bounty** = 项目方悬赏 + 开发者接单 + 完成获酬

```
项目方发布任务 → 开发者认领 → 提交 PR → 审核通过 → 获得奖励
```

### 1.2 收入潜力

| 任务类型 | 奖励范围 | 耗时 | 时薪 |
|---------|---------|------|------|
| 文档修复 | $30-100 | 1-2h | $30-50/h |
| Bug 修复 | $50-200 | 2-4h | $25-50/h |
| 功能开发 | $100-500 | 4-8h | $25-60/h |
| 安全漏洞 | $200-2000 | 8-20h | $25-100/h |

### 1.3 主要平台

| 平台 | 特点 | 链接 |
|------|------|------|
| **Gitcoin** | 专注开源项目 | gitcoin.co |
| **GitHub Sponsors** | 官方赞助 | github.com/sponsors |
| **IssueHunt** | Issue 悬赏 | issuehunt.io |
| **Bountysource** | 老牌平台 | bountysource.com |

---

## 二、准备工作

### 2.1 技能准备

```
必备技能：
✅ Git 版本控制
✅ 至少一门编程语言（Python/JS/Go）
✅ 英语阅读能力
✅ 沟通能力

加分技能：
⭐ 项目经验丰富
⭐ 有开源贡献记录
⭐ 特定领域专业知识
```

### 2.2 账号准备

```bash
# 1. GitHub 账号
- 完善个人资料
- 上传头像
- 填写 Bio

# 2. Gitcoin 账号
- 连接 GitHub
- 完成身份验证
- 绑定收款方式

# 3. 收款方式
- PayPal（最常用）
- 银行转账
- 加密货币（USDC）
```

### 2.3 环境配置

```python
# requirements.txt
# 开发环境
pytest==7.4.0
black==23.7.0
flake8==6.1.0
pre-commit==3.3.3

# Git 配置
# ~/.gitconfig
[user]
    name = Your Name
    email = your@email.com
```

---

## 三、任务筛选

### 3.1 筛选标准

```python
def should_apply(issue: Dict) -> bool:
    """判断是否应该申请任务"""
    
    # 必须满足的条件
    checks = {
        "stars": issue["repo_stars"] > 100,
        "recent_activity": issue["last_commit"] < 90,  # 天内
        "clear_description": len(issue["description"]) > 50,
        "acceptance_criteria": "acceptance" in issue["description"].lower(),
        "bounty_amount": issue["bounty"] >= 50,
        "competitors": issue["claimants"] < 5,
        "maintainer_response": issue["maintainer_response_rate"] > 0.5
    }
    
    return all(checks.values())
```

### 3.2 优先级评分

```python
def calculate_priority(issue: Dict) -> float:
    """计算任务优先级"""
    
    score = 0
    
    # 奖励金额（0-30 分）
    score += min(issue["bounty"] / 10, 30)
    
    # 项目活跃度（0-25 分）
    score += min(issue["repo_stars"] / 100, 25)
    
    # 竞争程度（0-20 分）
    score += max(20 - issue["claimants"] * 4, 0)
    
    # 技术匹配度（0-25 分）
    score += calculate_tech_match(issue["tags"])
    
    return score
```

### 3.3 避免的坑

| 红旗 | 说明 | 风险 |
|------|------|------|
| ❌ 要求先付费 | 诈骗 | 高 |
| ❌ 描述模糊 | 需求不明确 | 高 |
| ❌ 项目废弃 | 无维护者 | 中 |
| ❌ 奖励过高 | 可能是骗局 | 中 |
| ❌ 要求版权转让 | 失去代码所有权 | 低 |

---

## 四、任务执行

### 4.1 标准流程

```
1. 认领任务
   ↓
2. Fork 仓库
   ↓
3. 创建分支
   ↓
4. 开发实现
   ↓
5. 本地测试
   ↓
6. 提交 PR
   ↓
7. 回应审查
   ↓
8. 合并收款
```

### 4.2 沟通技巧

#### 认领时的评论

```markdown
Hi @maintainer,

I'm interested in working on this issue. 

**My approach:**
1. First, I'll reproduce the bug locally
2. Then identify the root cause
3. Implement a fix with tests
4. Submit a PR for review

**Timeline:** I can complete this within 3-5 days.

**Relevant experience:**
- Fixed similar issues in [project link]
- Contributed to [related projects]

Please let me know if you have any questions!
```

#### 进度更新

```markdown
Update: Day 2

✅ Completed:
- Reproduced the issue
- Identified root cause in module X

🔄 In progress:
- Implementing the fix

⏭️ Next:
- Add unit tests
- Update documentation

Expected completion: Tomorrow EOD
```

### 4.3 PR 质量

```markdown
## PR 模板

### Description
Fixes #123

### Changes
- Fixed bug in `module.py`
- Added unit tests
- Updated documentation

### Testing
- [x] Local tests pass
- [x] No breaking changes
- [x] Code follows style guide

### Screenshots
(If applicable)
```

---

## 五、实战案例

### 5.1 文档修复（$50）

```
任务：修复项目 README 中的错误链接
耗时：30 分钟
实际时薪：$100/h

步骤：
1. 发现链接指向 404
2. 找到正确链接
3. 提交 PR
4. 合并收款
```

### 5.2 Bug 修复（$150）

```
任务：修复登录功能的边界条件 bug
耗时：3 小时
实际时薪：$50/h

步骤：
1. 复现问题
2. 定位代码
3. 编写修复
4. 添加测试
5. 通过审查
```

### 5.3 功能开发（$400）

```
任务：实现 API 速率限制功能
耗时：8 小时
实际时薪：$50/h

步骤：
1. 理解需求
2. 设计方案
3. 实现功能
4. 完整测试
5. 文档更新
```

---

## 六、收入优化

### 6.1 策略建议

| 策略 | 说明 | 效果 |
|------|------|------|
| **专注领域** | 深耕特定技术栈 | 提高效率 |
| **建立关系** | 与维护者保持良好关系 | 更多机会 |
| **质量保证** | 每次都超出预期 | 口碑传播 |
| **快速响应** | 及时回复审查意见 | 加快合并 |

### 6.2 收入目标

```
第 1 个月：$200-500（熟悉流程）
第 2 个月：$500-1000（建立信誉）
第 3 个月：$1000-2000（稳定收入）
6 个月后：$2000+（长期合作）
```

### 6.3 税务处理

```python
# 收入记录
income_record = {
    "date": "2026-03-15",
    "platform": "Gitcoin",
    "project": "project-name",
    "amount": 150,
    "currency": "USD",
    "task_id": "#123",
    "tax_category": "freelance"
}
```

---

## 七、工具推荐

### 7.1 监控工具

```python
# Bounty 监控脚本
def monitor_bounties():
    """监控新任务"""
    
    # 使用 GitHub API
    issues = github.search_issues(
        q="label:bounty is:open",
        sort="created",
        order="desc"
    )
    
    for issue in issues:
        if should_apply(issue):
            send_notification(issue)
```

### 7.2 时间追踪

```python
# 时间记录
time_log = {
    "task_id": "#123",
    "date": "2026-03-15",
    "activity": "development",
    "duration_minutes": 180,
    "description": "Implemented feature X"
}
```

---

## 八、常见问题

### Q1: 新手如何开始？

**A:** 从文档修复开始，建立贡献记录

### Q2: PR 被拒怎么办？

**A:** 虚心接受反馈，修改后重新提交

### Q3: 遇到诈骗怎么办？

**A:** 使用正规平台，不提前付费

---

## 📝 课后作业

1. 注册 Gitcoin 账号
2. 找到 3 个合适的任务
3. 完成第一个 PR 提交
4. 记录时间和收入

---

## 🔗 参考资料

- [Gitcoin](https://gitcoin.co)
- [GitHub Sponsors](https://github.com/sponsors)
- [开源贡献指南](https://opensource.guide)

---

**下一课：** [10 - 外包接单指南](10_freelance_guide.md)
