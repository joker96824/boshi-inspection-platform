#!/usr/bin/env python3
"""
博实智能巡检平台 - 系统健康检查脚本

检查应用程序、数据库、ROS2等组件的状态
"""

import asyncio
import sys
import httpx
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from app.config.settings import settings
from app.config.database import engine
from sqlalchemy import text


async def check_web_server():
    """检查Web服务器状态"""
    print("🌐 检查Web服务器...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{settings.HOST}:{settings.PORT}/api/v1/system/health",
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Web服务器正常 - {data.get('status')}")
                return True
            else:
                print(f"❌ Web服务器异常 - HTTP {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Web服务器连接失败: {e}")
        return False


async def check_database():
    """检查数据库连接"""
    print("🗄️ 检查数据库连接...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("✅ 数据库连接正常")
                return True
            else:
                print("❌ 数据库查询异常")
                return False
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


async def check_ros2():
    """检查ROS2状态"""
    print("🤖 检查ROS2状态...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{settings.HOST}:{settings.PORT}/api/v1/ros2/topics",
                timeout=10.0,
                headers={"Authorization": "Bearer dummy"}  # 需要认证，这里用假token测试连接
            )
            # 即使认证失败，如果能连接到服务说明ROS2模块加载正常
            if response.status_code in [200, 401, 403]:
                print("✅ ROS2模块加载正常")
                return True
            else:
                print(f"❌ ROS2模块异常 - HTTP {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ ROS2模块检查失败: {e}")
        return False


async def check_websocket():
    """检查WebSocket状态"""
    print("🔌 检查WebSocket状态...")
    try:
        # 简单的WebSocket连接测试
        import websockets
        uri = f"ws://{settings.HOST}:{settings.PORT}/ws"
        
        async with websockets.connect(uri, timeout=5) as websocket:
            await websocket.send('{"type": "ping"}')
            response = await websocket.recv()
            print("✅ WebSocket连接正常")
            return True
    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")
        return False


async def main():
    """主函数"""
    print("🏥 开始系统健康检查...")
    print(f"📍 目标服务器: {settings.HOST}:{settings.PORT}")
    print("-" * 50)
    
    checks = [
        ("Web服务器", check_web_server()),
        ("数据库", check_database()),
        ("ROS2模块", check_ros2()),
        ("WebSocket", check_websocket()),
    ]
    
    results = []
    for name, check in checks:
        result = await check
        results.append((name, result))
        print()
    
    print("-" * 50)
    print("📊 健康检查汇总:")
    
    all_healthy = True
    for name, result in results:
        status = "✅ 正常" if result else "❌ 异常"
        print(f"   {name}: {status}")
        if not result:
            all_healthy = False
    
    print("-" * 50)
    if all_healthy:
        print("🎉 系统整体状态: 健康")
        sys.exit(0)
    else:
        print("⚠️ 系统整体状态: 存在问题")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
