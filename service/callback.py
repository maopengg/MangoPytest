from flask import Flask, request, jsonify

app = Flask(__name__)

data_store = {}


# GET 接口
@app.route('/data', methods=['GET'])
def get_data():
    item_id = request.args.get('id', type=int)  # 从查询参数中获取 id
    item = data_store.get(item_id)
    if item:
        return jsonify({'item_id': item_id, 'data': item}), 200
    else:
        return jsonify({'error': 'Item not found'}), 404


# POST 接口
@app.route('/data', methods=['POST'])
def create_data():
    new_item = request.json
    item_id = len(data_store) + 1
    data_store[item_id] = new_item
    return jsonify({'item_id': item_id, 'data': new_item}), 201


# PUT 接口
@app.route('/data', methods=['PUT'])
def update_data():
    item_id = request.args.get('id', type=int)  # 从查询参数中获取 id
    if item_id in data_store:
        updated_item = request.json
        data_store[item_id] = updated_item
        return jsonify({'item_id': item_id, 'data': updated_item}), 200
    else:
        return jsonify({'error': 'Item not found'}), 404


# DELETE 接口
@app.route('/data', methods=['DELETE'])
def delete_data():
    item_id = request.args.get('id', type=int)  # 从查询参数中获取 id
    if item_id in data_store:
        del data_store[item_id]
        return jsonify({'message': 'Item deleted successfully'}), 200
    else:
        return jsonify({'error': 'Item not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
