"""
测试API响应格式
"""

import requests
import json

def test_api_formats():
    """测试API响应格式"""
    base_url = "http://localhost:8000"
    
    print("🔍 测试API响应格式...")
    
    # 1. 测试登录
    print("\n1. 测试登录API:")
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin"
        })
        print(f"状态码: {response.status_code}")
        data = response.json()
        print("响应结构:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            token = data["data"]["access_token"]
            print(f"\nToken: {token[:50]}...")
            
            # 2. 测试获取用户信息
            print("\n2. 测试获取用户信息API:")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
            print(f"状态码: {response.status_code}")
            data = response.json()
            print("响应结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 3. 测试获取用户列表
            print("\n3. 测试获取用户列表API:")
            response = requests.get(f"{base_url}/api/v1/users/?page=1&size=5", headers=headers)
            print(f"状态码: {response.status_code}")
            data = response.json()
            print("响应结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 4. 测试创建地图
            print("\n4. 测试创建地图API:")
            map_data = {
                "map_name": f"测试地图_{int(time.time())}",
                "map_image_url": "https://example.com/test.jpg",
                "map_scale": 1.0,
                "map_center_x": 0.0,
                "map_center_y": 0.0
            }
            response = requests.post(f"{base_url}/api/v1/maps/", json=map_data, headers=headers)
            print(f"状态码: {response.status_code}")
            data = response.json()
            print("响应结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 5. 测试获取日志文件
            print("\n5. 测试获取日志文件API:")
            response = requests.get(f"{base_url}/api/v1/logs/files?log_date=2025-09-22", headers=headers)
            print(f"状态码: {response.status_code}")
            data = response.json()
            print("响应结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    import time
    test_api_formats()
