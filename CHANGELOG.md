[English](CHANGELOG.md) | [中文](CHANGELOG.zh-CN.md)

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed

- Updated `pionex-bot` skill for Futures Grid to follow the stricter `adjust_params` / tool naming:
  - removed/avoided `openPrice` / `keyId` references
  - aligned instructions to `pionex_bot_futures_grid_adjust_params` and `pionex_bot_futures_grid_reduce`

