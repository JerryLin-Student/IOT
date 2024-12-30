import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter
import datetime
from gpiozero import Button
import json
from datetime import datetime
import requests
# 定義 JSON 文件路徑
json_file_path = "detected_items.json"

# API 端點設置
BASE_URL = "http://127.0.0.1:5000/api/items"

# 新增物品
def add_item(name):
    url = BASE_URL
    stored_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    payload = {
        "name": name,
        "stored_time": stored_time
    }
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        print(f"已新增物品 {name}，儲存時間：{stored_time}")
    else:
        print(f"新增物品失敗，錯誤代碼：{response.status_code}")

def get_unclaimed_items():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        items = response.json().get("data", [])
        # 過濾已領取的物品 (有 taken_time 的物品)
        unclaimed_items = [item for item in items if not item["taken_time"]]
        return unclaimed_items
    else:
        print(f"查詢失敗，錯誤代碼：{response.status_code}")
        return []

# 更新物品領取時間
def update_item(index):
    url = f"{BASE_URL}/{index}"
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    payload = {"taken_time": current_time}
    response = requests.put(url, json=payload)

    if response.status_code == 200:
        print(f"物品編號 {index} 已成功更新。")
    else:
        print(f"更新失敗，錯誤代碼：{response.status_code}")

# 自動處理未領取物品
def auto_update_items():
    items = get_unclaimed_items()
    if not items:
        print("目前無未領取的物品。")
        return

    for item in items:
        index = item["index"]
        name = item["name"]
        stored_time = item["stored_time"]
        print(f"正在更新物品 {name}（編號: {index}, 儲存時間: {stored_time}）...")
        update_item(index)

# 初始化 JSON 文件（如果文件不存在，則創建）
def initialize_json_file():
    try:
        with open(json_file_path, 'r') as f:
            json.load(f)  # 嘗試讀取現有 JSON 文件
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或 JSON 格式錯誤，重新創建文件
        with open(json_file_path, 'w') as f:
            json.dump([], f)

# 將檢測結果寫入 JSON 文件
def log_to_json(item, timestamp):
    # 加載現有數據
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # 新的檢測記錄
    new_entry = {
        "item": item,
        "timestamp": timestamp
    }

    # 添加到數據中
    data.append(new_entry)

    # 將數據寫回文件
    with open(json_file_path, 'w') as f:
        json.dump(data, f, indent=4)

# 初始化 JSON 文件
initialize_json_file()

# 載入標籤檔案
def load_labels(path):
    with open(path, 'r') as f:
        return [line.strip().split(maxsplit=1)[1] for line in f.readlines()]

# 設定輸入彈性
def set_input_tensor(interpreter, image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image[0]  # 批量維度取第一個

# 進行分類
def classify_image(interpreter, image, top_k=1):
    set_input_tensor(interpreter, image)
    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)
    ordered = np.argpartition(-output, top_k)
    return [(i, output[i]) for i in ordered[:top_k]]

# 模型和標籤路徑
data_folder = "/home/user/iotexp/model"
model_path = f"{data_folder}/model.tflite"
label_path = f"{data_folder}/labels.txt"
before_itmes = None

# 初始化解釋器
interpreter = Interpreter(model_path)
interpreter.allocate_tensors()
_, height, width, _ = interpreter.get_input_details()[0]['shape']

# 載入標籤
labels = load_labels(label_path)

# GPIO Zero Button 初始化
button = Button(2)  # GPIO 重要按鈕連接在 GPIO2

# 初始化攝像頭
camera = cv2.VideoCapture(0)  # 使用第一個攝像頭設備
if not camera.isOpened():
    print("無法打開攝像頭！")
    exit()

print("按下按鈕以啟動錄像與辨識，釋放按鈕以停止。按下 'q' 離開程式。")

# 該變量用於記錄最後一個結果
final_result = None
before_result = None

# 定義錄像功能
def record_and_classify():
    global final_result
    global before_result

    print("Recording started...")
    try:
        while button.is_pressed:
            # 捕獲幕影
            ret, frame = camera.read()
            if not ret:
                print("無法讀取攝像頭幕影！")
                break

            # 調整圖像大小並預處理
            resized_frame = cv2.resize(frame, (width, height))
            input_data = np.expand_dims(resized_frame, axis=0).astype(np.uint8)

            # 分類
            results = classify_image(interpreter, input_data, top_k=1)
            label_id, prob = results[0]
            classification_label = labels[label_id]
            final_result = f"{classification_label}"

            # 在原始圖像上添加標示框和標籤
            start_point = (50, 50)  # 左上角
            end_point = (frame.shape[1] - 50, frame.shape[0] - 50)  # 右下角
            color = (0, 255, 0)  # 綠色框
            thickness = 2  # 框線的粗細

            # 繪制標示框
            cv2.rectangle(frame, start_point, end_point, color, thickness)

            # 在框上顯示分類結果
            cv2.putText(frame, f"{classification_label} ({prob:.2%})", (start_point[0], start_point[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 顯示圖像
            cv2.imshow("TFLite USB Camera", frame)

            # 判斷是否按下 'q' 離開程序
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting program...")
                camera.release()
                cv2.destroyAllWindows()
                exit()
    finally:
        print("Recording stopped. ")
        print(before_result) 
        #print(classification_label)	
        if final_result:
            print("Final Result:", final_result ,)

        if final_result == "Nothing" and before_result is None:
            # 不執行任何動作
            print("Nothing detected. No action.")

        if before_result in [None, "Nothing"] and final_result != "Nothing":
            # 動作邏輯
            print(f"Action triggered! Detected: {final_result}")
            # 記錄到 JSON 文件
            add_item(final_result)
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            log_to_json(final_result, current_time)

        if before_result not in [None, "Nothing"] and final_result == "Nothing":
            # 動作邏輯
            print(f"Action triggered! take away : {before_result} Now : {final_result}")
            # 記錄到 JSON 文件
            auto_update_items()
            #current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #log_to_json(final_result, current_time)
        before_result=final_result	

# 保持程式運行
try:
    while True:
        if button.is_pressed:
            record_and_classify()
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    camera.release()
    cv2.destroyAllWindows()
