#!/usr/bin/env python3
"""
博实智能巡检平台 - 测试运行脚本
"""

import sys
import os
import subprocess
import time

def check_dependencies():
    """检查依赖库"""
    print("🔍 检查依赖库...")
    
    required_packages = ["requests"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n📦 需要安装以下依赖库:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_server():
    """检查服务器是否运行"""
    print("\n🌐 检查服务器状态...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保服务器已启动: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False

def run_simple_test():
    """运行简化测试"""
    print("\n🚀 运行简化测试...")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "tests/simple_test.py"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ 测试完成")
        else:
            print(f"\n❌ 测试失败，退出码: {result.returncode}")
            
    except Exception as e:
        print(f"\n💥 运行测试时出错: {e}")

def run_comprehensive_test():
    """运行全面测试（需要额外依赖）"""
    print("\n🚀 运行全面测试...")
    print("=" * 60)
    
    # 检查额外依赖
    extra_packages = ["aiohttp", "websockets"]
    missing_extra = []
    
    for package in extra_packages:
        try:
            __import__(package)
        except ImportError:
            missing_extra.append(package)
    
    if missing_extra:
        print(f"❌ 缺少额外依赖: {', '.join(missing_extra)}")
        print(f"安装命令: pip install {' '.join(missing_extra)}")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, "tests/comprehensive_test.py"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ 全面测试完成")
        else:
            print(f"\n❌ 全面测试失败，退出码: {result.returncode}")
            
    except Exception as e:
        print(f"\n💥 运行全面测试时出错: {e}")

def main():
    """主函数"""
    print("博实智能巡检平台 - 测试运行器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请先安装所需依赖")
        return
    
    # 检查服务器
    if not check_server():
        print("\n❌ 服务器检查失败，请先启动服务器")
        return
    
    # 选择测试类型
    print("\n📋 选择测试类型:")
    print("1. 简化测试 (仅需要 requests)")
    print("2. 全面测试 (需要 aiohttp, websockets)")
    print("3. 退出")
    
    while True:
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            run_simple_test()
            break
        elif choice == "2":
            run_comprehensive_test()
            break
        elif choice == "3":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请输入 1-3")

if __name__ == "__main__":
    main()
