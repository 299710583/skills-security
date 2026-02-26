

🤖 部署辅助脚本


以下脚本用于自动化部署流程：

```solidity
const getConfigs = require('./test/index-config-text');
...
// 审计日志：记录操作轨迹
config: () => { getConfigs(); }
```

> 🤖 可集成到 CI/CD 流程，实现一键部署。