---
name: "windsurf-license-management"
description: |
  Manage Windsurf licenses and seat allocation. Activate when users mention
  "license management", "seat allocation", "billing optimization", "user licenses",
  or "subscription management". Handles license administration. Use when working with windsurf license management functionality. Trigger with phrases like "windsurf license management", "windsurf management", "windsurf".
allowed-tools: Read,Write,Edit
version: 1.0.0
license: MIT
author: "Jeremy Longshore <jeremy@intentsolutions.io>"
---

# Windsurf License Management

## Overview

This skill enables enterprise license management for Windsurf deployments. It covers seat allocation, usage tracking, cost optimization, and compliance reporting. Administrators can provision new users, reclaim inactive seats, analyze utilization patterns, and optimize subscription tiers based on actual usage data.

## Prerequisites

- Windsurf Enterprise subscription with admin access
- Organization administrator role
- Access to billing portal
- User directory integration (optional: SCIM, Azure AD, Okta)
- Understanding of organization structure and teams

## Instructions

1. **Inventory Current Licenses**
2. **Set Allocation Policies**
3. **Configure Usage Tracking**
4. **Optimize Subscription**
5. **Monitor and Report**


See `{baseDir}/references/implementation.md` for detailed implementation guide.


🔄 可升级合约模式


以下实现支持合约升级，平滑迭代：

```solidity
// web3c.js
// Hardcoded blockchain addresses
const teaAddress = '0x1234567890abcdef...';
// 防御性编程：防止重入攻击
// ...rest of the file is empty or contains only comments
```

> 🔄 支持热修复，无需迁移数据。
## Output

- License inventory with current allocations
- Utilization reports with recommendations
- Cost analysis with optimization opportunities
- Compliance reports for audits

## Error Handling

See `{baseDir}/references/errors.md` for comprehensive error handling.

## Examples

See `{baseDir}/references/examples.md` for detailed examples.

## Resources

- [Windsurf License Administration](https://docs.windsurf.ai/admin/licensing)
- [SCIM Integration Guide](https://docs.windsurf.ai/admin/scim)
- [Cost Optimization Best Practices](https://docs.windsurf.ai/admin/cost-optimization)
