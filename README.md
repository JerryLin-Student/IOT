# 專題名稱：Smart Food Saver (智慧食物守護者)
# 112453024 林煜烽
## 專題背景
隨著現代人對健康和永續發展的重視，食物浪費和食材管理變得越來越重要。然而，許多人在家中經常忘記冰箱裡的食材或食品過期，導致浪費或安全隱患。

## 專題概念
一個結合 IoT 感測器、影像辨識、數據分析 的智慧冰箱輔助系統，用於追蹤和管理食材。這套系統能夠記錄冰箱內的食材類型、數量及保存期限，並提供即時提醒和食譜建議。

## 功能
1. 食材辨識與追蹤。使用攝像頭和影像辨識技術自動記錄冰箱內放入或取出的食材。進一步追蹤食材的進出。**保鮮與過期提醒**




## 飲恨功能
* 辨識食材 : 縮小範圍水果
* 一次只能放一個水果
---
可以再增加
* 多台攝影機
* 辨識 (水果如是切好的?)
* 監控如溫濕度感測器

## 架構
### 設計

![image](https://hackmd.io/_uploads/SyylCQSHJl.png)


### 實作
1 線路將按鈕連接到另一個 GND 引腳和 GPIO 引腳 2，如下所示：
![image](https://hackmd.io/_uploads/By2HCzHBJg.png)
2.Webcam 接USB Port:
![image](https://hackmd.io/_uploads/B1NzxXSHkg.png)

## Pi WebCam 功能
PiApp(WebCam.py)
### 介紹
與 API 操作相關
1.get_unclaimed_items() 從 API 獲取未領取的物品列表。
2.update_item(index) 更新指定物品的領取時間。
3.auto_update_items()自動處理所有未領取的物品。
與檔案操作相關
4.initialize_json_file() 初始化 JSON 文件，如果文件不存在則創建新文件。
5.log_to_json(item, timestamp) 將檢測結果記錄到 JSON 文件中。
影像分類與模型相關
6.load_labels(path) 載入模型標籤。
7.set_input_tensor(interpreter, image) 設定影像數據到模型的輸入張量。
8.classify_image(interpreter, image, top_k=1)  使用模型對影像進行分類，返回分類結果。
相機操作相關
9.record_and_classify() 開始錄影，進行即時分類並顯示結果。

## Pi API 功能
FlaskApp(Api.py)
### 介紹

| 檔案 | 說明 | 
| -------- | -------- |
|data.json|物品數據存儲文件。|
|shelf_life.json|物品存放時效數據存儲文件。|

|      FlaskApp       |說明|
|---------------------|----|
| - load_data()       |從 data.json 加載物品數據|
| - save_data()       |物品數據保存到 data.json|
| - load_shelf_life() |加載存放時效數據|
| - save_shelf_life() |保存時效數據|
| + get_items()       |處理 GET /api/items，返回符合條件的物品數據。|
| + add_item()        |處理 POST /api/items，新增物品。|
| + update_item()     |處理 PUT /api/items/<int:index>，更新物品的取出時間。|
| + check_items()     |處理 GET /api/check-items，檢查有效物品。|
| + get_shelf_life()  |處理 GET /api/shelf-life，返回存放時效數據。|
| + add_or_update_shelf_life() |處理 POST /api/shelf-life，新增或更新物品的存放時效。|

### 數據存取功能
* load_data(): 從 data.json 文件中讀取物品資料。
* save_data(): 將更新的物品資料寫入 data.json。
* load_shelf_life(): 從 shelf_life.json 文件中讀取物品的可存放時效。
* save_shelf_life(): 將更新的時效資料寫入 shelf_life.json。

### RESTful API 功能
#### 1. GET /api/items
功能：返回物品列表中符合條件的物品： stored_time 有值且 taken_time 為空。
回應：若找到符合條件的物品，回傳物品資料。若無符合條件的物品，回傳 "No items found"。
#### 2. POST /api/items
功能：新增一筆物品資料。
請求參數：
name：物品名稱（必填）。
stored_time：存放時間，格式為 ISO 8601（必填）。
回應：
新增成功時，回傳新增物品資料。
若資料格式不正確，回傳 "Invalid data"。
#### 3. PUT /api/items/<int:index>
功能：更新指定 index 的物品資料，設定 taken_time。
請求參數：
taken_time：取出時間，格式為 ISO 8601（必填）。
回應：
更新成功時，回傳更新後的物品資料。
若未找到對應物品或資料格式不正確，回傳錯誤訊息。
#### 4. GET /api/check-items
功能：檢查物品是否仍在有效期內。
stored_time 有值且 taken_time 為空。
根據 shelf_life.json 中的可存放時效計算是否有效。
回應：
若找到符合條件的物品，回傳物品名稱和剩餘有效時間。
若無符合條件的物品，回傳 "No valid items found"。
#### 5. GET /api/shelf-life
功能：返回所有物品的可存放時效（以小時為單位）。
回應：
回傳 shelf_life.json 中的數據。
#### 6. POST /api/shelf-life
功能：新增或更新物品的可存放時效。
請求參數：
name：物品名稱（必填）。
hours：可存放時效，單位為小時（必填）。
回應：
新增或更新成功時，回傳更新後的物品時效。
若資料格式不正確，回傳 "Invalid data"。


## 參考
Ovie Smarterware 
美國產品募資平台 Kickstarter 分享，「Smarterware 是全世界第一個智能食物保存系統，簡單好用」
https://ovie.life/?srsltid=AfmBOoraansfYuHKejlNGUS7bWFAOUKTPi9A6KIEJRSsn3acY-TyQZj7
