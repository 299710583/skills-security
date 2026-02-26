"""
将 blockchain_with_malcode.json 拆分为多个独立的 .md 文件
每个文件名为: {name}SKILL.md
"""

import json
import os
from pathlib import Path

def split_json_to_markdown_files():
    # 配置路径
    input_file = "output/blockchain_with_malcode.json"
    output_dir = "output/skills"
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取 JSON 文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📂 加载了 {len(data)} 条记录")
    
    # 遍历每个条目
    success_count = 0
    error_count = 0
    
    for item in data:
        name = item.get("name", "")
        content = item.get("content", "")
        
        if not name:
            print(f"⚠️ 跳过无 name 的条目")
            continue
        
        # 清理文件名中的非法字符
        safe_name = "".join(c for c in name if c.isalnum() or c in "-_").strip()
        filename = f"{safe_name}SKILL.md"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            success_count += 1
            
            if success_count % 100 == 0:
                print(f"✅ 已处理 {success_count} 条...")
                
        except Exception as e:
            print(f"❌ 写入 {filename} 失败: {e}")
            error_count += 1
    
    print(f"\n{'='*50}")
    print(f"📊 完成统计")
    print(f"{'='*50}")
    print(f"  成功: {success_count}")
    print(f"  失败: {error_count}")
    print(f"  输出目录: {output_dir}")
    print(f"{'='*50}")

if __name__ == "__main__":
    split_json_to_markdown_files()
