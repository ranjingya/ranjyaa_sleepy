import json

import redis
from flask import Flask, request, jsonify
from flask_socketio import SocketIO

from logger_config import create_custom_logger

app = Flask(__name__)
logger = create_custom_logger(__name__)

"""

这里用到了redis，如果不需要的话直接用一个全局变量存储对应的数据即可
e.g.
win_data = {"title": None, "time": None}
mobile_data = {"title": None, "time": None}
visit_num = 0

"""

# TODO 改成你自己的前端地址
socketio = SocketIO(app, cors_allowed_origins=["http://ranjyaa-alive.ranjyaa.top",
                                               "http://localhost:5173"])

# TODO 改成你自己的
redis_client = redis.StrictRedis(host='redis host', port=6379, password="redis password",
                                 db=0, decode_responses=True)

# ALLOWED_SOCKET_IPS = ["localhost", "127.0.0.1"]

# TODO 都改成你自己的
API_KEY_UPLOAD = "API_KEY"
WIN_REDIS_PREFIX = "redis key"
MOBILE_REDIS_PREFIX = "redis key"
VISIT_NUM_REDIS_PREFIX = "redis key"

EMPTY_DATA = {"title": None, "time": None}


@socketio.on('connect')
def handle_connect():
    real_ip = request.headers.get('X-Real-IP') or request.headers.get('X-Forwarded-For', request.remote_addr)
    logger.info(f"socket请求ip: {real_ip}")
    # if real_ip not in ALLOWED_SOCKET_IPS:
    #     logger.error(f"非法socket请求ip: {real_ip}")
    #     return False
    # 连接成功立即发送数据
    data = get_redis_data()
    socketio.emit('title_update', data)
    logger.info("socket连接成功")
    redis_client.incr(VISIT_NUM_REDIS_PREFIX)


def get_redis_data():
    data = {"win": None, "mobile": None, "visit_num": None}
    latest_win = redis_client.get(WIN_REDIS_PREFIX)
    latest_mobile = redis_client.get(MOBILE_REDIS_PREFIX)
    data["win"] = json.loads(latest_win) if latest_win else EMPTY_DATA
    data["mobile"] = json.loads(latest_mobile) if latest_mobile else EMPTY_DATA
    data["visit_num"] = redis_client.get(VISIT_NUM_REDIS_PREFIX) or 0
    return data


@app.route('/api/upload', methods=['POST'])
def upload():
    """接收客户端上传的数据"""
    api_key = request.headers.get('x-api-key')
    if api_key != API_KEY_UPLOAD:
        return jsonify({"code": 401, "msg": "Unauthorized", "data": None}), 401

    data = request.json["data"]
    title_type = request.json["type"]
    if data:
        if title_type == 0:
            redis_client.set(WIN_REDIS_PREFIX, json.dumps(data), ex=60 * 20 * 12)
        elif title_type == 1:
            redis_client.set(MOBILE_REDIS_PREFIX, json.dumps(data), ex=60 * 60 * 12)
        redis_data = get_redis_data()
        socketio.emit('title_update', redis_data)

        return jsonify({"code": 0, "msg": "success", "data": None}), 200
    return jsonify({"code": 400, "msg": "No data received", "data": None}), 400


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5002)
