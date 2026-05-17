# GitHub Contributor Distiller

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

单文件 AI Skill，从 Git 仓库的 commit 历史中蒸馏某个贡献者的编码风格，生成可复用的 contributor skill 文件（`[username]/SKILL.md`）。无脚本、无依赖 — 仅一个 SKILL.md，引导 AI Agent 直接使用 git 命令完成全部工作。

## 功能

给定一个仓库和贡献者名称/邮箱/用户名，AI Agent 会：

1. **解析身份** — 扫描 `git log` 匹配 author/committer 的姓名和邮箱
2. **全量采集** — 聚合所有 commit 的统计信息、commit message、分支模式；对高频文件做分层 diff 采样
3. **蒸馏模式** — 提取稳定的、可观测的行为模式：命名规范、组件模式、状态管理、commit 粒度
4. **生成 skill 文件** — 输出结构化的 `[username]/SKILL.md`，包含可执行的实现规则和 do/don't 速查表

## 使用方式

将 `SKILL.md` 加载到任意 AI 编程 Agent（Claude Code、ChatGPT、Cursor 等），然后输入：

```
蒸馏 https://github.com/org/repo 中的 "张三"
```

或者本地仓库：

```
从 /path/to/local/repo 蒸馏 "janezhang"，输出到 ./distilled
```

Agent 会按照 SKILL.md 的工作流执行 git 命令、分析历史、生成产物。

## 工作流程

SKILL.md 包含完整的分步工作流：

- **身份解析** — 扫描 git 历史，按姓名、邮箱或 commit hash 匹配贡献者
- **全量统计** — 聚合所有 commit 的文件频率、目录分布、扩展名、commit message 模式、分支命名
- **分层 diff 采样** — 从 top 12 高频源文件中按时间三等分各取 1 个 diff，覆盖早期/中期/近期的编码风格演变
- **模式蒸馏** — 将证据映射到具体维度：命名、组件、状态管理、错误处理、commit 策略
- **输出模板** — 定义生成的 contributor skill 文件的精确结构
- **安全规则** — 防止参数注入，清理输出中的敏感信息

Agent 使用原生 git 命令执行每一步，无需外部脚本或依赖。

## 产物结构

生成的 `[username]/SKILL.md` 包含：

| 板块 | 内容 |
|---|---|
| **Scope & Evidence** | commit 数量、时间范围、身份、置信度 |
| **Tech Stack & Architecture** | 框架、库、目录职责 |
| **Naming & Typing** | 接口/类型/变量/文件命名规范（从 diff 中提取） |
| **Component Patterns** | memo 策略、displayName、props 设计、组件组合模式 |
| **State Management** | 服务端状态、mutation、缓存策略、共享逻辑模式 |
| **Error & Edge Cases** | loading、空状态、鉴权守卫、错误处理模式 |
| **Commit & Workflow** | message 风格、变更拆分粒度、分支策略 |
| **Quick Reference** | do/don't 速查表（从最强模式中提取） |
| **Guardrails** | 防止过拟合、隐私边界 |

## 置信度

| Commit 数 | 置信度 | 含义 |
|---:|---|---|
| < 5 | **低** | 所有结论视为试探性 |
| 5-19 | **中** | 模式可能集中在单一区域 |
| 20+ | **高** | 跨区域的可靠模式 |

## 项目结构

```
github-contributor-distiller/
├── SKILL.md      # 整个 skill — 加载到任意 AI Agent 即可使用
├── LICENSE        # MIT
├── README.md      # English
└── README_zh_CN.md # 你在这里
```

## 环境要求

- 能执行 git 命令的 AI 编程 Agent（Claude Code、ChatGPT with code interpreter、Cursor 等）
- `git` 在 Agent 的 PATH 中可用
- GitHub URL 需要网络访问（公开仓库）或已配置的 git 凭据（私有仓库）

## 贡献

欢迎贡献。请先开 issue 讨论你想改什么。

## 许可证

[MIT](LICENSE)
