#!/usr/bin/env python3
"""
日志管理工具
用于清理、统计和管理项目日志文件
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.logging import cleanup_old_logs, get_log_stats


def show_stats():
    """显示日志统计信息"""
    stats = get_log_stats()
    
    print("📊 日志统计信息")
    print("=" * 40)
    print(f"日志目录数量: {stats['total_dirs']}")
    print(f"总占用空间: {stats['total_size_mb']} MB")
    print(f"日志目录列表: {', '.join(stats['log_dirs']) if stats['log_dirs'] else '无'}")
    
    # 显示今日日志目录
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = Path("logs") / today
    if today_dir.exists():
        print(f"\n📁 今日日志目录: logs/{today}/")
        for log_file in today_dir.glob("*.log*"):
            size_mb = log_file.stat().st_size / 1024 / 1024
            print(f"  - {log_file.name}: {size_mb:.2f} MB")


def cleanup_logs(days: int):
    """清理指定天数之前的日志"""
    print(f"🧹 清理 {days} 天前的日志文件...")
    cleanup_old_logs(days)
    print("清理完成！")


def list_logs():
    """列出所有日志文件"""
    base_log_dir = Path("logs")
    if not base_log_dir.exists():
        print("❌ 日志目录不存在")
        return
    
    print("📋 所有日志文件:")
    print("=" * 50)
    
    for date_dir in sorted(base_log_dir.iterdir()):
        if date_dir.is_dir():
            print(f"\n📅 {date_dir.name}/")
            for log_file in sorted(date_dir.glob("*.log*")):
                if log_file.is_file():
                    size_mb = log_file.stat().st_size / 1024 / 1024
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    print(f"  📄 {log_file.name} ({size_mb:.2f} MB, 修改于 {mtime.strftime('%H:%M:%S')})")


def tail_log(log_type: str = "app", lines: int = 50):
    """显示日志文件的最后几行"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_dir = Path("logs") / today
    
    log_files = {
        "app": "app.log",
        "error": "app_error.log", 
        "debug": "app_debug.log"
    }
    
    if log_type not in log_files:
        print(f"❌ 不支持的日志类型: {log_type}")
        print(f"支持的类型: {', '.join(log_files.keys())}")
        return
    
    log_file = log_dir / log_files[log_type]
    if not log_file.exists():
        print(f"❌ 日志文件不存在: {log_file}")
        return
    
    print(f"📖 显示 {log_file} 的最后 {lines} 行:")
    print("=" * 60)
    
    with open(log_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
        tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        for line in tail_lines:
            print(line.rstrip())


def main():
    parser = argparse.ArgumentParser(description="博实智能巡检平台 - 日志管理工具")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 统计命令
    subparsers.add_parser('stats', help='显示日志统计信息')
    
    # 清理命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧日志文件')
    cleanup_parser.add_argument('--days', type=int, default=7, help='保留最近几天的日志 (默认: 7)')
    
    # 列表命令
    subparsers.add_parser('list', help='列出所有日志文件')
    
    # 查看命令
    tail_parser = subparsers.add_parser('tail', help='查看日志文件末尾')
    tail_parser.add_argument('--type', choices=['app', 'error', 'debug'], default='app', help='日志类型 (默认: app)')
    tail_parser.add_argument('--lines', type=int, default=50, help='显示行数 (默认: 50)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'stats':
            show_stats()
        elif args.command == 'cleanup':
            cleanup_logs(args.days)
        elif args.command == 'list':
            list_logs()
        elif args.command == 'tail':
            tail_log(args.type, args.lines)
    except KeyboardInterrupt:
        print("\n\n👋 操作已取消")
    except Exception as e:
        print(f"❌ 执行出错: {e}")


if __name__ == "__main__":
    main()
