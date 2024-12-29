from flask import Flask, jsonify, request
import json
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

def send_line_notify(message, token):
    """
    發送 LINE 通知
    :param message: 要傳送的訊息內容
    :param token: LINE Notify 存取權杖
    """
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "message": message
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("通知已成功發送！")
    else:
        print(f"發送失敗，錯誤代碼：{response.status_code}")

# Load data from JSON file
def load_data():
    try:
        with open("data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save data to JSON file
def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

# Load shelf life data
def load_shelf_life():
    try:
        with open("shelf_life.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save shelf life data
def save_shelf_life(data):
    with open("shelf_life.json", "w") as file:
        json.dump(data, file, indent=4)

# RESTful API to get data
@app.route('/api/items', methods=['GET'])
def get_items():
    data = load_data()
    filtered_data = [item for item in data if not (item["stored_time"] and item["taken_time"])]
    if filtered_data:
        return jsonify({"message": "Items found", "data": filtered_data}), 200
    else:
        return jsonify({"message": "No items found"}), 404

# RESTful API to add a new item
@app.route('/api/items', methods=['POST'])
def add_item():
    new_item = request.get_json()
    if not new_item or "name" not in new_item or "stored_time" not in new_item:
        return jsonify({"message": "Invalid data"}), 400

    data = load_data()
    new_index = len(data) + 1
    new_item_entry = {
        "index": new_index,
        "name": new_item["name"],
        "stored_time": new_item["stored_time"],
        "taken_time": None
    }
    data.append(new_item_entry)
    save_data(data)
    return jsonify({"message": "Item added successfully", "data": new_item_entry}), 201

# RESTful API to update an item
@app.route('/api/items/<int:index>', methods=['PUT'])
def update_item(index):
    data = load_data()
    item = next((item for item in data if item["index"] == index), None)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    updated_data = request.get_json()
    if not updated_data or "taken_time" not in updated_data:
        return jsonify({"message": "Invalid data"}), 400

    item["taken_time"] = updated_data["taken_time"]
    save_data(data)
    return jsonify({"message": "Item updated successfully", "data": item}), 200

# New API to process and check items
@app.route('/api/check-items', methods=['GET'])
def check_items():
    data = load_data()
    shelf_life = load_shelf_life()
    access_token = "9viUbetG6iKh2wqJS9cT2gcKhbNOJTrrNjnhxFdNXEw"

    # 預設值，防止未分配錯誤
    name = "未知物品"
    expiration_time = None

    for item in data:
        if item["stored_time"] and not item["taken_time"]:
            stored_time = datetime.strptime(item["stored_time"], "%Y-%m-%dT%H:%M:%S")
            name = item["name"]
            max_hours = shelf_life.get(name)

            if max_hours is not None:
                expiration_time = stored_time + timedelta(hours=max_hours)
                if datetime.now() > expiration_time:
                    message = f"物品 {name} 已過期！"
                    send_line_notify(message, access_token)
                    return jsonify({
                        "message": "Valid item found",
                        "name": name,
                        "expires_in": (expiration_time - datetime.now()).total_seconds() // 3600
                    }), 200

    # 如果無有效物品，返回 404
    return jsonify({
        "message": "No valid items found",
        "name": name,
        "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "expires_in": expiration_time if expiration_time else "未知"
    }), 404

# RESTful API to get shelf life data
@app.route('/api/shelf-life', methods=['GET'])
def get_shelf_life():
    shelf_life = load_shelf_life()
    return jsonify({"message": "Shelf life data", "data": shelf_life}), 200

# RESTful API to add or update shelf life data
@app.route('/api/shelf-life', methods=['POST'])
def add_or_update_shelf_life():
    new_data = request.get_json()
    if not new_data or "name" not in new_data or "hours" not in new_data:
        return jsonify({"message": "Invalid data"}), 400

    shelf_life = load_shelf_life()
    shelf_life[new_data["name"]] = new_data["hours"]
    save_shelf_life(shelf_life)
    return jsonify({"message": "Shelf life updated", "data": {new_data["name"]: new_data["hours"]}}), 200

if __name__ == "__main__":
    app.run(debug=True)
