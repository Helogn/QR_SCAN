# screen_qr_scanner.py - 扫描屏幕指定区域（带可视化窗口）
"""
Q1:package install:
pip install pyzbar opencv-python pillow

Q2:安装pyzbar问题，libzbar-64.dll找不到
https://www.microsoft.com/zh-cn/download/details.aspx?id=40784

"""
import os
import mss
import cv2
import numpy as np
from pyzbar import pyzbar
import sys
import time

# ------------------ 配置区域 ------------------
MONITOR_REGION = {
    'top': 100,
    'left': 50,
    'width': 400,
    'height': 400,
}

SCAN_INTERVAL = 0.5
WINDOW_NAME = "🔍 二维码扫描监控"
SAVE_TIMEOUT = 5  # 若在5秒内未接收到新二维码，则自动保存
# ----------------------------------------------

received_data = set()
current_file_path = None
last_save_time = time.time()
received_files = {}

def parse_qr_data(data):
    try:
        if data.startswith("PATH:"):
            return 'PATH', data[5:]
        elif data.startswith("FILE:"):
            header, *content_lines = data.split('\n')
            _, filename = header.split('FILE:', 1)
            filename = filename.split('|')[0].strip()
            content = '\n'.join(content_lines)
            return 'CODE', filename, content
        else:
            return 'TEXT', None, data
    except Exception as e:
        return 'ERROR', None, str(e)

def save_current_file(dst_folder):
    global received_files, current_file_path
    if current_file_path and current_file_path in received_files:
        output_dir = dst_folder
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, os.path.basename(current_file_path))
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(''.join(received_files[current_file_path]))
        print(f"✅ 已保存: {filepath}")
        del received_files[current_file_path]

def main(dst_folder):
    global received_data, current_file_path, last_save_time

    print("🔍 屏幕二维码扫描器启动")
    print(f"监听区域: {MONITOR_REGION}")
    print(f"显示窗口: [{WINDOW_NAME}]")
    print("按 Q 键关闭窗口并停止...\n")

    # 创建显示窗口
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_GUI_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, MONITOR_REGION['width'], MONITOR_REGION['height'])

    with mss.mss() as sct:
        while True:
            # 1. 截图
            screenshot = sct.grab(MONITOR_REGION)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # 2. 识别二维码
            barcodes = pyzbar.decode(frame)

            for barcode in barcodes:
                data = barcode.data.decode('utf-8')

                if data in received_data:
                    continue
                received_data.add(data)

                dtype, *info = parse_qr_data(data)

                if dtype == 'PATH':
                    # 如果检测到新的 PATH 信息，则保存之前的文件并开始记录新文件
                    save_current_file(dst_folder)
                    current_file_path = info[0]
                    received_files[current_file_path] = []
                    print(f"📂 新建文件: {current_file_path}")
                elif dtype == 'CODE' and current_file_path:
                    filename, content = info
                    received_files[current_file_path].append(content)
                    print(f"📄 收到代码片段: {filename}")
                else:
                    print(f"💬 识别到: {data}")

                # 绘制二维码边框
                points = barcode.polygon
                pts = np.array(points, np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)

                last_save_time = time.time()

            # 如果一段时间内没有新的二维码，则保存当前文件
            if time.time() - last_save_time > SAVE_TIMEOUT:
                save_current_file()
                last_save_time = time.time()

            # ✅ 显示当前扫描画面
            cv2.imshow(WINDOW_NAME, frame)

            # 按 Q 退出
            key = cv2.waitKey(int(SCAN_INTERVAL * 1000)) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break

    cv2.destroyAllWindows()
    save_current_file()  # 确保在程序结束前保存所有数据

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python sender.py <source_folder_path>")
        sys.exit(1)

    try:
        main(sys.argv[1])
    except KeyboardInterrupt:
        print("\n\n👋 扫描被中断，正在保存文件...")

    print("🎉 所有文件保存完成！")
    