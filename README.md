# 專題名稱：Smart Food Saver (智慧食物守護者)                               
## 學號: 112453024 姓名: 林煜烽
# 專題背景
隨著現代人對健康和永續發展的重視，食物浪費和食材管理變得越來越重要。然而，許多人在家中經常忘記冰箱裡的食材或食品過期，導致浪費或安全隱患。

## 專題概念
一個結合 IoT 感測器、影像辨識、數據分析 的智慧冰箱輔助系統，用於追蹤和管理食材。這套系統能夠記錄冰箱內的食材類型、數量及保存期限，並提供即時提醒和食譜建議。

## 功能
食材辨識與追蹤。使用攝像頭和影像辨識技術自動記錄冰箱內放入或取出的食材。進一步追蹤食材的進出。**保鮮與過期提醒**

# 架構
## 設計圖

![image](https://hackmd.io/_uploads/SyylCQSHJl.png)


# 實作
## **1 線路將按鈕連接到另一個 GND 引腳和 GPIO 引腳 2，如下所示：**

![image](https://hackmd.io/_uploads/By2HCzHBJg.png)

## **2.Webcam 接 USB Port:**

![image](https://hackmd.io/_uploads/B1NzxXSHkg.png)

## **3.軟體安裝:**
### 使用 Python3
```
python3
```
### 安裝 OpenCV
back to root
```
cd ~/
```
install packages
```
sudo apt install git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev libatlas-base-dev python3-scipy
```
download opencv
```
git clone --depth 1 --branch 4.5.2-openvino https://github.com/opencv/opencv.git
```
go to opencv && create new file && go to new file
```
cd opencv && mkdir build && cd build
```
```
cmake –DCMAKE_BUILD_TYPE=Release –DCMAKE_INSTALL_PREFIX=/usr/local ..
```
Take a really long time
```
make -j4
```
Success:
![](https://hackmd.io/_uploads/BJluqWHGMT.png)
```
sudo make install
```
Success:
![](https://hackmd.io/_uploads/B1LnWHzMp.png)
### 安裝 Flask
```
pip install Flask
```
### 安裝 pygame
```
python3 -m pip install -U pygame --user
```
### 安裝模型框架Tensorflow Lite
```
pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl
```
### 更新及升級所有套件包
```
sudo apt-get update && sudo apt-get upgrade
```
# 啟動程式
## Step 1 : 編輯 Crontab (定時程式)
```
crontab -e
```
這行代表每 1 小時執行一次腳本，具體含義：
```
* 1 * * * /usr/bin/python3 /user/iotexp/myscript.py
```
## Step 2 : 啟動 Api.py (API程式)
另開一個Terminal 
```
/user/iotexp/Api.py
```
## Step 3 : 啟動 WebCam.py (Pi主程式)
```
/user/iotexp/Api.py
```

# Demo
## **4.放入物品 按下不放(模擬打開冰箱) 放開時(模擬關上冰箱):**

![image](https://hackmd.io/_uploads/rJd1vNRByg.png)

## **5.取出物品 按下不放(模擬打開冰箱) 放開時(模擬關上冰箱):** 

![image](https://hackmd.io/_uploads/Hk5zv40rJg.png)

## **6.Line Notify:**

![image](https://hackmd.io/_uploads/Syz1YVRB1e.png)



## 參考
Ovie Smarterware 
美國產品募資平台 Kickstarter 分享，「Smarterware 是全世界第一個智能食物保存系統，簡單好用」
https://ovie.life/?srsltid=AfmBOoraansfYuHKejlNGUS7bWFAOUKTPi9A6KIEJRSsn3acY-TyQZj7

**Flask** https://pypi.org/project/Flask/

**Pygame** https://www.pygame.org/wiki/GettingStarted

**使用Google Teachable Machine 來實現Raspberry Pi 4 的影像分類推論** https://blog.cavedu.com/2020/11/26/google-teachable-machine-raspberry-pi-4/

## 飲恨功能
* 辨識食材 : 縮小範圍水果
* 一次只能放一個水果
---
可以再增加
* 多台攝影機
* 辨識 (水果如是切好的?)
* 監控如溫濕度感測器
