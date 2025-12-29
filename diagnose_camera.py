import sys
import cv2

print(f"OpenCV Version: {cv2.__version__}")
print("GStreamer Support:", "YES" if cv2.getBuildInformation().find("GSTREAMER") >= 0 else "NO")

print("\n--- 尝试简单的 GStreamer 测试 ---")
# 一个最简单的测试管道，不涉及摄像头，只生成测试信号
test_pipeline = "videotestsrc ! videoconvert ! appsink drop=1"
cap = cv2.VideoCapture(test_pipeline, cv2.CAP_GSTREAMER)

if cap.isOpened():
    print("✅ GStreamer 基础功能正常 (videotestsrc)")
    ret, frame = cap.read()
    if ret:
        print(f"   读取帧成功: {frame.shape}")
    else:
        print("   无法读取帧")
    cap.release()
else:
    print("❌ GStreamer 基础功能失败 (无法加载 videotestsrc)")
    print("   原因可能是: 缺少 gstreamer1.0-plugins-base 或 opencv 未编译 GStreamer 支持")

print("\n--- 尝试 Libcamera GStreamer 测试 ---")
# 检查 libcamerasrc 是否存在
camera_pipeline = "libcamerasrc ! video/x-raw,width=640,height=480 ! videoconvert ! appsink drop=1"
cap2 = cv2.VideoCapture(camera_pipeline, cv2.CAP_GSTREAMER)

if cap2.isOpened():
    print("✅ libcamerasrc 管道初始化成功")
    ret, frame = cap2.read()
    if ret:
        print(f"   摄像头读取成功: {frame.shape}")
    else:
        print("   ❌ 管道已打开，但无法读取帧 (可能流协商失败)")
else:
    print("❌ libcamerasrc 管道初始化失败")
    print("   可能原因: ")
    print("   1. 未安装 'gstreamer1.0-libcamera'")
    print("   2. 摄像头正被其他程序占用")
    print("   3. 排线接触不良 (即使 rpicam-hello 能跑，有时也不稳定)")
