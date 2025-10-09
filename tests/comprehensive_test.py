"""
博实智能巡检平台 - 全面功能测试脚本
使用 admin/admin 账号测试所有功能模块
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List
from datetime import datetime


class ComprehensiveTester:
    """全面功能测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.token = None
        self.user_id = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": []
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """记录测试结果"""
        self.test_results["total"] += 1
        if success:
            self.test_results["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results["failed"] += 1
            status = "❌ FAIL"
        
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results["details"].append(result)
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple[bool, Dict, int]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
        try:
            async with self.session.request(
                method, url, 
                json=data, 
                headers=request_headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()
                return True, response_data, response.status
        except Exception as e:
            return False, {"error": str(e)}, 0
    
    async def test_auth_module(self):
        """测试认证模块"""
        print("\n🔐 测试认证模块...")
        
        # 1. 测试登录
        success, data, status = await self.make_request(
            "POST", "/api/v1/auth/login",
            {"username": "admin", "password": "admin"}
        )
        
        if success and status == 200 and data.get("code") == 200:
            self.token = data["data"]["access_token"]
            self.user_id = data["data"]["user"]["id"]
            self.log_test("用户登录", True, f"Token: {self.token[:20]}...")
        else:
            self.log_test("用户登录", False, f"状态码: {status}, 响应: {data}")
            return False
        
        # 2. 测试获取当前用户信息
        headers = {"Authorization": f"Bearer {self.token}"}
        success, data, status = await self.make_request(
            "GET", "/api/v1/auth/me", headers=headers
        )
        
        if success and status == 200:
            self.log_test("获取用户信息", True, f"用户: {data['data']['username']}")
        else:
            self.log_test("获取用户信息", False, f"状态码: {status}")
        
        return True
    
    async def test_user_module(self):
        """测试用户管理模块"""
        print("\n👥 测试用户管理模块...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 1. 测试获取用户列表
        success, data, status = await self.make_request(
            "GET", "/api/v1/users/?page=1&size=10", headers=headers
        )
        
        if success and status == 200:
            users = data["data"]["items"]
            self.log_test("获取用户列表", True, f"共 {len(users)} 个用户")
        else:
            self.log_test("获取用户列表", False, f"状态码: {status}")
        
        # 2. 测试创建用户
        test_user_data = {
            "username": f"testuser_{int(time.time())}",
            "password": "testpass123",
            "mobile": "13800138000",
            "email": "test@example.com",
            "role": "user"
        }
        
        success, data, status = await self.make_request(
            "POST", "/api/v1/users/", test_user_data, headers
        )
        
        if success and status == 200:
            created_user_id = data["data"]["id"]
            self.log_test("创建用户", True, f"用户ID: {created_user_id}")
            
            # 3. 测试更新用户
            update_data = {
                "mobile": "13800138001",
                "email": "updated@example.com"
            }
            
            success, data, status = await self.make_request(
                "PUT", f"/api/v1/users/{created_user_id}", update_data, headers
            )
            
            if success and status == 200:
                self.log_test("更新用户", True, "用户信息已更新")
            else:
                self.log_test("更新用户", False, f"状态码: {status}")
            
            # 4. 测试删除用户
            success, data, status = await self.make_request(
                "DELETE", f"/api/v1/users/{created_user_id}", headers=headers
            )
            
            if success and status == 200:
                self.log_test("删除用户", True, "用户已删除")
            else:
                self.log_test("删除用户", False, f"状态码: {status}")
        else:
            self.log_test("创建用户", False, f"状态码: {status}")
    
    async def test_map_module(self):
        """测试地图管理模块"""
        print("\n🗺️ 测试地图管理模块...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 1. 测试创建地图
        map_data = {
            "map_name": f"测试地图_{int(time.time())}",
            "map_image_url": "https://example.com/map.jpg",
            "map_scale": 1.5,
            "map_center_x": 100.0,
            "map_center_y": 200.0
        }
        
        success, data, status = await self.make_request(
            "POST", "/api/v1/maps/", map_data, headers
        )
        
        if success and status == 200:
            map_id = data["data"]["id"]
            self.log_test("创建地图", True, f"地图ID: {map_id}")
            
            # 2. 测试获取地图列表
            success, data, status = await self.make_request(
                "GET", "/api/v1/maps/?page=1&size=10", headers=headers
            )
            
            if success and status == 200:
                maps = data["data"]["items"]
                self.log_test("获取地图列表", True, f"共 {len(maps)} 个地图")
            else:
                self.log_test("获取地图列表", False, f"状态码: {status}")
            
            # 3. 测试获取地图详情
            success, data, status = await self.make_request(
                "GET", f"/api/v1/maps/{map_id}", headers=headers
            )
            
            if success and status == 200:
                self.log_test("获取地图详情", True, f"地图名称: {data['data']['map_name']}")
            else:
                self.log_test("获取地图详情", False, f"状态码: {status}")
            
            # 4. 测试更新地图
            update_data = {
                "map_name": f"更新地图_{int(time.time())}",
                "map_scale": 2.0
            }
            
            success, data, status = await self.make_request(
                "PUT", f"/api/v1/maps/{map_id}", update_data, headers
            )
            
            if success and status == 200:
                self.log_test("更新地图", True, "地图信息已更新")
            else:
                self.log_test("更新地图", False, f"状态码: {status}")
            
            # 5. 测试地图统计
            success, data, status = await self.make_request(
                "GET", "/api/v1/maps/stats/summary", headers=headers
            )
            
            if success and status == 200:
                self.log_test("获取地图统计", True, f"统计信息: {data['data']}")
            else:
                self.log_test("获取地图统计", False, f"状态码: {status}")
            
            return map_id
        else:
            self.log_test("创建地图", False, f"状态码: {status}")
            return None
    
    async def test_robot_module(self, map_id: str = None):
        """测试机器人管理模块"""
        print("\n🤖 测试机器人管理模块...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 1. 测试创建机器人
        robot_data = {
            "robot_name": f"测试机器人_{int(time.time())}",
            "robot_info": {
                "type": "patrol",
                "status": "active",
                "battery": 85,
                "location": {"x": 100, "y": 200}
            }
        }
        
        success, data, status = await self.make_request(
            "POST", "/api/v1/robots/", robot_data, headers
        )
        
        if success and status == 200:
            robot_id = data["data"]["id"]
            self.log_test("创建机器人", True, f"机器人ID: {robot_id}")
            
            # 2. 测试获取机器人列表
            success, data, status = await self.make_request(
                "GET", "/api/v1/robots/?page=1&size=10", headers=headers
            )
            
            if success and status == 200:
                robots = data["data"]["items"]
                self.log_test("获取机器人列表", True, f"共 {len(robots)} 个机器人")
            else:
                self.log_test("获取机器人列表", False, f"状态码: {status}")
            
            # 3. 测试机器人名称模糊匹配
            success, data, status = await self.make_request(
                "GET", "/api/v1/robots/?robot_name=测试", headers=headers
            )
            
            if success and status == 200:
                robots = data["data"]["items"]
                self.log_test("机器人模糊匹配", True, f"匹配到 {len(robots)} 个机器人")
            else:
                self.log_test("机器人模糊匹配", False, f"状态码: {status}")
            
            # 4. 测试更新机器人
            update_data = {
                "robot_name": f"更新机器人_{int(time.time())}",
                "robot_info": {
                    "type": "patrol",
                    "status": "maintenance",
                    "battery": 90
                }
            }
            
            success, data, status = await self.make_request(
                "PUT", f"/api/v1/robots/{robot_id}", update_data, headers
            )
            
            if success and status == 200:
                self.log_test("更新机器人", True, "机器人信息已更新")
            else:
                self.log_test("更新机器人", False, f"状态码: {status}")
            
            # 5. 测试删除机器人
            success, data, status = await self.make_request(
                "DELETE", f"/api/v1/robots/{robot_id}", headers=headers
            )
            
            if success and status == 200:
                self.log_test("删除机器人", True, "机器人已删除")
            else:
                self.log_test("删除机器人", False, f"状态码: {status}")
        else:
            self.log_test("创建机器人", False, f"状态码: {status}")
    
    async def test_point_module(self, map_id: str):
        """测试巡检点管理模块"""
        print("\n📍 测试巡检点管理模块...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 1. 测试创建巡检点
        point_data = {
            "point_name": f"测试巡检点_{int(time.time())}",
            "map_id": map_id,
            "point_actions": {
                "actions": [
                    {"type": "check", "description": "检查设备状态", "duration": 30},
                    {"type": "photo", "description": "拍照记录", "duration": 10},
                    {"type": "measure", "description": "测量温度", "duration": 15}
                ],
                "total_duration": 55
            }
        }
        
        success, data, status = await self.make_request(
            "POST", "/api/v1/points/", point_data, headers
        )
        
        if success and status == 200:
            point_id = data["data"]["id"]
            self.log_test("创建巡检点", True, f"巡检点ID: {point_id}")
            
            # 2. 测试获取地图巡检点列表
            success, data, status = await self.make_request(
                "GET", f"/api/v1/points/map/{map_id}?page=1&size=10", headers=headers
            )
            
            if success and status == 200:
                points = data["data"]["items"]
                self.log_test("获取巡检点列表", True, f"共 {len(points)} 个巡检点")
            else:
                self.log_test("获取巡检点列表", False, f"状态码: {status}")
            
            # 3. 测试巡检点名称模糊匹配
            success, data, status = await self.make_request(
                "GET", f"/api/v1/points/map/{map_id}?point_name=测试", headers=headers
            )
            
            if success and status == 200:
                points = data["data"]["items"]
                self.log_test("巡检点模糊匹配", True, f"匹配到 {len(points)} 个巡检点")
            else:
                self.log_test("巡检点模糊匹配", False, f"状态码: {status}")
            
            # 4. 测试更新巡检点
            update_data = {
                "point_name": f"更新巡检点_{int(time.time())}",
                "point_actions": {
                    "actions": [
                        {"type": "check", "description": "检查设备状态", "duration": 30},
                        {"type": "photo", "description": "拍照记录", "duration": 10}
                    ],
                    "total_duration": 40
                }
            }
            
            success, data, status = await self.make_request(
                "PUT", f"/api/v1/points/{point_id}", update_data, headers
            )
            
            if success and status == 200:
                self.log_test("更新巡检点", True, "巡检点信息已更新")
            else:
                self.log_test("更新巡检点", False, f"状态码: {status}")
            
            # 5. 测试获取巡检点统计
            success, data, status = await self.make_request(
                "GET", f"/api/v1/points/map/{map_id}/stats/summary", headers=headers
            )
            
            if success and status == 200:
                self.log_test("获取巡检点统计", True, f"统计信息: {data['data']}")
            else:
                self.log_test("获取巡检点统计", False, f"状态码: {status}")
            
            # 6. 测试删除巡检点
            success, data, status = await self.make_request(
                "DELETE", f"/api/v1/points/{point_id}", headers=headers
            )
            
            if success and status == 200:
                self.log_test("删除巡检点", True, "巡检点已删除")
            else:
                self.log_test("删除巡检点", False, f"状态码: {status}")
        else:
            self.log_test("创建巡检点", False, f"状态码: {status}")
    
    async def test_ros2_module(self):
        """测试ROS2模块"""
        print("\n🔧 测试ROS2模块...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 1. 测试获取ROS2状态
        success, data, status = await self.make_request(
            "GET", "/api/v1/ros2/status", headers=headers
        )
        
        if success and status == 200:
            self.log_test("获取ROS2状态", True, f"状态: {data['data']}")
        else:
            self.log_test("获取ROS2状态", False, f"状态码: {status}")
        
        # 2. 测试获取ROS2话题列表
        success, data, status = await self.make_request(
            "GET", "/api/v1/ros2/topics", headers=headers
        )
        
        if success and status == 200:
            topics = data["data"]["topics"]
            self.log_test("获取ROS2话题列表", True, f"共 {len(topics)} 个话题")
        else:
            self.log_test("获取ROS2话题列表", False, f"状态码: {status}")
        
        # 3. 测试发布字符串消息
        success, data, status = await self.make_request(
            "POST", "/api/v1/ros2/publish/string",
            {"topic": "/test_topic", "message": "Hello ROS2!"},
            headers
        )
        
        if success and status == 200:
            self.log_test("发布ROS2字符串消息", True, "消息发布成功")
        else:
            self.log_test("发布ROS2字符串消息", False, f"状态码: {status}")
        
        # 4. 测试发布速度命令
        success, data, status = await self.make_request(
            "POST", "/api/v1/ros2/publish/cmd_vel",
            {"linear_x": 0.5, "angular_z": 0.2},
            headers
        )
        
        if success and status == 200:
            self.log_test("发布ROS2速度命令", True, "速度命令发布成功")
        else:
            self.log_test("发布ROS2速度命令", False, f"状态码: {status}")
    
    async def test_log_module(self):
        """测试日志管理模块"""
        print("\n📋 测试日志管理模块...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 1. 测试获取日志文件列表
        success, data, status = await self.make_request(
            "GET", "/api/v1/logs/files?log_date=2025-09-22", headers=headers
        )
        
        if success and status == 200:
            files = data["data"]["files"]
            self.log_test("获取日志文件列表", True, f"共 {len(files)} 个日志文件")
        else:
            self.log_test("获取日志文件列表", False, f"状态码: {status}")
        
        # 2. 测试获取日志内容
        success, data, status = await self.make_request(
            "GET", "/api/v1/logs/content?log_date=2025-09-22&log_type=app&lines=10", headers=headers
        )
        
        if success and status == 200:
            content = data["data"]["content"]
            self.log_test("获取日志内容", True, f"获取到 {len(content)} 行日志")
        else:
            self.log_test("获取日志内容", False, f"状态码: {status}")
        
        # 3. 测试搜索日志
        success, data, status = await self.make_request(
            "GET", "/api/v1/logs/search?keyword=admin&log_date=2025-09-22", headers=headers
        )
        
        if success and status == 200:
            results = data["data"]["results"]
            self.log_test("搜索日志", True, f"找到 {len(results)} 条匹配记录")
        else:
            self.log_test("搜索日志", False, f"状态码: {status}")
    
    async def test_websocket(self):
        """测试WebSocket连接"""
        print("\n🔌 测试WebSocket连接...")
        
        try:
            import websockets
            
            uri = "ws://localhost:8000/ws"
            async with websockets.connect(uri) as websocket:
                # 发送ping消息
                ping_message = {"type": "ping"}
                await websocket.send(json.dumps(ping_message))
                
                # 接收pong响应
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "pong":
                    self.log_test("WebSocket连接", True, "连接成功，收到pong响应")
                else:
                    self.log_test("WebSocket连接", False, f"收到意外响应: {data}")
                
                # 测试获取连接状态
                status_message = {"type": "get_connection_status"}
                await websocket.send(json.dumps(status_message))
                
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "connection_status":
                    self.log_test("WebSocket状态查询", True, f"连接状态: {data}")
                else:
                    self.log_test("WebSocket状态查询", False, f"收到意外响应: {data}")
                    
        except ImportError:
            self.log_test("WebSocket连接", False, "websockets库未安装，跳过WebSocket测试")
        except Exception as e:
            self.log_test("WebSocket连接", False, f"连接失败: {str(e)}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始全面功能测试...")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试目标: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. 认证测试
        if not await self.test_auth_module():
            print("❌ 认证失败，无法继续测试")
            return
        
        # 2. 用户管理测试
        await self.test_user_module()
        
        # 3. 地图管理测试
        map_id = await self.test_map_module()
        
        # 4. 机器人管理测试
        await self.test_robot_module()
        
        # 5. 巡检点管理测试
        if map_id:
            await self.test_point_module(map_id)
        
        # 6. ROS2模块测试
        await self.test_ros2_module()
        
        # 7. 日志管理测试
        await self.test_log_module()
        
        # 8. WebSocket测试
        await self.test_websocket()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 输出测试结果
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        print(f"总测试数: {self.test_results['total']}")
        print(f"通过数量: {self.test_results['passed']}")
        print(f"失败数量: {self.test_results['failed']}")
        print(f"成功率: {(self.test_results['passed'] / self.test_results['total'] * 100):.1f}%")
        print(f"测试耗时: {duration:.2f} 秒")
        
        # 输出失败详情
        failed_tests = [test for test in self.test_results['details'] if 'FAIL' in test['status']]
        if failed_tests:
            print("\n❌ 失败的测试:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        # 保存详细结果到文件
        with open(f"test_results_{int(time.time())}.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细测试结果已保存到: test_results_{int(time.time())}.json")


async def main():
    """主函数"""
    async with ComprehensiveTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    print("博实智能巡检平台 - 全面功能测试")
    print("请确保服务器已启动在 http://localhost:8000")
    print("按 Ctrl+C 可随时停止测试")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n💥 测试执行出错: {e}")
