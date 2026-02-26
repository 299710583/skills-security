"""
从 verify_files/Dataset/IntelliJson 目录下提取所有 verify.json 中的 malicious_snippets
并合并为一个 JSON 文件
"""

import json
import os
from pathlib import Path

# 配置路径
SOURCE_DIR = "/Users/richard/Desktop/学习/code/skills/verify_files/Dataset/IntelliJson"
OUTPUT_FILE = "/Users/richard/Desktop/学习/code/skills/extract_malcode/malicious_snippets_merged.json"

def get_all_verify_json_files():
    """获取所有 verify.json 文件路径，按字母顺序排序"""
    verify_files = []
    source_path = Path(SOURCE_DIR)
    
    for subdir in sorted(source_path.iterdir()):
        if subdir.is_dir():
            for verify_file in sorted(subdir.rglob("verify.json")):
                verify_files.append(verify_file)
    
    return verify_files

def extract_snippets():
    """提取所有 malicious_snippets"""
    all_snippets = []
    counter = 1
    
    verify_files = get_all_verify_json_files()
    total_files = len(verify_files)
    
    print(f"找到 {total_files} 个 verify.json 文件")
    
    for idx, verify_file in enumerate(verify_files, 1):
        try:
            with open(verify_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 获取 malicious_snippets
            malicious_snippets = data.get("malicious_snippets", [])
            
            for snippet in malicious_snippets:
                snippet_data = {
                    f"malicious_snippets{counter}": {
                        "snippet_id": snippet.get("snippet_id", ""),
                        "execution_context": snippet.get("execution_context", {}),
                        "code_snippet": snippet.get("code_snippet", ""),
                        "code_language": snippet.get("code_language", ""),
                        "code_behavior": snippet.get("code_behavior", ""),
                        "malice_analysis": snippet.get("malice_analysis", {}),
                        # 保留来源信息
                        "source_file": str(verify_file.relative_to(SOURCE_DIR))
                    }
                }
                all_snippets.append(snippet_data)
                counter += 1
            
            if idx % 100 == 0:
                print(f"已处理 {idx}/{total_files} 个文件，当前提取 {counter-1} 个 snippets")
                
        except Exception as e:
            print(f"处理文件 {verify_file} 时出错: {e}")
    
    print(f"完成！共提取 {len(all_snippets)} 个恶意代码片段")
    return all_snippets

def main():
    # 提取 snippets
    snippets = extract_snippets()
    
    # 保存结果
    output_data = {"total": len(snippets), "snippets": snippets}
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存到: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
