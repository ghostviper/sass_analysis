"""
从 Docker 中的 PostgreSQL 导出数据

使用 pg_dump 导出数据库到 SQL 文件
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
DOCKER_CONTAINER_NAME = "postgres"  # 你的 PostgreSQL Docker 容器名称
DB_NAME = "sass_analysis"  # 数据库名称
DB_USER = "postgres"  # 数据库用户
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")  # 从环境变量获取密码

# 导出目录
EXPORT_DIR = Path(__file__).parent.parent / "data" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# 生成文件名（带时间戳）
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
EXPORT_FILE = EXPORT_DIR / f"postgres_backup_{timestamp}.sql"
EXPORT_FILE_CUSTOM = EXPORT_DIR / f"postgres_backup_{timestamp}.dump"


def check_docker_container():
    """检查 Docker 容器是否运行"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={DOCKER_CONTAINER_NAME}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        containers = result.stdout.strip().split('\n')
        if DOCKER_CONTAINER_NAME in containers:
            print(f"✓ Docker 容器 '{DOCKER_CONTAINER_NAME}' 正在运行")
            return True
        else:
            print(f"✗ Docker 容器 '{DOCKER_CONTAINER_NAME}' 未运行")
            print("\n可用的容器:")
            subprocess.run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"])
            return False
    except subprocess.CalledProcessError as e:
        print(f"✗ 检查 Docker 容器失败: {e}")
        return False
    except FileNotFoundError:
        print("✗ Docker 未安装或不在 PATH 中")
        return False


def export_sql_format():
    """导出为 SQL 格式（纯文本，易读）"""
    print(f"\n正在导出数据库到 SQL 格式...")
    print(f"目标文件: {EXPORT_FILE}")
    
    try:
        # 使用 docker exec 运行 pg_dump
        cmd = [
            "docker", "exec", "-i", DOCKER_CONTAINER_NAME,
            "pg_dump",
            "-U", DB_USER,
            "-d", DB_NAME,
            "--clean",  # 包含 DROP 语句
            "--if-exists",  # 使用 IF EXISTS
            "--no-owner",  # 不导出所有者信息
            "--no-privileges",  # 不导出权限信息
            "--verbose"
        ]
        
        # 设置环境变量
        env = os.environ.copy()
        env["PGPASSWORD"] = DB_PASSWORD
        
        # 执行导出
        with open(EXPORT_FILE, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                check=True
            )
        
        # 检查文件大小
        file_size = EXPORT_FILE.stat().st_size
        print(f"✓ SQL 导出成功")
        print(f"  文件大小: {file_size / 1024 / 1024:.2f} MB")
        print(f"  文件路径: {EXPORT_FILE}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ SQL 导出失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False


def export_custom_format():
    """导出为自定义格式（压缩，适合大数据库）"""
    print(f"\n正在导出数据库到自定义格式（压缩）...")
    print(f"目标文件: {EXPORT_FILE_CUSTOM}")
    
    try:
        # 使用 docker exec 运行 pg_dump
        cmd = [
            "docker", "exec", "-i", DOCKER_CONTAINER_NAME,
            "pg_dump",
            "-U", DB_USER,
            "-d", DB_NAME,
            "-F", "c",  # 自定义格式
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            "--verbose"
        ]
        
        # 设置环境变量
        env = os.environ.copy()
        env["PGPASSWORD"] = DB_PASSWORD
        
        # 执行导出
        with open(EXPORT_FILE_CUSTOM, 'wb') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                env=env,
                check=True
            )
        
        # 检查文件大小
        file_size = EXPORT_FILE_CUSTOM.stat().st_size
        print(f"✓ 自定义格式导出成功")
        print(f"  文件大小: {file_size / 1024 / 1024:.2f} MB")
        print(f"  文件路径: {EXPORT_FILE_CUSTOM}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 自定义格式导出失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False


def export_schema_only():
    """仅导出数据库结构（不含数据）"""
    schema_file = EXPORT_DIR / f"postgres_schema_{timestamp}.sql"
    print(f"\n正在导出数据库结构...")
    print(f"目标文件: {schema_file}")
    
    try:
        cmd = [
            "docker", "exec", "-i", DOCKER_CONTAINER_NAME,
            "pg_dump",
            "-U", DB_USER,
            "-d", DB_NAME,
            "--schema-only",  # 仅结构
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges"
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = DB_PASSWORD
        
        with open(schema_file, 'w', encoding='utf-8') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env, check=True)
        
        file_size = schema_file.stat().st_size
        print(f"✓ 结构导出成功")
        print(f"  文件大小: {file_size / 1024:.2f} KB")
        print(f"  文件路径: {schema_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 结构导出失败: {e}")
        return False


def get_database_info():
    """获取数据库信息"""
    print("\n正在获取数据库信息...")
    
    try:
        # 获取数据库大小
        cmd = [
            "docker", "exec", "-i", DOCKER_CONTAINER_NAME,
            "psql",
            "-U", DB_USER,
            "-d", DB_NAME,
            "-t",  # 仅输出数据
            "-c", f"SELECT pg_size_pretty(pg_database_size('{DB_NAME}'));"
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = DB_PASSWORD
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=True)
        db_size = result.stdout.strip()
        print(f"  数据库大小: {db_size}")
        
        # 获取表数量
        cmd[7] = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=True)
        table_count = result.stdout.strip()
        print(f"  表数量: {table_count}")
        
        # 获取表列表和行数
        cmd[7] = """
        SELECT 
            schemaname || '.' || tablename AS table_name,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
        """
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=True)
        print(f"\n  表信息:")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 获取数据库信息失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("PostgreSQL 数据导出工具")
    print("=" * 60)
    
    # 检查 Docker 容器
    if not check_docker_container():
        print("\n请确保:")
        print("1. Docker 已安装并运行")
        print("2. PostgreSQL 容器正在运行")
        print(f"3. 容器名称为 '{DOCKER_CONTAINER_NAME}'（或修改脚本中的 DOCKER_CONTAINER_NAME）")
        sys.exit(1)
    
    # 获取数据库信息
    get_database_info()
    
    # 导出数据
    print("\n" + "=" * 60)
    print("开始导出数据...")
    print("=" * 60)
    
    success_count = 0
    
    # 1. 导出 SQL 格式（推荐用于恢复到新数据库）
    if export_sql_format():
        success_count += 1
    
    # 2. 导出自定义格式（可选，适合大数据库）
    if export_custom_format():
        success_count += 1
    
    # 3. 导出结构（可选，用于参考）
    if export_schema_only():
        success_count += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("导出完成")
    print("=" * 60)
    print(f"成功导出: {success_count} 个文件")
    print(f"导出目录: {EXPORT_DIR}")
    print("\n推荐使用 SQL 格式文件进行恢复:")
    print(f"  {EXPORT_FILE}")
    print("\n下一步:")
    print("1. 在 Windows 上安装 PostgreSQL")
    print("2. 创建新数据库")
    print("3. 运行 import_postgres_data.py 脚本恢复数据")


if __name__ == "__main__":
    main()
