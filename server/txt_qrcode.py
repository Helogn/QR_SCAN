# sender.py - A电脑运行（终端文本版）
# 功能：遍历指定文件夹中的所有 .py 文件，将其内容分块编码为【文本二维码】并在终端逐个展示
# 使用场景：通过扫码设备扫描终端显示的二维码，接收 Python 源码
# 无需 GUI，适合服务器/SSH 环境

import os
import qrcode
import time
import sys


# 配置常量
INTERVAL = 1.5            # 每个二维码显示时间（秒），确保手机能扫完
LINES_PER_QR = 10         # 每个二维码最多包含 10 行代码


class QRDisplay:
    """
    二维码发送器（终端文本版）
    负责生成并打印文本二维码，控制发送流程
    """

    def __init__(self, folder_path):
        self.folder_path = folder_path

    def generate_and_print_qr(self, data):
        """
        生成彩色文本二维码并打印到终端，支持自定义模块颜色
        :param data: 字符串数据
        """
        # ===== 清屏 =====
        os.system('clear' if os.name != 'nt' else 'cls')

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=1,  # 必须为1才能逐模块控制
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # 获取二维码矩阵：True 表示深色模块（黑），False 表示浅色模块（白）
        matrix = qr.get_matrix()

        # ANSI 颜色定义（可自定义）
        BLACK = '\033[48;2;0;0;0m  \033[0m'  # 背景黑
        WHITE = '\033[48;2;255;255;255m  \033[0m'  # 背景白
        # 或使用简写：
        # BLACK = '\033[40m  \033[0m'
        # WHITE = '\033[47m  \033[0m'

        # ✅ 自定义你喜欢的颜色（RGB）
        DARK_GREEN = '\033[48;2;0;100;0m  \033[0m'  # 深绿模块
        LIGHT_YELLOW = '\033[48;2;255;255;200m  \033[0m'  # 浅黄背景

        # 选择你想要的样式：
        module_dark = DARK_GREEN  # 二维码“黑块”颜色
        module_light = WHITE  # 二维码“白块”颜色

        print("\n" + "=" * 50)
        print("🔍 请扫描二维码（终端已清屏）...")
        print("=" * 50)

        # 打印带颜色的二维码
        for row in matrix:
            line = ""
            for cell in row:
                line += module_dark if cell else module_light
            print("  " + line)  # 左侧加空格模拟边框位置感

        print("\n" + "-" * 50)
        print(f"📌 数据预览: {repr(data[:60] + '...' if len(data) > 60 else data)}")
        print("-" * 50)

    def send_file(self, filepath, filename):
        """
        发送单个文件：
        1. 先发路径元信息 (PATH:)
        2. 再分块发送代码 (FILE:|LINE:)
        """
        # 1. 发送文件路径
        path_info = f"PATH:{filename}"
        print(f"\n📤 开始发送文件: {filename}")
        self.generate_and_print_qr(path_info)
        time.sleep(INTERVAL)

        # 2. 读取文件内容
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ 无法读取文件 {filepath}: {e}")
            return

        # 3. 分块发送
        for i in range(0, len(lines), LINES_PER_QR):
            chunk = lines[i:i + LINES_PER_QR]
            start_line = i
            data = f"FILE:{filename}|LINE:{start_line}\n" + ''.join(chunk)

            print(f"📨 发送块: {filename} 第 {start_line}-{start_line + len(chunk)-1} 行")
            self.generate_and_print_qr(data)
            time.sleep(INTERVAL)  # 等待扫码

    @staticmethod
    def get_all_files(directory):
        """递归获取目录下所有文件的相对路径"""
        all_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, directory)
                all_files.append(rel_path)
        return all_files

    def start(self):
        """主流程启动"""
        if not os.path.exists(self.folder_path):
            print(f"❌ 错误：目录不存在: {self.folder_path}")
            return

        py_files = [
            f for f in self.get_all_files(self.folder_path)
            if f.endswith('.py')
        ]

        print(f"📁 找到 {len(py_files)} 个 .py 文件: {py_files}")

        if not py_files:
            print("⚠️  警告：未找到任何 .py 文件")
            return

        print("\n🚀 开始发送文件...每个二维码显示 {INTERVAL} 秒，请用扫码设备扫描终端。")

        for filename in py_files:
            filepath = os.path.join(self.folder_path, filename)
            self.send_file(filepath, filename)

        print("\n✅ 所有文件发送完毕！")


# ==================== 程序入口 ====================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python sender.py <source_folder_path>")
        print("示例: python sender.py ./my_python_code/")
        sys.exit(1)

    folder_path = sys.argv[1]
    app = QRDisplay(folder_path=folder_path)
    app.start()