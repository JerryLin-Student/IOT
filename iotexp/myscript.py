import requests

def check_items():
    url = "http://127.0.0.1:5000/api/check-items"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("成功取得資料:", response.json())
        else:
            print(f"請求失敗，狀態碼: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    check_items()