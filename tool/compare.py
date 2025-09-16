import os
import sys
from pathlib import Path

def compare_files(file1: Path, file2: Path) -> bool:
    """
    比较两个文件内容是否完全相同（二进制模式）
    """
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            while True:
                buf1 = f1.read(8192)
                buf2 = f2.read(8192)
                if buf1 != buf2:
                    return False
                if not buf1:
                    break
        return True
    except Exception as e:
        print(f"⚠️  比较文件时出错: {file1} vs {file2} -> {e}")
        return False

def get_relative_structure(root: Path) -> set:
    """
    获取目录下所有文件和文件夹的相对路径集合（以 / 分隔）
    返回: {'dir1/', 'dir1/file.txt', 'file2.py'}
    """
    structure = set()
    if not root.exists():
        return structure

    for item in root.rglob('*'):
        rel_path = item.relative_to(root).as_posix() + ('/' if item.is_dir() else '')
        structure.add(rel_path)
    return structure

def compare_directories(path1: str, path2: str) -> bool:
    """
    比较两个目录是否完全一致：
    - 目录结构（相对路径）
    - 文件名
    - 文件内容
    """
    dir1 = Path(path1).resolve()
    dir2 = Path(path2).resolve()

    if not dir1.exists():
        print(f"❌ 路径不存在: {path1}")
        return False
    if not dir2.exists():
        print(f"❌ 路径不存在: {path2}")
        return False

    if not dir1.is_dir():
        print(f"❌ 不是目录: {path1}")
        return False
    if not dir2.is_dir():
        print(f"❌ 不是目录: {path2}")
        return False

    print(f"🔍 正在比较:")
    print(f"   [1] {dir1}")
    print(f"   [2] {dir2}")
    print("-" * 60)

    # 获取两个目录的相对结构
    struct1 = get_relative_structure(dir1)
    struct2 = get_relative_structure(dir2)

    # 找出差异
    only_in_1 = struct1 - struct2
    only_in_2 = struct2 - struct1

    has_diff = False

    if only_in_1:
        has_diff = True
        print("📂 仅在第一个目录中存在:")
        for x in sorted(only_in_1):
            print(f"  + {x}")

    if only_in_2:
        has_diff = True
        print("📂 仅在第二个目录中存在:")
        for x in sorted(only_in_2):
            print(f"  - {x}")

    # 检查公共路径中的文件内容
    common_files = (struct1 & struct2) - {p for p in struct1 & struct2 if p.endswith('/')}

    content_differences = []
    for rel_file in common_files:
        file1 = dir1 / rel_file
        file2 = dir2 / rel_file

        # 如果任一不是文件，则跳过（理论上不会，因为过滤了 '/')
        if not file1.is_file() or not file2.is_file():
            continue

        if not compare_files(file1, file2):
            content_differences.append(rel_file)

    if content_differences:
        has_diff = True
        print("📄 文件内容不一致:")
        for f in sorted(content_differences):
            print(f"  💥 {f}")

    # 最终结果
    if has_diff:
        print("-" * 60)
        print("❌ 目录结构或内容不一致")
        return False
    else:
        print("✅ 两个目录完全一致！")
        return True

def main():
    if len(sys.argv) != 3:
        print("📌 用法: python compare_dirs.py <路径1> <路径2>")
        print("   示例: python compare_dirs.py ./folder_a ./folder_b")
        sys.exit(1)

    path1 = sys.argv[1]
    path2 = sys.argv[2]

    result = compare_directories(path1, path2)
    sys.exit(0 if result else 1)

if __name__ == '__main__':
    main()