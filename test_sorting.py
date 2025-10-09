"""
测试任务信息排序功能
"""

import requests
import json
import time

def test_taskinfo_sorting():
    """测试任务信息排序功能"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试任务信息排序功能...")
    
    # 1. 登录获取token
    response = requests.post(f"{base_url}/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin"
    })
    
    if response.status_code != 200:
        print("❌ 登录失败")
        return
    
    data = response.json()
    token = data["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ 登录成功")
    
    # 2. 创建测试任务信息
    test_tasks = [
        {
            "task_name": f"测试任务A_{int(time.time())}",
            "map_id": "test-map-id",  # 需要先创建地图
            "robot_id": "test-robot-id",  # 需要先创建机器人
            "task_order": 3,
            "task_res_prior": 5,
            "task_int_prior": 2
        },
        {
            "task_name": f"测试任务B_{int(time.time())}",
            "map_id": "test-map-id",
            "robot_id": "test-robot-id",
            "task_order": 1,
            "task_res_prior": 8,
            "task_int_prior": 4
        },
        {
            "task_name": f"测试任务C_{int(time.time())}",
            "map_id": "test-map-id",
            "robot_id": "test-robot-id",
            "task_order": 2,
            "task_res_prior": 3,
            "task_int_prior": 6
        }
    ]
    
    print("\n📋 测试排序参数验证...")
    
    # 3. 测试无效的排序字段
    response = requests.get(f"{base_url}/api/v1/taskinfos/?sort_by=invalid_field", headers=headers)
    print(f"无效排序字段测试: {response.status_code} - {response.json().get('message', '')}")
    
    # 4. 测试无效的排序顺序
    response = requests.get(f"{base_url}/api/v1/taskinfos/?sort_order=invalid", headers=headers)
    print(f"无效排序顺序测试: {response.status_code} - {response.json().get('message', '')}")
    
    # 5. 测试有效的排序参数
    print("\n📊 测试有效排序参数...")
    
    sort_tests = [
        ("task_order", "asc", "按任务顺序正序"),
        ("task_order", "desc", "按任务顺序反序"),
        ("task_res_prior", "asc", "按响应优先级正序"),
        ("task_res_prior", "desc", "按响应优先级反序"),
        ("task_int_prior", "asc", "按打断优先级正序"),
        ("task_int_prior", "desc", "按打断优先级反序"),
    ]
    
    for sort_by, sort_order, description in sort_tests:
        response = requests.get(
            f"{base_url}/api/v1/taskinfos/?sort_by={sort_by}&sort_order={sort_order}&page=1&size=10",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data["data"]["items"]
            print(f"✅ {description}: 获取到 {len(items)} 个任务")
            
            # 显示排序结果
            if items:
                print(f"   排序字段 {sort_by} 的值: {[item[sort_by] for item in items]}")
        else:
            print(f"❌ {description}: {response.status_code} - {response.json().get('message', '')}")
    
    print("\n🎉 排序功能测试完成！")

if __name__ == "__main__":
    test_taskinfo_sorting()
