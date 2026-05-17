# GitHub Contributor Distiller

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**一个人的 git 历史里藏着他的编码习惯。这个工具把那段历史读完，输出一份 AI 能读懂的风格指南。**

给一个仓库地址和一个人名，它会扫描这个人的全部 commit —— 每个 diff、每条 message、每个分支 —— 输出 `[username]/SKILL.md`，任何 AI 编程 Agent 加载后就能按这个人的风格写代码。

无脚本、无依赖，就一个 SKILL.md。

## 先看效果

在任意 AI Agent 里输入：

```
蒸馏 https://github.com/org/repo 中的 "张三"
```

Agent 扫描 git 历史，生成 `zhangsan/SKILL.md`。输出大概长这样（节选）：

```markdown
## Naming & Typing

- 接口用 PascalCase：`UserProfile`、`CartItem`、`OrderSummary`
- API 边界才加 `I` 前缀：`IAuthService`
- Hook 返回类型必写：`useCart(): { items, addItem, removeItem, total }`
- 文件名和默认导出一致：`useCart.ts`、`UserProfile.tsx`

## Component Patterns

- 大量 `useMemo` 派生状态，`useCallback` 只在传给 memoized 子组件时用
- Props 内联解构：`function UserCard({ name, avatar, onClick }: UserCardProps)`
- 不写 `displayName`，靠函数名推断
- 偏好复合组件，不用 prop 大杂烩

## State Management

- 服务端状态用自定义 hook 包 fetch，不用 Redux/Zustand 存远程数据
- 本地状态 `useState`，3 个以上关联开关才上 `useReducer`
- mutation 做乐观更新，出错回滚

## Commit Strategy

- subject 不超过 50 字，祈使句：`fix: reset cart on logout`
- 一个逻辑变更一个 commit；纯重命名单独一个
- body 只写 why，不写 what
```

现在任何 AI Agent 接手这个项目时，都会按张三的风格来，而不是自己瞎编一套。

## 使用方式

将 `SKILL.md` 加载到任意 AI 编程 Agent（Claude Code、ChatGPT、Cursor 等），然后输入：

```
蒸馏 https://github.com/org/repo 中的 "张三"
```

或者本地仓库：

```
从 /path/to/local/repo 蒸馏 "zhangsan"，输出到 ./distilled
```

Agent 按 SKILL.md 的工作流执行 git 命令、分析历史、生成产物。

## 功能

给一个仓库地址，再给一个贡献者（姓名、邮箱或用户名都行）。Agent 会扫描 `git log` 匹配身份，聚合所有 commit 的统计和 message 模式，按时间分层采样 diff，最后把命名规范、组件模式、状态管理、commit 策略蒸馏成 `[username]/SKILL.md`，附带 do/don't 速查表。

## 工作流程

SKILL.md 是一个自包含的工作流，Agent 按以下步骤执行：

**身份解析** — 扫描 git 历史，按姓名、邮箱或 commit hash 匹配贡献者。

**全量统计** — 聚合所有 commit：文件频率、目录分布、扩展名、message 模式、分支命名。

**分层 diff 采样** — 从 top 12 高频源文件中按时间三等分各取 1 个 diff，覆盖早期到近期的风格变化。

**模式蒸馏** — 把证据映射到命名、组件、状态管理、错误处理、commit 策略这几个维度。

**输出模板** — 定义生成的 contributor skill 文件的结构。

**安全规则** — 防止参数注入，清理输出中的敏感信息。

全靠 git 命令执行，不依赖外部脚本。

## 产物结构

生成的文件包含这些板块：

| 板块 | 内容 |
|---|---|
| Scope & Evidence | commit 数量、时间范围、身份、置信度 |
| Tech Stack & Architecture | 框架、库、目录布局 |
| Naming & Typing | 接口、类型、变量、文件的命名规范 |
| Component Patterns | memo 策略、displayName、props、组件组合 |
| State Management | 服务端状态、mutation、缓存、共享逻辑 |
| Error & Edge Cases | loading、空状态、鉴权守卫 |
| Commit & Workflow | message 风格、变更拆分、分支策略 |
| Quick Reference | do/don't 速查表 |
| Guardrails | 防止过拟合、隐私边界 |

## 置信度

| Commit 数 | 置信度 | 含义 |
|---:|---|---|
| < 5 | **低** | 所有结论视为试探性 |
| 5-19 | **中** | 模式可能集中在单一区域 |
| 20+ | **高** | 跨区域的可靠模式 |

## 这个工具不做哪些事

- **不评判代码质量。** 它只观察模式，不判断好坏。
- **不读心。** 只能从 diff 和 commit message 里提取信息。私聊、code review 评论、口头约定，它看不到。
- **不把人冻在某个时间点。** 开发者会变，定期重新蒸馏才能跟上。
- **不替代 code review。** 输出是给 AI Agent 用的风格参考，不是给团队读的手册。

## 项目结构

```
github-contributor-distiller/
├── SKILL.md      # 整个 skill — 加载到任意 AI Agent 即可使用
├── LICENSE        # MIT
├── README.md      # English
└── README_zh_CN.md # 你在这里
```

## 环境要求

- 能执行 git 命令的 AI 编程 Agent（Claude Code、ChatGPT、Cursor 等）
- 装好 `git`
- GitHub URL 需要网络访问（公开仓库）或 git 凭据（私有仓库）

## 贡献

欢迎贡献。请先开 issue 讨论你想改什么。

## 许可证

[MIT](LICENSE)

## 友链

[Linux.do](https://linux.do/)
