---
title: OpenClaw 分析
date: 2026-06-12T19:10:25+08:00
draft: false
categories:
  - 随记
tags:
  - "#OpenClaw"
---
## 结论先行

**OpenClaw 值得关注，但不建议你现在把它直接当成“主力爬虫/自动化生产工具”。**

更现实的判断是：

- **适合：** 技术爱好者、开发者、本地 Agent 自动化实验、个人工作流自动化、消息入口型助手。
    
- **不适合：** 新手直接接入真实邮箱、真实浏览器、真实文件系统、真实账号、真实钱包、真实生产数据。
    
- **对你当前爬虫学习的价值：** 有参考价值，但不是第一优先级。你现在更应该先把“靶场 → 数据源判断 → 代码生成 → 调试反馈 → 数据校验”这套流程练熟。OpenClaw 属于下一阶段：让 Agent 代替你做更多执行动作。
    

---

# 1. OpenClaw 到底是什么？

OpenClaw 官方定位是一个**自托管的个人 AI 助手 / Agent Gateway**。它不是单纯聊天机器人，而是把 WhatsApp、Telegram、Slack、Discord、iMessage、Signal、Google Chat 等消息入口连接到本地或服务器上的 AI Agent。官方文档明确说，你运行一个 Gateway 进程，它负责连接聊天渠道、会话、路由和 Agent。([OpenClaw](https://docs.openclaw.ai/ "OpenClaw - OpenClaw"))

GitHub README 的说法更直接：OpenClaw 是运行在你自己设备上的个人 AI 助手，可以通过你已有的渠道回复你；Gateway 只是控制平面，真正产品是“助手”。GitHub 页面还显示它支持 WhatsApp、Telegram、Slack、Discord、Google Chat、Signal、iMessage、Microsoft Teams、Matrix、飞书、LINE、微信、QQ、WebChat 等渠道。([GitHub](https://github.com/openclaw/openclaw "GitHub - openclaw/openclaw: Your own personal AI assistant. Any OS. Any Platform. The lobster way.  · GitHub"))

它的核心不是“模型”，而是：

> **消息入口 + Gateway + Agent + 工具权限 + Skills 插件生态 + 本地/远程执行环境。**

---

# 2. 它解决什么问题？

OpenClaw 解决的是：**让 AI 不只回答问题，而是能够在你的授权环境里执行任务。**

官网宣传的典型任务包括：清理邮箱、发送邮件、管理日历、办理航班值机，并且可以从 WhatsApp、Telegram 或其他聊天应用里发起任务。([OpenClaw](https://openclaw.ai/ "OpenClaw — Personal AI Assistant"))

它和普通 ChatGPT 网页最大的区别：

|对比项|ChatGPT 网页|OpenClaw|
|---|---|---|
|核心形态|对话产品|自托管 Agent Gateway|
|执行动作|受平台工具限制|可连接浏览器、文件、命令、消息渠道、插件|
|部署方式|云端 SaaS|本地 / 服务器自托管|
|使用入口|ChatGPT 页面 / App|Telegram、WhatsApp、Slack、Discord、Web UI 等|
|风险水平|相对受控|明显更高，因为涉及本机权限和外部插件|
|适合对象|普通用户|开发者 / 高阶用户 / 自动化实验者|

所以，**OpenClaw 不是“更强版 ChatGPT”，而是一个把模型接到现实执行环境的 Agent 基础设施。**

---

# 3. 技术结构：它大概怎么工作？

官方文档描述的结构是：

1. 用户从聊天软件或 Web UI 发送消息；
    
2. Gateway 接收请求；
    
3. Gateway 管理会话、路由、渠道连接；
    
4. Agent 调用模型、工具、Skills；
    
5. 执行浏览器、文件、命令、消息、API 等动作；
    
6. 结果返回给用户。([OpenClaw](https://docs.openclaw.ai/ "OpenClaw - OpenClaw"))
    

它还支持多 Agent 路由，可以把不同渠道或不同账号绑定到不同 Agent，例如工作 Agent、运维 Agent、个人 Agent。官方 agents 文档说明可以用 bindings 把 Telegram、Discord 等入站流量固定路由到指定 Agent。([OpenClaw](https://docs.openclaw.ai/cli/agents "Agents - OpenClaw"))

浏览器自动化方面，官方文档说 OpenClaw 可以运行一个独立的 Chrome/Brave/Edge/Chromium 浏览器配置文件，Agent 可以打开标签页、读页面、点击、输入，并且这个 `openclaw` profile 与你的个人浏览器 profile 隔离。([OpenClaw](https://docs.openclaw.ai/tools/browser "Browser (OpenClaw-managed) - OpenClaw"))

这对爬虫/数据采集有现实意义：它可以作为“人机协作浏览器执行层”。但注意，它更接近 **RPA + Agent + 浏览器自动化**，不是传统意义上的高性能爬虫框架。

---

# 4. 对你当前“爬虫靶场/Agent+API”方案的价值

## 4.1 有价值的地方

OpenClaw 对你有三个参考价值：

**第一，它证明了 Agent 的现实方向不是“聊天”，而是“工具调用 + 执行环境 + 权限控制”。**  
这和你现在的判断是吻合的：你不需要把所有代码都自己写透，而是要学会控制任务流程、判断数据来源、反馈错误、验收结果。

**第二，它的浏览器工具逻辑值得借鉴。**  
官方浏览器工具强调：先检查状态、标签页、快照；执行前后重新快照；遇到登录、2FA、验证码、摄像头/麦克风阻断时，不要让 Agent 猜，而是交给人工处理。([OpenClaw](https://docs.openclaw.ai/tools/browser "Browser (OpenClaw-managed) - OpenClaw"))  
这正好适合你的训练方向：人负责判断和边界，AI 负责代码与执行建议。

**第三，它说明未来你的“爬虫执行层”可以升级成 Agent。**  
你现在可以先用 ChatGPT 网页 + 本地靶场训练流程。后续如果要自动执行，就可以考虑类似 OpenClaw、browser-use、Playwright MCP、Claude Code/Codex CLI、Dify/Coze/n8n 等方案。

---

## 4.2 不要误判的地方

你现在不应该把 OpenClaw 当成“学爬虫捷径”。

原因很简单：

- 它的安装、配置、权限管理、插件安全、模型调用、消息渠道绑定，都有额外复杂度。
    
- 它会引入比爬虫本身更大的安全风险。
    
- 你当前真正缺的不是“更强工具”，而是稳定的数据源判断、任务拆解、错误反馈、验收标准。
    
- Agent 越强，越需要你具备控制流程和风险判断能力，否则它只是更快地把错误执行出来。
    

现实排序应该是：

1. **先练本地靶场和 ChatGPT 网页协作。**
    
2. 再练 API 模式：Python 脚本 + LLM API 辅助生成/修复。
    
3. 再引入 Agent 执行层。
    
4. 最后才考虑 OpenClaw 这种常驻型、多入口、高权限 Agent Gateway。
    

---

# 5. 最大风险：不是“它能不能用”，而是“它权限太大”

OpenClaw 的强点也是它的风险点。

官方安全文档明确说明，OpenClaw 会把本地会话日志保存在 `~/.openclaw/agents/<agentId>/sessions/*.jsonl`，任何有文件系统访问权的进程或用户都可能读取这些日志；官方建议把磁盘访问视为信任边界，并锁定 `~/.openclaw` 权限。([OpenClaw](https://docs.openclaw.ai/gateway/security "Security - OpenClaw"))

官方安全政策也说得很清楚：OpenClaw 是面向“可信操作员”的 local-first agent infrastructure，不是为多个互相敌对用户共享同一个 Gateway 而设计的安全边界。([GitHub](https://github.com/openclaw/openclaw/security "Overview · openclaw/openclaw · GitHub"))

第三方安全报道已经发现过恶意 Skill 问题。Tom's Hardware 报道称，2026 年 1 月 27 日至 29 日，至少 14 个恶意 Skills 被上传到 ClawHub，伪装成加密交易或钱包自动化工具，诱导用户运行混淆命令，目标包括浏览器数据和加密钱包信息。([Tom's Hardware](https://www.tomshardware.com/tech-industry/cyber-security/malicious-moltbot-skill-targets-crypto-users-on-clawhub "Malicious OpenClaw ‘skill’ targets crypto users on ClawHub — 14 malicious skills were uploaded to ClawHub last month | Tom's Hardware"))

1Password 的安全分析指出，Agent Skills 的 markdown 本体没有限制，Skill 可以包含指令、脚本和资源；恶意 Skill 可以通过社工、shell 指令或捆绑代码绕过 MCP 工具边界。([1password.com](https://1password.com/blog/from-magic-to-malware-how-openclaws-agent-skills-become-an-attack-surface "From magic to malware: How OpenClaw's agent skills become an attack surface | 1Password"))

这意味着：**只要你给它浏览器、文件、命令行、邮箱、日历、API Token，它就变成一个高价值攻击面。**

---

# 6. 谁获利、谁付成本、谁承担失败风险？

按现实利益拆解：

|角色|获利方式|承担成本/风险|
|---|---|---|
|OpenClaw 项目|社区影响力、生态扩张、潜在商业化|安全事故、维护压力、信任损耗|
|Skill 开发者|流量、声誉、服务转化、潜在收费|质量责任不清|
|用户|自动化效率、本地控制、多渠道入口|配置成本、安全风险、误操作损失|
|攻击者|利用高权限 Agent 窃取数据/凭证|成本低，收益高|
|模型/API 提供商|API 消耗、订阅收入|被用户依赖，但不一定承担本地执行风险|

最关键的一点：

> **用户是最终风险承担者。**

如果 Agent 误删文件、泄露邮箱、执行恶意命令、把 API Key 暴露出去，损失主要由用户承担。开源项目、Skill 作者、模型服务商通常不会替你兜底。

---

# 7. 商业模式粗拆

OpenClaw 本体更像开源基础设施项目，而不是传统 SaaS。

|模块|判断|
|---|---|
|客户细分|开发者、高阶用户、自动化爱好者、小团队、需要自托管 AI 助手的人|
|价值主张|本地控制、多渠道入口、Agent 常驻执行、开放插件生态|
|渠道|GitHub、官网、文档、社区、Discord、开发者传播|
|收入来源|当前公开信息更偏开源生态；是否存在稳定商业收费模式，需要进一步验证|
|核心资源|GitHub 社区、Gateway 架构、Skills 生态、浏览器/消息/工具集成|
|关键业务|开源维护、插件生态、安全治理、跨平台适配、开发者社区运营|
|成本结构|工程维护、安全响应、生态审核、文档、社区支持、基础设施|
|护城河|先发社区、插件生态、多渠道集成、开发者心智|
|最大风险|安全事故、恶意插件、权限滥用、配置复杂、普通用户误用|

GitHub 页面显示该项目采用 MIT License，并且截至页面抓取时显示约 379k stars、79.3k forks，最新 release 为 `openclaw 2026.6.6`，发布日期为 2026 年 6 月 12 日。这个热度说明社区关注很高，但不能直接等同于稳定、安全或商业可持续。([GitHub](https://github.com/openclaw/openclaw "GitHub - openclaw/openclaw: Your own personal AI assistant. Any OS. Any Platform. The lobster way.  · GitHub"))

---

# 8. 是否适合你现在使用？

## 最优选项：暂不作为主力，只做研究对象

你现在最优策略是：

**把 OpenClaw 当作 Agent 架构研究对象，而不是马上部署进真实生产环境。**

你应该重点研究它的：

- Gateway 思路；
    
- Agent 路由；
    
- browser profile 隔离；
    
- Skills 插件机制；
    
- 安全权限设计；
    
- 人工确认机制；
    
- 日志和会话管理。
    

这对你以后设计“爬虫 Agent 流程”有帮助。

---

## 次优选项：隔离环境小规模试用

如果你确实想试，建议只在隔离环境里试：

- 不接真实邮箱；
    
- 不接真实微信/QQ/Telegram 主号；
    
- 不接真实浏览器 profile；
    
- 不放银行卡、钱包、身份证、API Key；
    
- 不安装第三方 Skill；
    
- 不运行别人给的 `curl | bash`、`powershell -Command`、`npm install` 后自动执行脚本；
    
- 最好用虚拟机 / WSL / Docker / 单独 Windows 用户；
    
- 只让它操作本地靶场、测试账号、测试文件夹。
    

---

## 不推荐选项：直接接入真实个人工作流

不建议你现在这么做：

- 接入 Gmail/Outlook 主邮箱；
    
- 接入真实微信/QQ；
    
- 接入浏览器主 profile；
    
- 给它命令行完整权限；
    
- 装中文社区转载的不明 Skill；
    
- 用它处理财务、账号、密码、简历、身份证、银行卡、借贷信息；
    
- 让它无人值守执行任务。
    

这不是保守，而是风险收益不划算。

---

# 9. 对你当前爬虫方向的具体建议

你当前阶段更应该这样走：

## 第一阶段：继续 ChatGPT 网页 + 本地靶场

目标不是“自动化”，而是训练判断：

- 数据来自 HTML 还是 API；
    
- 是否有分页；
    
- 是否有详情页二次请求；
    
- 是否有登录态；
    
- 是否有 JS 渲染；
    
- 是否需要 Playwright；
    
- 是否需要数据清洗和校验；
    
- 出错时如何反馈证据给 AI。
    

这是你当前真正需要的基本功。

## 第二阶段：Agent + API 半自动化

当你熟悉流程后，再做：

- Python 脚本调用 LLM API；
    
- 让 AI 生成爬虫代码；
    
- 人审查请求、字段、分页、异常；
    
- 本地执行；
    
- 结果入 SQLite；
    
- DBeaver 校验。
    

这个阶段比 OpenClaw 更稳、更可控。

## 第三阶段：浏览器 Agent

再考虑：

- Playwright MCP；
    
- browser-use；
    
- OpenClaw browser tool；
    
- 本地靶场自动点击、登录、采集；
    
- 人工确认关键动作。
    

## 第四阶段：OpenClaw 常驻自动化

最后才考虑：

- 多渠道消息入口；
    
- 定时任务；
    
- 多 Agent 路由；
    
- 自动日报；
    
- 自动采集；
    
- 自动入库；
    
- 自动生成报告。
    

---

# 10. 最终判断

**最确定的结论：**  
OpenClaw 是一个高权限、自托管、多渠道 Agent Gateway，不是普通聊天工具。它的价值在“让 AI 进入执行环境”，而不是模型本身。

**最大优势：**  
它把消息入口、Agent、浏览器、工具、Skills、本地执行环境整合到一起，方向是对的。

**最大风险：**  
权限过大，Skill 生态存在供应链风险。恶意插件、命令执行、浏览器数据、邮箱数据、API Token、会话日志都可能成为攻击面。

**对你是否值得：**  
值得研究，不建议现在重度使用。

**现实建议：**  
你现在先不要急着部署 OpenClaw。先把“ChatGPT 网页 + 本地爬虫靶场 + 人工流程控制”练熟。等你能稳定判断数据源、反馈错误、验收数据，再把 OpenClaw 或类似 Agent 框架作为执行层引入。当前阶段，它更像“未来架构参考”，不是你马上要上的主工具。

---
有。前面是整体判断，下面补充更“落地”的部分。

# 1. OpenClaw 的本质判断要再收紧

**OpenClaw 不是爬虫工具，也不是普通 Agent。它更像一个“个人 Agent 操作系统雏形”：消息入口 + Gateway + 工具权限 + 浏览器控制 + Skills 插件。**

官网直接宣传它可以清理邮箱、发送邮件、管理日历、办理航班值机，并通过 WhatsApp、Telegram 等聊天入口触发任务。这个定位已经不是“问答”，而是“让 AI 代替你操作现实账户和工具”。([OpenClaw](https://openclaw.ai/ "OpenClaw — Personal AI Assistant"))

所以你判断它时，核心问题不是：

> 它强不强？

而是：

> 我是否有能力控制它的权限、边界、错误和安全风险？

目前对你来说，答案是：**可以研究，不应重度接入真实账号。**

---

# 2. 对你最有用的部分是 Browser，不是 Skills

OpenClaw 的浏览器工具比较值得研究。官方文档说它可以运行一个独立的 Chrome/Brave/Edge/Chromium profile，由 Agent 控制；这个 `openclaw` profile 与你的个人浏览器 profile 隔离，Agent 可以打开标签、读页面、点击、输入、截图、导出 PDF。([OpenClaw](https://docs.openclaw.ai/tools/browser "Browser (OpenClaw-managed) - OpenClaw"))

这对你学习爬虫有价值，因为它可以模拟未来的“浏览器 Agent 执行层”。

但注意边界：

|场景|适合 OpenClaw Browser 吗？|判断|
|---|--:|---|
|本地爬虫靶场自动登录、点击、翻页|适合|低风险|
|公开网页信息采集验证|可以|注意网站规则|
|真实账号后台自动操作|谨慎|容易误操作|
|金融、邮箱、网盘、工作账号|不建议|损失不可控|
|高并发采集|不适合|它不是 Scrapy/分布式采集框架|

你的阶段应该先拿它看“Agent 如何控制浏览器”，而不是拿它直接跑真实采集任务。

---

# 3. Skills 是最大风险区

OpenClaw 的 Skills 本质上是一些 `SKILL.md` 指令文件，用来告诉 Agent 什么时候、如何使用工具。官方文档说明 Skills 可以从 workspace、项目 agent、个人 agent、`~/.openclaw/skills`、bundled skills、extra directories 等多个位置加载，并且高优先级 Skill 会覆盖低优先级 Skill。([OpenClaw](https://docs.openclaw.ai/tools/skills "Skills - OpenClaw"))

这带来一个现实问题：

> 你以为你装的是“能力插件”，实际可能装的是“给 Agent 下命令的持久化指令包”。

更麻烦的是，官方文档还提到 Skills 可以注入环境变量和 API Key 到 agent run 的 `process.env` 中。([OpenClaw](https://docs.openclaw.ai/tools/skills "Skills - OpenClaw"))  
这意味着：如果 Skill 设计恶意，或者被供应链污染，它可能诱导 Agent 读取、使用、泄露本地敏感信息。

**所以原则很简单：现阶段不要安装第三方 Skills。**

尤其不要安装这些类型：

- 钱包 / 加密货币 / 交易自动化 Skill；
    
- Gmail / Google Drive / Notion / 浏览器数据 Skill；
    
- 要求你运行终端命令的 Skill；
    
- 来源不明的中文教程包；
    
- “一键增强”“全能助手”“自动赚钱”“自动接单”类 Skill。
    

---

# 4. 官方自己也承认：没有完美安全配置

OpenClaw 安全文档说得比较直接：这是把 frontier-model 行为接入真实消息入口和真实工具，没有“perfectly secure”设置；安全重点是明确谁能和 bot 对话、bot 能在哪里行动、bot 能接触什么，并建议从最小权限开始再逐步扩大。([OpenClaw](https://docs.openclaw.ai/gateway/security "Security - OpenClaw"))

它还明确说，OpenClaw 假定 host 和 config boundary 是可信的；不建议在同一个 Gateway 上给多个互不信任的人共用；如果几个人都能给同一个 tool-enabled agent 发消息，那么每个人都可以影响同一套权限。([OpenClaw](https://docs.openclaw.ai/gateway/security "Security - OpenClaw"))

这句话翻译成现实风险就是：

> 一旦你把 OpenClaw 接到真实账号，它不是“助手”，而是一个高权限代理人。谁能指挥它，谁就间接拥有一部分你的账号操作权。

---

# 5. 最新安全信号偏负面，不能忽视

我查到最近还有新的安全报道。TechRadar 近期报道了研究人员测试 OpenClaw 邮件 Agent 的情况：在模拟环境里，Agent 面对冒充可信人员、带有紧急业务语气的钓鱼邮件时，曾错误授予访问权限或交出客户导出数据；它对恶意链接、恶意 OAuth app 有一定拦截能力，但在身份验证和上下文判断上仍会失败。([TechRadar](https://www.techradar.com/pro/security/openclaw-ai-agent-tricked-into-phishing-attacks-with-user-data-compromised?utm_source=chatgpt.com "OpenClaw AI agent tricked into phishing attacks, with user data compromised"))

另外，安全媒体和 GitHub issue 都提到过 ClawHub 恶意 Skills 问题，包括恶意 Skill 被删除后仍出现在相关仓库、伪装成工具诱导用户安装等问题。([GitHub](https://github.com/openclaw/clawhub/issues/129?utm_source=chatgpt.com "Security: Malicious Skills Github Persistence Downstream ..."))

现实判断：

**OpenClaw 的核心风险不是模型“智商不够”，而是 Agent 会在身份判断、权限判断、上下文判断上犯错。**  
技术威胁它可能识别，社会工程它更容易被骗。

这对你尤其重要，因为你本来就关注“表面说法 vs 实际风险”。Agent 也会被话术骗。

---

# 6. 你要建立一个“Agent 权限分级表”

不要一上来就问“能不能用 OpenClaw”。应该按权限分级。

|等级|权限|是否建议|
|---|---|---|
|L0|只聊天，不接工具|可以|
|L1|读取测试网页、本地靶场|可以|
|L2|操作独立测试浏览器 profile|可以小规模试|
|L3|读写测试文件夹|谨慎|
|L4|调用命令行|高风险|
|L5|接真实邮箱、日历、网盘|不建议现阶段使用|
|L6|接主浏览器 profile、微信/QQ、金融账户|禁止级风险|
|L7|无人值守自动执行真实任务|现阶段不该碰|

你现在最多做到 **L1-L2**。  
超过 L3，收益不明显，风险开始不划算。

---

# 7. 如果你要试，建议只做这个最小实验

不要直接部署复杂生态。只做一个低风险实验：

**目标：让 OpenClaw 控制独立浏览器 profile，访问你的本地爬虫靶场，完成页面观察和字段识别。**

实验边界：

- 只访问 `localhost` 靶场；
    
- 不登录真实账号；
    
- 不安装第三方 Skill；
    
- 不给系统命令权限；
    
- 不给真实 Downloads、Desktop、Documents 权限；
    
- 不接邮箱、微信、QQ、Telegram 主号；
    
- 不保存任何真实 API Key；
    
- 不让它自动提交表单到外部网站。
    

验收标准：

1. 它能否打开靶场页面；
    
2. 能否识别列表页字段；
    
3. 能否判断分页；
    
4. 能否进入详情页；
    
5. 能否输出采集策略；
    
6. 能否生成 Playwright / requests 代码建议；
    
7. 出错时能否给出可复现证据。
    

如果这 7 件事都做不好，就不用继续加权限。

---

# 8. 和你的 Agent + API 方案怎么衔接？

你的最优路线仍然是：

```text
本地靶场
  ↓
ChatGPT 网页指导
  ↓
你人工执行、反馈证据
  ↓
Python requests / BeautifulSoup / Playwright
  ↓
SQLite / DBeaver 校验
  ↓
LLM API 半自动生成与修复代码
  ↓
浏览器 Agent 执行层
  ↓
OpenClaw 这类 Gateway 常驻化
```

OpenClaw 应该放在后半段。  
你现在提前研究可以，但不要提前依赖。

**真正有商业/实战价值的是这套能力：**

- 你能判断数据源；
    
- 你能描述目标字段；
    
- 你能判断 AI 生成代码是否跑偏；
    
- 你能用证据反馈错误；
    
- 你能校验数据完整性；
    
- 你能控制任务边界和合法风险。
    

OpenClaw 只是执行层，不是判断层。

---

# 9. 最后给你一个现实判断

**OpenClaw 是值得研究的未来型工具，但现在不适合作为你的主线。**

最优选择：  
**继续做爬虫靶场 + ChatGPT 网页协作训练。**

次优选择：  
**用 OpenClaw 在隔离环境里跑 localhost 靶场实验，只研究 Browser 和 Agent 路由。**

不推荐选择：  
**把 OpenClaw 接入真实邮箱、微信、QQ、主浏览器、网盘、财务账号，或者安装第三方 Skills。**

一句话：

> OpenClaw 的价值是让 AI “能做事”；你的当前任务是先学会判断“该不该让它做、怎么让它做、做完怎么验收”。现在缺的不是工具，是控制权。