
        cv2.polylines(frame, [pts], True, (0,255,0), 2)
        return data
    return None

def parse_data(data):
    try:
        header, content = data.split('\n', 1)
        _, filename = header.split('FILE:')
        filename = filename.split('|')[0]
        return filename, content
    except:
        return None, None

def main():
    received = {}
    cap = cv2.VideoCapture(0)  # 假设你用摄像头拍A电脑屏幕

    print("开始扫描二维码（按 Q 退出）...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        data = decode_qr_from_frame(frame)
        if data:
            filename, content = parse_data(data)
            if filename:
                if filename not in received:
                    received[filename] = []
                if content not in received[filename]:  # 去重
                    received[filename].append(content)
                    print(f"收到: {filename}")

        cv2.imshow("Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # 保存文件
    for filename, chunks in received.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(''.join(chunks))
        print(f"已保存: {filepath}")

if __name__ == "__main__":
    main()