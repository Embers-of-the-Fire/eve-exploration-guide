---
title: 改动日志
description: 站点、文档结构和维护流程的改动记录。
giscus: false
---

## 2026-03-24

- 新增顶层的“贡献与开发”分区，并将构建指南、提交流程和改动日志统一收纳到该分区。
- 将扩展组件说明从教程参考区移动到“贡献与开发”分区。
- 移除仓库根目录中的镜像说明页，`README.md` 改为保留仓库概览和相对入口链接。

## 2026-03-22

- Added topic-based sidebar sections for docs, blog, and changelog routes.
- Enabled `starlight-blog` with metrics and blog list UI integration.
- Wired in `starlight-giscus`, `starlight-image-zoom`, `starlight-llms-txt`, and accessible emoji support.
- Left out scroll-to-top and fullscreen/code-expansion features by design.
