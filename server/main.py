"""
Q1: package install
在运行前请确保安装所需依赖：
pip install qrcode[pil] pillow

说明：
- qrcode[pil]：用于生成二维码图像（PIL 支持）
- pillow：提供图像处理支持（如缩放、显示）
"""

# sender.py - A电脑运行
# 功能：遍历指定文件夹中的所有 .py 文件，将其内容分块编码为二维码，并通过 GUI 窗口逐个展示
# 使用场景：可用于向 B 设备（如手机）传输 Python 源码，通过扫码方式接收

import os                  # 用于操作文件系统（路径、读取目录等）
import qrcode              # 生成二维码的核心库
import time                # 控制时间间隔（sleep）
from PIL import Image, ImageTk  # PIL 用于图像处理；ImageTk 将 PIL 图像嵌入 Tkinter
import tkinter as tk       # 创建图形用户界面（GUI），用于显示二维码
import sys                 # 处理命令行参数


# 配置常量
INTERVAL = 2        # 每个二维码显示的时间（秒），之后切换下一个
LINES_PER_QR = 10   # 每个二维码最多包含 10 行源代码，避免数据过大无法识别


class QRDisplay:
    """
    二维码发送器主类
    负责创建窗口、生成二维码、控制显示流程
    """

    def __init__(self, folder_path):
        """
        初始化对象
        :param folder_path: 待发送的 Python 文件所在的文件夹路径
        """
        self.folder_path = folder_path  # 存储传入的目标文件夹路径
        self.root = tk.Tk()             # 创建主窗口
        self.root.title("二维码发送器")  # 设置窗口标题

        # 设置窗口大小为 400x400 像素，并定位到屏幕左上角 (0, 0)
        # 这样不会遮挡其他重要区域（比如任务栏或通知中心）
        self.root.geometry("400x400+0+0")

        # 窗口始终置顶，保证二维码不被其他窗口覆盖
        self.root.attributes('-topmost', True)

        # 创建一个 Label 组件，用于承载并显示生成的二维码图像
        self.label = tk.Label(self.root)
        self.label.pack(expand=True)  # 自动扩展填充整个窗口空间

        # 强制更新一次窗口布局，防止首次显示延迟或空白
        self.root.update()

    def generate_qr_image(self, data):
        """
        根据输入的数据生成二维码图像
        :param data: 字符串数据（如文件路径、代码片段等）
        :return: PIL.Image 对象，已调整尺寸的二维码图像
        """
        # 使用 qrcode 库生成二维码（自动选择最佳纠错等级）
        qr = qrcode.make(data)

        # 将二维码图像放大至 300x300 像素，使用高质量重采样算法（LANCZOS）
        qr = qr.resize((300, 300), Image.Resampling.LANCZOS)

        return qr  # 返回处理后的图像对象

    def display_qr(self, image):
        """
        在 Tkinter 窗口中显示 PIL 图像
        :param image: PIL.Image 类型的二维码图像
        """
        # 将 PIL 图像转换为 Tkinter 可识别的 PhotoImage 格式
        photo = ImageTk.PhotoImage(image)

        # 保留对 photo 的引用，否则会被 Python 垃圾回收导致图像消失
        self.label.image = photo

        # 把图像设置给 label 显示出来
        self.label.configure(image=photo)

        # 刷新 GUI 界面，立即生效
        self.root.update()

    def send_file(self, filepath, filename):
        """
        发送单个 Python 文件的全过程：
        1. 先发送文件路径信息（以 PATH: 开头）
        2. 再将文件内容按每 10 行一组分块，依次发送每个代码块
        :param filepath: 文件完整路径（含目录）
        :param filename: 文件名（不含路径）
        """
        # 第一步：先发送文件路径元信息
        path_info = f"PATH:{filepath}"  # 添加标识前缀 "PATH:"
        print(f"发送文件路径: {path_info}")

        # 生成二维码并显示
        qr_img = self.generate_qr_image(path_info)
        self.display_qr(qr_img)

        # 暂停 INTERVAL 秒，等待扫码设备读取
        time.sleep(INTERVAL)

        # 第二步：读取该文件的所有文本行
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()  # 一次性读取所有行，返回列表
        except Exception as e:
            # 如果文件打不开（权限问题、编码错误等），打印错误并跳过
            print(f"无法读取文件 {filepath}: {e}")
            return  # 直接退出当前文件的发送

        # 第三步：将文件内容分批发送，每批最多 LINES_PER_QR 行
        for i in range(0, len(lines), LINES_PER_QR):
            # 取出从第 i 行开始的最多 10 行代码
            chunk = lines[i:i + LINES_PER_QR]

            # 构造要编码的数据字符串：
            # 格式：FILE:<文件名>|LINE:<起始行号>\n<实际代码>
            data = f
            