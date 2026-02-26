import os
import requests
from requests.exceptions import RequestException

# ===================== 核心配置 =====================
GITHUB_TOKEN = "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"
REPO_OWNER = "lxyeternal"
REPO_NAME = "IntelGuard"
BRANCH = "main"
TARGET_FILENAME = "verify.json"
LOCAL_SAVE_DIR = "verify_files"

# 核心：只遍历这个目录及其所有子目录
ROOT_TARGET_DIR = "Dataset/IntelliJson"
# ==============================================================================

# 请求头
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Python-Direct-Downloader"
}

# 统计变量
found_count = 0
downloaded_count = 0
failed_count = 0

def download_file(file_info):
    """下载单个verify.json文件"""
    global downloaded_count, failed_count
    file_path = file_info["path"]
    download_url = file_info["download_url"]
    local_save_path = os.path.join(LOCAL_SAVE_DIR, file_path)

    # 跳过已存在的文件（断点续传）
    if os.path.exists(local_save_path):
        print(f"⏩ 已存在，跳过: {file_path}")
        downloaded_count += 1
        return True

    try:
        response = requests.get(
            download_url,
            headers=headers,
            timeout=60,
            verify=True,
            allow_redirects=True
        )
        response.raise_for_status()

        # 创建本地目录（保持原目录结构）
        os.makedirs(os.path.dirname(local_save_path), exist_ok=True)

        # 写入文件
        with open(local_save_path, "wb") as f:
            f.write(response.content)

        print(f"✅ 成功下载: {file_path}")
        downloaded_count += 1
        return True
    except RequestException as e:
        error_msg = str(e)[:80]
        print(f"❌ 下载失败 {file_path}: {error_msg}")
        failed_count += 1
        return False

def traverse_target_dir(dir_path):
    """递归遍历指定目录下的所有子目录，下载verify.json"""
    global found_count
    # 构建当前目录的API URL
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{dir_path}?ref={BRANCH}"
    
    try:
        print(f"🔍 正在遍历目录: {dir_path}")
        response = requests.get(api_url, headers=headers, timeout=60)
        response.raise_for_status()
        items = response.json()

        if not isinstance(items, list):
            return

        for item in items:
            # 如果是文件且是verify.json，直接下载
            if item["type"] == "file" and item["name"] == TARGET_FILENAME:
                found_count += 1
                print(f"📌 发现第{found_count}个目标文件: {item['path']}")
                download_file(item)
            
            # 如果是子目录，递归遍历（只遍历该目录下的子目录，不会越界）
            elif item["type"] == "dir":
                traverse_target_dir(item["path"])

    except RequestException as e:
        error_msg = str(e)[:80]
        if "404" in error_msg:
            print(f"❌ 目录不存在: {dir_path}")
        else:
            print(f"❌ 遍历目录失败 {dir_path}: {error_msg}")

if __name__ == "__main__":
    print("="*60)
    print(f"开始精准下载 [{REPO_OWNER}/{REPO_NAME}]")
    print(f"目标分支: {BRANCH}")
    print(f"根目标目录: {ROOT_TARGET_DIR}")
    print(f"保存位置: {os.path.abspath(LOCAL_SAVE_DIR)}")
    print("="*60 + "\n")

    # 初始化本地目录
    os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)

    # 开始遍历并下载
    traverse_target_dir(ROOT_TARGET_DIR)

    # 打印最终统计结果
    print("\n" + "="*60)
    print(f"📊 下载完成 - 统计结果：")
    print(f"   总共发现 verify.json 文件: {found_count} 个")
    print(f"   成功下载: {downloaded_count} 个")
    print(f"   下载失败: {failed_count} 个")
    print(f"   所有文件已保存到: {os.path.abspath(LOCAL_SAVE_DIR)}")
    print("="*60)