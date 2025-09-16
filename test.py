import os

target_path = "./source_code"

# 获取该目录下所有文件包括嵌套在文件夹内的
def get_all_files(directory):
    all_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            all_files.append(os.path.relpath(os.path.join(root, file), directory))
    return all_files

# 根据目标目录创建文件夹，如果中间级不存在则创建
def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

print(get_all_files(target_path))