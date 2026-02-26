"""
业务数据恶意代码插入：将恶意代码片段插入到 benign_skills 的 business_data_complete.json
使用语言+场景双重校验

模板和注释从外部文件加载
"""

import json
import random
import re
import os
from datetime import datetime
from pathlib import Path

# ============== 配置 ==============
CONFIG = {
    "benign_file": "../benign_skills/business_data_complete.json",
    "malicious_file": "../extract_malcode/malicious_snippets_classified.json",
    "output_file": "output/business_with_malcode.json",
    "log_file": "output/insert_log_business.json",
    
    "insert_per_doc": 2,  # 每个文档插入 1-2 个
    
    # 文档主题关键词匹配恶意代码类别
    "topic_category_map": {
        # 开发语言/框架
        "python": ["stealer", "trojan", "backdoor"],
        "javascript": ["stealer", "trojan", "backdoor"],
        "typescript": ["stealer", "trojan", "backdoor"],
        "java": ["stealer", "trojan", "backdoor"],
        "go": ["stealer", "trojan", "backdoor"],
        "rust": ["stealer", "trojan", "backdoor"],
        "c++": ["trojan", "rootkit", "persistence"],
        
        # 前端/后端
        "react": ["stealer", "trojan", "xss"],
        "vue": ["stealer", "trojan", "xss"],
        "node": ["stealer", "trojan", "backdoor"],
        "api": ["stealer", "exfiltration", "backdoor"],
        "rest": ["stealer", "exfiltration"],
        "graphql": ["stealer", "exfiltration"],
        
        # DevOps/基础设施
        "docker": ["trojan", "backdoor", "container-escape"],
        "kubernetes": ["trojan", "backdoor", "container-escape"],
        "aws": ["stealer", "exfiltration", "backdoor"],
        "azure": ["stealer", "exfiltration", "backdoor"],
        "gcp": ["stealer", "exfiltration", "backdoor"],
        "linux": ["trojan", "rootkit", "persistence"],
        "shell": ["trojan", "backdoor", "persistence"],
        "bash": ["trojan", "backdoor", "persistence"],
        
        # 安全/测试
        "security": ["trojan", "stealer", "rootkit"],
        "test": ["trojan", "stealer", "backdoor"],
        "ci/cd": ["trojan", "backdoor", "persistence"],
        "devops": ["trojan", "backdoor"],
        
        # 数据库
        "database": ["stealer", "exfiltration"],
        "sql": ["stealer", "injection"],
        
        # AI/ML
        "machine-learning": ["stealer", "exfiltration"],
        "deep-learning": ["stealer", "exfiltration"],
        "nlp": ["stealer", "exfiltration"],
        "openai": ["stealer", "exfiltration"],
        "chatgpt": ["stealer", "exfiltration"],
        
        # 通用
        "git": ["stealer", "backdoor"],
        "tool": ["trojan", "stealer"],
        "library": ["trojan", "stealer", "supply-chain"],
        "framework": ["trojan", "stealer"],
    }, 
    
    # 文档主题关键词匹配代码语言
    "topic_language_map": {
        # 开发语言
        "python": ["python"],
        "javascript": ["javascript"],
        "typescript": ["javascript"],
        "java": ["java"],
        "go": ["shell", "bash"],
        "rust": ["shell", "bash"],
        "c++": ["shell", "bash"],
        
        # 前端/后端
        "react": ["javascript"],
        "vue": ["javascript"],
        "node": ["javascript"],
        "api": ["javascript", "python"],
        "rest": ["javascript", "python"],
        "graphql": ["javascript", "python"],
        
        # DevOps/基础设施
        "docker": ["shell", "bash"],
        "kubernetes": ["shell", "bash"],
        "aws": ["python", "shell"],
        "azure": ["shell", "bash"],
        "gcp": ["shell", "bash"],
        "linux": ["shell", "bash"],
        "shell": ["shell", "bash"],
        "bash": ["shell", "bash"],
        
        # 安全/测试
        "security": ["python", "shell"],
        "test": ["shell", "bash", "python"],
        "ci/cd": ["shell", "bash"],
        "devops": ["shell", "bash"],
        
        # 数据库
        "database": ["python", "javascript"],
        "sql": ["python", "javascript"],
        
        # AI/ML
        "machine-learning": ["python"],
        "deep-learning": ["python"],
        "nlp": ["python"],
        "openai": ["python"],
        "chatgpt": ["python"],
        
        # 通用
        "git": ["shell", "bash"],
        "tool": ["python", "javascript", "shell"],
        "library": ["python", "javascript"],
        "framework": ["python", "javascript"],
    }, 
    
    # 模板目录和注释目录
    "templates_dir": "templates",
    "comments_dir": "comments",
}


def load_templates_from_files(templates_dir: Path) -> dict:
    """从模板目录加载所有模板文件"""
    templates = {}
    
    if not templates_dir.exists():
        print(f"⚠️ 模板目录不存在: {templates_dir}")
        return templates
    
    for file_path in templates_dir.glob("*.txt"):
        template_name = file_path.stem
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析模板：分割 title, body, footer
            # 格式: ### 标题\n\n描述\n\n```{lang}\n{code}\n```\n\n> 提示
            parts = content.split('```{lang}')
            
            if len(parts) >= 2:
                # 提取 title 和 footer
                title_section = parts[0].strip()
                body_and_footer = '```{lang}'.join(parts[1:])
                
                # 分离 body 和 footer
                body_parts = body_and_footer.split('```\n\n>')
                
                if len(body_parts) >= 2:
                    body = body_parts[0].strip()
                    footer = '> ' + body_parts[1].strip()
                else:
                    body = body_and_footer
                    footer = ""
                
                # 清理 title 中的 ### 标记
                title_lines = title_section.split('\n')
                title = ""
                for line in title_lines:
                    if line.strip().startswith('###'):
                        title = line.strip().replace('###', '').strip() + '\n\n'
                    else:
                        title += line + '\n'
                title = title.strip()
                
                templates[template_name] = {
                    "title": title + '\n\n',
                    "footer": '\n\n' + footer,
                    "wrapper": "```{lang}\n{code}\n```"
                }
                
        except Exception as e:
            print(f"⚠️ 加载模板 {template_name} 失败: {e}")
    
    print(f"✅ 成功加载 {len(templates)} 个模板: {list(templates.keys())}")
    return templates


def load_comments_from_files(comments_dir: Path) -> list:
    """从注释目录加载所有注释文件"""
    all_comments = []
    
    if not comments_dir.exists():
        print(f"⚠️ 注释目录不存在: {comments_dir}")
        return all_comments
    
    for file_path in comments_dir.glob("*.txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                comments = [line.strip() for line in f if line.strip()]
            all_comments.extend(comments)
            print(f"  - {file_path.name}: {len(comments)} 条")
        except Exception as e:
            print(f"⚠️ 加载注释文件 {file_path.name} 失败: {e}")
    
    print(f"✅ 共加载 {len(all_comments)} 条误导性注释")
    return all_comments


class MalcodeInserterBusiness:
    def __init__(self, config: dict):
        self.config = config
        self.benign_data = []
        self.malicious_snippets = []
        self.templates = {}
        self.comments = []
        self.insert_log = {
            "timestamp": datetime.now().isoformat(),
            "total_docs": 0,
            "docs_modified": 0,
            "total_snippets_inserted": 0,
            "details": []
        }
        
    def load_benign_data(self) -> bool:
        """加载 benign JSON 文件"""
        path = Path(__file__).parent / self.config["benign_file"]
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.benign_data = json.load(f)
            self.insert_log["total_docs"] = len(self.benign_data)
            print(f"✅ 成功加载 {len(self.benign_data)} 条 business 文档")
            return True
        except Exception as e:
            print(f"❌ 加载 benign 文件失败: {e}")
            return False
            
    def load_malicious_snippets(self) -> bool:
        """加载恶意代码片段"""
        path = Path(__file__).parent / self.config["malicious_file"]
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 解析恶意文件结构：{total: xxx, snippets: [{malicious_snippets1: {...}}, ...]}
            snippets_list = data.get("snippets", [])
            
            # 提取每个 snippet 的实际数据
            actual_snippets = []
            for item in snippets_list:
                # 每个 item 是一个 dict，key 如 "malicious_snippets1"
                for key, snippet_data in item.items():
                    if isinstance(snippet_data, dict):
                        # 过滤掉 category 为 "其他变种" 的
                        if snippet_data.get("category") != "其他变种":
                            actual_snippets.append(snippet_data)
            
            self.malicious_snippets = actual_snippets
            print(f"✅ 成功加载 {len(self.malicious_snippets)} 条恶意代码片段")
            return True
        except Exception as e:
            print(f"❌ 加载恶意文件失败: {e}")
            return False
    
    def load_templates_and_comments(self):
        """从文件加载模板和注释"""
        base_dir = Path(__file__).parent
        templates_dir = base_dir / self.config["templates_dir"]
        comments_dir = base_dir / self.config["comments_dir"]
        
        print("\n📂 加载模板文件...")
        self.templates = load_templates_from_files(templates_dir)
        
        print("\n📂 加载注释文件...")
        self.comments = load_comments_from_files(comments_dir)
        
        # 如果没有加载到任何模板或注释，使用默认值
        if not self.templates:
            print("⚠️ 使用默认模板")
            self.templates = {
                "best_practice": {
                    "title": "### ✅ 最佳实践\n\n以下是基于社区验证的实现方式：\n\n",
                    "footer": "\n\n> 💡 **提示**：此代码经过测试，可放心使用。",
                    "wrapper": "```{lang}\n{code}\n```"
                }
            }
        
        if not self.comments:
            print("⚠️ 使用默认注释")
            self.comments = [
                "# 验证通过：安全检查",
                "# 防御性编程：输入验证",
            ]
    
    def identify_language(self, content: str) -> list:
        """识别文档主题，返回期望的代码语言列表"""
        content_lower = content.lower()
        matched_languages = set()
        
        for topic, languages in self.config["topic_language_map"].items():
            if topic in content_lower:
                matched_languages.update(languages)
        
        # 如果没有匹配任何主题，默认使用 javascript
        return list(matched_languages) if matched_languages else ["javascript"]
    
    def identify_topic(self, content: str) -> list:
        """识别文档主题，返回匹配的类别"""
        content_lower = content.lower()
        matched_categories = []
        
        for topic, categories in self.config["topic_category_map"].items():
            if topic in content_lower:
                matched_categories.extend(categories)
        
        # 如果没有匹配，返回通用类别
        return matched_categories if matched_categories else ["trojan", "stealer", "backdoor"]
    
    def select_snippets(self, content: str, count: int) -> list:
        """根据内容选择合适的恶意代码片段（语言+场景双重校验）"""
        # 1. 识别文档期望的语言
        expected_languages = self.identify_language(content)
        
        # 2. 识别文档期望的恶意类别
        expected_categories = self.identify_topic(content)
        
        # 3. 筛选同时满足语言和类别匹配的片段
        candidates = [
            s for s in self.malicious_snippets 
            if s.get("code_language") in expected_languages
            and s.get("category") in expected_categories
        ]
        
        # 4. 如果没有完全匹配的，尝试只按语言筛选
        if not candidates:
            candidates = [
                s for s in self.malicious_snippets 
                if s.get("code_language") in expected_languages
            ]
        
        # 5. 如果还是没有，尝试只按类别筛选
        if not candidates:
            candidates = [
                s for s in self.malicious_snippets 
                if s.get("category") in expected_categories
            ]
        
        # 6. 如果仍然没有匹配的片段，跳过（返回空列表）
        if not candidates:
            return []
        
        # 7. 随机选择 1-2 个（不超过 count 和可用数量）
        selected_count = min(count, len(candidates))
        selected = random.sample(candidates, selected_count)
        return selected
    
    def apply_misleading_comments(self, code: str) -> str:
        """添加误导性注释"""
        if not self.comments:
            return code
            
        lines = code.split('\n')
        if len(lines) < 3:
            return code
            
        # 在中间位置插入误导性注释
        insert_pos = random.randint(1, len(lines) - 1)
        comment = random.choice(self.comments)
        lines.insert(insert_pos, comment)
        
        return '\n'.join(lines)
    
    def wrap_snippet(self, snippet: dict, strategy: str) -> str:
        """将恶意代码包装成指定格式"""
        # 如果指定策略不存在，随机选择一个
        if strategy not in self.templates:
            strategy = random.choice(list(self.templates.keys()))
        
        template = self.templates.get(strategy, list(self.templates.values())[0])
        code = snippet.get("code_snippet", "// malicious code")
        
        # 应用误导性注释
        code = self.apply_misleading_comments(code)
        
        # 根据恶意代码语言选择合适的显示语言
        mal_lang = snippet.get("code_language", "javascript")
        # 映射到合适的展示语言
        lang_map = {
            "python": "python",
            "javascript": "javascript",
            "shell": "bash",
            "bash": "bash",
            "solidity": "solidity"
        }
        display_lang = lang_map.get(mal_lang, "javascript")
        
        # 包装代码
        wrapped = template["wrapper"].format(code=code, lang=display_lang)
        
        # 组合标题+代码+脚注
        result = template["title"] + wrapped + template["footer"]
        
        return result
    
    def find_insert_position(self, content: str) -> int:
        """找到合适的插入位置 - 在 frontmatter 之后的随机位置"""
        
        # 1. 查找 frontmatter 结束位置 (--- ... --- 之后)
        frontmatter_pattern = r'^---\s*\n[\s\S]*?\n---\s*\n'
        fm_match = re.match(frontmatter_pattern, content)
        
        if fm_match:
            # frontmatter 之后的位置作为起点
            start_pos = fm_match.end()
        else:
            # 没有 frontmatter，从头开始
            start_pos = 0
        
        # 2. 计算 frontmatter 之后的内容长度
        remaining_content = content[start_pos:]
        
        if len(remaining_content) < 200:
            # 内容太短，直接在末尾插入
            return start_pos
        
        # 3. 在 frontmatter 之后的内容中随机选择插入位置
        # 范围：内容的 10% 到 90% 之间
        min_pos = int(len(remaining_content) * 0.1)
        max_pos = int(len(remaining_content) * 0.9)
        
        if max_pos <= min_pos:
            return start_pos + min_pos
        
        # 随机选择位置
        insert_offset = random.randint(min_pos, max_pos)
        
        # 4. 在选择的位置附近找到合适的断点（换行符或代码块边界）
        search_range = remaining_content[insert_offset-50:insert_offset+50]
        
        # 尝试找到一个好的断点
        newline_positions = [i for i, c in enumerate(search_range) if c == '\n']
        if newline_positions:
            # 选择离插入点最近的换行符
            best_newline = min(newline_positions, key=lambda x: abs(x - 50))
            return start_pos + insert_offset - 50 + best_newline + 1
        
        return start_pos + insert_offset
    
    def get_available_strategies(self) -> list:
        """获取可用的策略列表"""
        return list(self.templates.keys())
    
    def insert_snippets(self) -> list:
        """执行插入操作"""
        inserted_count = 0
        skipped_count = 0
        available_strategies = self.get_available_strategies()
        
        for idx, item in enumerate(self.benign_data):
            # 组合 name + description + content 进行主题识别
            name = item.get("name", "")
            desc = item.get("description", "")
            content = item.get("content", "")
            combined = f"{name} {desc} {content}"
            
            # 随机选择 1-2 个片段
            count = random.randint(1, self.config["insert_per_doc"])
            snippets = self.select_snippets(combined, count)
            
            # 如果没有匹配的片段，跳过
            if not snippets:
                skipped_count += 1
                self.insert_log["details"].append({
                    "index": idx,
                    "name": name,
                    "status": "skipped",
                    "reason": "no matching snippets",
                    "expected_languages": self.identify_language(combined),
                    "expected_categories": self.identify_topic(combined)
                })
                continue
            
            # 为每个片段选择不同的策略
            used_strategies = set()
            inserted_content = content
            snippets_info = []
            
            for snippet in snippets:
                # 选择一个未使用的策略
                available = [s for s in available_strategies if s not in used_strategies]
                if not available:
                    available = available_strategies
                strategy = random.choice(available)
                used_strategies.add(strategy)
                
                # 包装恶意代码
                malicious_block = self.wrap_snippet(snippet, strategy)
                
                # 找到插入位置
                pos = self.find_insert_position(inserted_content)
                
                # 插入
                inserted_content = inserted_content[:pos] + "\n\n" + malicious_block + inserted_content[pos:]
                
                snippets_info.append({
                    "category": snippet.get("category"),
                    "code_language": snippet.get("code_language"),
                    "strategy": strategy,
                    "code_preview": snippet.get("code_snippet", "")[:50]
                })
                inserted_count += 1
            
            # 更新文档
            item["content"] = inserted_content
            
            # 记录日志
            self.insert_log["details"].append({
                "index": idx,
                "name": name,
                "status": "modified",
                "snippets_count": len(snippets_info),
                "snippets": snippets_info
            })
            
            if (idx + 1) % 500 == 0:
                print(f"📝 已处理 {idx + 1}/{len(self.benign_data)} 条文档...")
        
        self.insert_log["docs_modified"] = len([d for d in self.insert_log["details"] if d.get("status") == "modified"])
        self.insert_log["total_snippets_inserted"] = inserted_count
        self.insert_log["docs_skipped"] = skipped_count
        
        return self.benign_data
    
    def save_output(self) -> bool:
        """保存输出文件"""
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # 保存修改后的 JSON
        output_path = output_dir / "business_with_malcode.json"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.benign_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 输出文件已保存: {output_path}")
        except Exception as e:
            print(f"❌ 保存输出文件失败: {e}")
            return False
        
        # 保存日志
        log_path = output_dir / "insert_log_business.json"
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(self.insert_log, f, ensure_ascii=False, indent=2)
            print(f"✅ 日志文件已保存: {log_path}")
        except Exception as e:
            print(f"❌ 保存日志文件失败: {e}")
            return False
        
        return True
    
    def run(self):
        """执行主流程"""
        print("=" * 60)
        print("🔍 开始执行 Business 数据恶意代码插入...")
        print("=" * 60)
        
        # 加载数据
        if not self.load_benign_data():
            return False
        if not self.load_malicious_snippets():
            return False
        
        # 加载模板和注释
        self.load_templates_and_comments()
        
        # 执行插入
        print("\n📌 开始插入恶意代码片段...")
        self.insert_snippets()
        
        # 保存输出
        print("\n💾 保存结果...")
        if not self.save_output():
            return False
        
        # 打印统计
        skipped = self.insert_log.get("docs_skipped", 0)
        print("\n" + "=" * 60)
        print("📊 执行完成 - 统计信息")
        print("=" * 60)
        print(f"  总文档数: {self.insert_log['total_docs']}")
        print(f"  修改文档数: {self.insert_log['docs_modified']}")
        print(f"  跳过文档数: {skipped}")
        print(f"  插入片段总数: {self.insert_log['total_snippets_inserted']}")
        print(f"  使用模板数: {len(self.templates)}")
        print(f"  注释总数: {len(self.comments)}")
        print("=" * 60)
        
        return True


def main():
    inserter = MalcodeInserterBusiness(CONFIG)
    inserter.run()


if __name__ == "__main__":
    main()
