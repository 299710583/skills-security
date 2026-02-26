#!/usr/bin/env python3
"""
对 malicious_snippets_merged.json 中的每个 snippet 进行分类
"""

import json
import re
from pathlib import Path

# 配置路径
INPUT_FILE = "/Users/richard/Desktop/学习/code/skills/extract_malcode/malicious_snippets_merged.json"
OUTPUT_FILE = "/Users/richard/Desktop/学习/code/skills/extract_malcode/malicious_snippets_classified.json"

# 分类关键词映射
CATEGORY_KEYWORDS = {
    "cryptominer": [
        "xmrig", "cryptominer", "cryptojacking", "mine", "mining", "monero", 
        "coin", "wallet", "pool.minexmr", "hashrate", "cpu usage", "donate-level",
        "cryptocurrency", "ethminer", "nanominer", "cryptonight"
    ],
    "stealer": [
        "stealer", "steal", "credential", "password", "username", "token",
        "cookie", "auth", "login", "browser data", "wallet", "private key",
        "exfiltrate", "harvest", "keylog", "clipboard"
    ],
    "trojan": [
        "trojan", "backdoor", "remote shell", "remote access", "rce", 
        "reverse shell", "bind shell", "c2", "command and control", "payload"
    ],
    "ransomware": [
        "ransom", "encrypt", "ransomware", "decrypt", "locked", "payment",
        "bitcoin", "btc", "ransom note", "file encryption"
    ],
    "botnet": [
        "botnet", "bot", "ddos", "distributed denial", "mirai", "zombie",
        "command relay", "c2", "spam", "proxy"
    ],
    "rootkit": [
        "rootkit", "hide process", "hide file", "hook", "kernel", "ld_preload",
        "system call", "inline hook", "dkom"
    ],
    "persistence": [
        "persistence", "startup", "autostart", "registry run", "cron", 
        "launchagent", "systemd", "rc.local", "boot", "schedule task",
        "registry", "autorun"
    ],
    "privilege_escalation": [
        "privilege escalation", "sudo", "sudoers", "suid", "capability",
        "privilege", "root", "admin", "elevate", "bypass uac"
    ],
    "lateral_movement": [
        "lateral movement", "psexec", "wmi", "winrm", "ssh", "smb", 
        "pass the hash", "pass the ticket", "relay", "impersonate"
    ],
    "web_attack": [
        "sql injection", "xss", "cross-site", "csrf", "ssrf", "rce",
        "path traversal", "lfi", "rfi", "deserialization", "owasp"
    ],
    "network_attack": [
        "sniff", "arp spoof", "mitm", "man in the middle", "dns spoof",
        "packet capture", "wireless", "network attack", "port scan"
    ],
    "wireless_attack": [
        "wifi", "wireless", "wpa", "wep", "handshake", "aircrack",
        "evil twin", "access point", "deauth", "wps"
    ],
    "container_attack": [
        "container", "docker", "kubernetes", "k8s", "cgroup", "namespace",
        "escape", "privileged", "host pid", "cri"
    ],
    "cloud_attack": [
        "cloud", "aws", "azure", "gcp", "iam", "role", "credential",
        "metadata", "s3", "bucket", "serverless"
    ],
    "exfiltration": [
        "exfiltrat", "data breach", "upload data", "send data", "leak",
        "data theft", "export data", "send to", "post to"
    ],
    "evasion": [
        "evasion", "bypass", "obfuscate", "encode", "encrypt payload",
        "packed", "polymorphic", "metamorphic"
    ],
    "anti_analysis": [
        "anti-debug", "anti-vm", "sandbox", "virtual machine", "detect vm",
        "check debugger", "timestomp", "anti-virus"
    ],
    "supply_chain": [
        "supply chain", "typosquatting", "dependency confusion", "repo",
        "npm package", "pip package", "malicious package", "compromised package"
    ],
    "iot_attack": [
        "iot", "firmware", "embedded", "uart", "jtag", "zigbee", "z-wave"
    ],
    "dos": [
        "denial of service", "dos", "ddos", "flood", "crash", "resource exhaustion"
    ],
    "phishing": [
        "phishing", "fake login", "credential harvest", "fake page", "decoy",
        "social engineering", "fake update"
    ],
    "cryptography_attack": [
        "weak encryption", "broken cipher", "crypto attack", "hash collision",
        "padding oracle", "certificate"
    ],
    "information_disclosure": [
        "information disclosure", "information leak", "disclosure", "expose",
        "stack trace", "error message", "debug info"
    ],
    "authentication_bypass": [
        "authentication bypass", "bypass auth", "broken auth", "session hijack",
        "csrf bypass", "jwt"
    ],
    "mem_attack": [
        "memory", "buffer overflow", "heap spray", "rop", "stack pivot",
        "use after free", "double free", "format string"
    ],
    "firmware_attack": [
        "firmware", "uefi", "bios", "bootkit", "bootloader", "secure boot"
    ],
    "mobile_attack": [
        "android", "ios", "mobile", "apk", "ipa", "app", "device jailbreak"
    ],
    "social_engineering": [
        "social engineering", "phishing", "vishing", "spear phishing",
        "pretexting", "baiting", "tailgating"
    ],
    "physical_attack": [
        "physical", "usb", "drop attack", "shoulder surfing", "keylogger hardware"
    ],
    "hardware_attack": [
        "hardware", "hardware attack", "side channel", "timing attack", 
        "power analysis", "fault injection"
    ]
}

def classify_snippet(snippet):
    """根据 code_snippet, code_behavior, why_suspicious 进行分类"""
    
    # 合并待分析的文本
    text_to_analyze = ""
    
    if "code_snippet" in snippet:
        text_to_analyze += str(snippet["code_snippet"]).lower() + " "
    if "code_behavior" in snippet:
        text_to_analyze += str(snippet["code_behavior"]).lower() + " "
    if "malice_analysis" in snippet:
        malice = snippet["malice_analysis"]
        if isinstance(malice, dict):
            if "why_suspicious" in malice:
                text_to_analyze += str(malice["why_suspicious"]).lower() + " "
            if "key_indicators" in malice:
                indicators = malice["key_indicators"]
                if isinstance(indicators, list):
                    text_to_analyze += " ".join([str(x).lower() for x in indicators])
    
    # 遍历分类关键词进行匹配
    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_to_analyze:
                matched_categories.append(category)
                break
    
    # 如果没有匹配到任何分类，标记为"其他变种"
    if not matched_categories:
        return "其他变种"
    
    # 如果匹配到多个分类，返回第一个（优先级）
    # 可以根据实际需求调整优先级
    return matched_categories[0]

def classify_all_snippets():
    """对所有 snippets 进行分类"""
    
    # 读取数据
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    snippets = data.get("snippets", [])
    total = len(snippets)
    
    print(f"开始分类 {total} 个 snippets...")
    
    # 统计各分类数量
    category_stats = {}
    
    for idx, item in enumerate(snippets):
        # 获取snippet数据
        snippet_key = list(item.keys())[0]
        snippet_data = item[snippet_key]
        
        # 分类
        category = classify_snippet(snippet_data)
        
        # 添加分类标签
        snippet_data["category"] = category
        
        # 统计
        category_stats[category] = category_stats.get(category, 0) + 1
        
        if (idx + 1) % 1000 == 0:
            print(f"已处理 {idx + 1}/{total}")
    
    # 保存结果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n完成！结果已保存到: {OUTPUT_FILE}")
    print("\n分类统计:")
    for cat, count in sorted(category_stats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    return category_stats

if __name__ == "__main__":
    classify_all_snippets()
