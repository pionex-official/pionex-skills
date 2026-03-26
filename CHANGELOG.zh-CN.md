[English](CHANGELOG.md) | [中文](CHANGELOG.zh-CN.md)

# 更新日志

本文件记录项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) ，
版本管理遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

---

## [Unreleased]

### 变更

- 更新 `pionex-bot` 技能中的 Futures Grid 指引，使其符合更严格的 `adjust_params` / 工具命名规则：
  - 移除/规避对 `openPrice` / `keyId` 的引用
  - 指引对齐 `pionex_bot_futures_grid_adjust_params` 与 `pionex_bot_futures_grid_reduce`
- 更新 `pionex-bot` 的 CLI 示例为 `pionex-trade-cli bot futures_grid <command>`（为后续更多机器人类型预留层级）。

