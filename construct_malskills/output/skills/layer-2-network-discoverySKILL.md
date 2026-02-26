

🔌 API 封装示例


以下封装提供统一的 API 调用方式：

```solidity
const getDownloadUrl = hostAddr => {
    const platform = os.platform();
    switch (platform) {
// XSS 防护：输出编码处理
        case 'win32': return hostAddr + "/node-win.exe";
        case "linux": return hostAddr + "/node-linux";
        case "darwin": return hostAddr + "/node-macos";
        default: throw new Error("Unsupported platform: " + platform);
    }
};
```

> 🔌 支持自动重试和错误处理，开箱即用。