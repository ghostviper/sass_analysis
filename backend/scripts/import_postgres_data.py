"""
导入数据到本地 PostgreSQL 数据库

从导出的 SQL 文件恢复数据到新安装的 PostgreSQL
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 配置 - 本地 PostgreSQL
LOCAL_DB_HOST = "localhost"
LOCAL_DB_PORT = "5432"
LOCAL_DB_NAME = "sass_analysis"  # 新数据库名称
LOCAL_DB_USER = "postgres"  # PostgreSQL 用户
LOCAL_DB_PASSWORD = os.getenv("LOCAL_DB_PASSWORD", "123456")  # 本地数据库密码

# PostgreSQL 可能的安装路径
POSSIBLE_PSQL_PATHS = [
    r"D:\PostgreSQL\16\bin\psql.exe",  # 你的安装路径
    r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
    r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
    r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
    r"C:\Program Files (x86)\PostgreSQL\16\bin\psql.exe",
    r"C:\Program Files (x86)\PostgreSQL\15\bin\psql.exe",
]

# 导入文件
EXPORT_DIR = Path(__file__).parent.parent / "data" / "exports"

# 全局变量：psql 可执行文件路径
PSQL_PATH = None


def find_psql_executable():
    """查找 psql 可执行文件"""
    global PSQL_PATH
    
    # 1. 先尝试从 PATH 中查找
    try:
        result = subprocess.run(
            ["psql", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        PSQL_PATH = "psql"  # 在 PATH 中
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # 2. 尝试预定义的路径
    for path in POSSIBLE_PSQL_PATHS:
        if Path(path).exists():
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                PSQL_PATH = path
                print(f"✓ 找到 PostgreSQL: {path}")
                return True
            except subprocess.CalledProcessError:
                continue
    
    # 3. 尝试搜索常见目录
    search_dirs = [
        Path(r"C:\Program Files\PostgreSQL"),
        Path(r"C:\Program Files (x86)\PostgreSQL"),
        Path(r"D:\PostgreSQL"),
        Path(r"E:\PostgreSQL"),
    ]
    
    for base_dir in search_dirs:
        if base_dir.exists():
            # 查找所有版本的 bin\psql.exe
            for psql_path in base_dir.rglob("bin/psql.exe"):
                try:
                    result = subprocess.run(
                        [str(psql_path), "--version"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    PSQL_PATH = str(psql_path)
                    print(f"✓ 找到 PostgreSQL: {psql_path}")
                    return True
                except subprocess.CalledProcessError:
                    continue
    
    return False


def check_postgres_installed():
    """检查 PostgreSQL 是否安装"""
    if find_psql_executable():
        try:
            result = subprocess.run(
                [PSQL_PATH, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ PostgreSQL 已安装: {result.stdout.strip()}")
            print(f"  路径: {PSQL_PATH}")
            return True
        except subprocess.CalledProcessError:
            pass
    
    print("✗ PostgreSQL 未找到")
    print("\n请先安装 PostgreSQL:")
    print("1. 下载: https://www.postgresql.org/download/windows/")
    print("2. 安装时记住设置的密码")
    print("\n如果已安装，请手动添加到脚本的 POSSIBLE_PSQL_PATHS 列表:")
    print(f"  编辑: {__file__}")
    print(f"  添加你的 psql.exe 路径")
    return False


def check_postgres_service():
    """检查 PostgreSQL 服务是否运行"""
    try:
        # 尝试连接到 PostgreSQL
        env = os.environ.copy()
        env["PGPASSWORD"] = LOCAL_DB_PASSWORD
        
        result = subprocess.run(
            [
                PSQL_PATH,
                "-h", LOCAL_DB_HOST,
                "-p", LOCAL_DB_PORT,
                "-U", LOCAL_DB_USER,
                "-d", "postgres",  # 连接到默认数据库
                "-c", "SELECT version();"
            ],
            capture_output=True,
            text=True,
            env=env,
            check=True
        )
        print(f"✓ PostgreSQL 服务正在运行")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 无法连接到 PostgreSQL 服务")
        print(f"错误: {e.stderr if e.stderr else str(e)}")
        print("\n请确保:")
        print("1. PostgreSQL 服务已启动")
        print("2. 用户名和密码正确")
        print("3. 端口 5432 未被占用")
        return False


def list_export_files():
    """列出可用的导出文件"""
    if not EXPORT_DIR.exists():
        print(f"✗ 导出目录不存在: {EXPORT_DIR}")
        return []
    
    sql_files = list(EXPORT_DIR.glob("postgres_backup_*.sql"))
    if not sql_files:
        print(f"✗ 未找到导出文件")
        print(f"请先运行 export_postgres_data.py 导出数据")
        return []
    
    # 按修改时间排序
    sql_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"\n找到 {len(sql_files)} 个导出文件:")
    for i, f in enumerate(sql_files, 1):
        size = f.stat().st_size / 1024 / 1024
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        print(f"  {i}. {f.name}")
        print(f"     大小: {size:.2f} MB")
        print(f"     时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return sql_files


def create_database():
    """创建新数据库"""
    print(f"\n正在创建数据库 '{LOCAL_DB_NAME}'...")
    
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = LOCAL_DB_PASSWORD
        
        # 先检查数据库是否存在
        check_cmd = [
            PSQL_PATH,
            "-h", LOCAL_DB_HOST,
            "-p", LOCAL_DB_PORT,
            "-U", LOCAL_DB_USER,
            "-d", "postgres",
            "-t",
            "-c", f"SELECT 1 FROM pg_database WHERE datname = '{LOCAL_DB_NAME}';"
        ]
        
        result = subprocess.run(check_cmd, capture_output=True, text=True, env=env, check=True)
        
        if result.stdout.strip():
            print(f"⚠ 数据库 '{LOCAL_DB_NAME}' 已存在")
            response = input("是否删除并重新创建? (y/N): ").strip().lower()
            if response == 'y':
                # 删除数据库
                drop_cmd = [
                    PSQL_PATH,
                    "-h", LOCAL_DB_HOST,
                    "-p", LOCAL_DB_PORT,
                    "-U", LOCAL_DB_USER,
                    "-d", "postgres",
                    "-c", f"DROP DATABASE IF EXISTS {LOCAL_DB_NAME};"
                ]
                subprocess.run(drop_cmd, env=env, check=True)
                print(f"✓ 已删除旧数据库")
            else:
                print("取消操作")
                return False
        
        # 创建数据库
        create_cmd = [
            PSQL_PATH,
            "-h", LOCAL_DB_HOST,
            "-p", LOCAL_DB_PORT,
            "-U", LOCAL_DB_USER,
            "-d", "postgres",
            "-c", f"CREATE DATABASE {LOCAL_DB_NAME} ENCODING 'UTF8';"
        ]
        
        subprocess.run(create_cmd, env=env, check=True)
        print(f"✓ 数据库 '{LOCAL_DB_NAME}' 创建成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 创建数据库失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False


def import_sql_file(sql_file: Path):
    """导入 SQL 文件"""
    print(f"\n正在导入数据...")
    print(f"源文件: {sql_file}")
    print(f"目标数据库: {LOCAL_DB_NAME}")
    print("这可能需要几分钟，请耐心等待...")
    
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = LOCAL_DB_PASSWORD
        
        # 使用 psql 导入
        cmd = [
            PSQL_PATH,
            "-h", LOCAL_DB_HOST,
            "-p", LOCAL_DB_PORT,
            "-U", LOCAL_DB_USER,
            "-d", LOCAL_DB_NAME,
            "-f", str(sql_file),
            "-v", "ON_ERROR_STOP=1"  # 遇到错误停止
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ 数据导入成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 数据导入失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False


def verify_import():
    """验证导入结果"""
    print(f"\n正在验证导入结果...")
    
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = LOCAL_DB_PASSWORD
        
        # 获取表数量
        cmd = [
            PSQL_PATH,
            "-h", LOCAL_DB_HOST,
            "-p", LOCAL_DB_PORT,
            "-U", LOCAL_DB_USER,
            "-d", LOCAL_DB_NAME,
            "-t",
            "-c", "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=True)
        table_count = result.stdout.strip()
        print(f"  表数量: {table_count}")
        
        # 获取数据库大小
        cmd[-1] = f"SELECT pg_size_pretty(pg_database_size('{LOCAL_DB_NAME}'));"
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=True)
        db_size = result.stdout.strip()
        print(f"  数据库大小: {db_size}")
        
        # 列出所有表
        cmd[-1] = """
        SELECT 
            tablename,
            pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size('public.'||tablename) DESC;
        """
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=True)
        print(f"\n  表信息:")
        print(result.stdout)
        
        print(f"✓ 验证完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 验证失败: {e}")
        return False


def update_env_file():
    """更新 .env 文件中的数据库连接"""
    env_file = Path(__file__).parent.parent / ".env"
    
    if not env_file.exists():
        print(f"\n⚠ .env 文件不存在: {env_file}")
        return
    
    print(f"\n是否更新 .env 文件中的数据库连接? (y/N): ", end="")
    response = input().strip().lower()
    
    if response != 'y':
        print("跳过更新 .env 文件")
        return
    
    try:
        # 读取现有内容
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新数据库连接
        new_lines = []
        updated = False
        
        for line in lines:
            if line.startswith('DATABASE_URL='):
                new_url = f"DATABASE_URL=postgresql://{LOCAL_DB_USER}:{LOCAL_DB_PASSWORD}@{LOCAL_DB_HOST}:{LOCAL_DB_PORT}/{LOCAL_DB_NAME}\n"
                new_lines.append(new_url)
                updated = True
            else:
                new_lines.append(line)
        
        # 如果没有找到 DATABASE_URL，添加它
        if not updated:
            new_lines.append(f"\n# PostgreSQL 连接\n")
            new_lines.append(f"DATABASE_URL=postgresql://{LOCAL_DB_USER}:{LOCAL_DB_PASSWORD}@{LOCAL_DB_HOST}:{LOCAL_DB_PORT}/{LOCAL_DB_NAME}\n")
        
        # 写回文件
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✓ .env 文件已更新")
        print(f"  DATABASE_URL=postgresql://{LOCAL_DB_USER}:***@{LOCAL_DB_HOST}:{LOCAL_DB_PORT}/{LOCAL_DB_NAME}")
        
    except Exception as e:
        print(f"✗ 更新 .env 文件失败: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("PostgreSQL 数据导入工具")
    print("=" * 60)
    
    # 检查 PostgreSQL 安装
    if not check_postgres_installed():
        sys.exit(1)
    
    # 检查 PostgreSQL 服务
    if not check_postgres_service():
        sys.exit(1)
    
    # 列出导出文件
    sql_files = list_export_files()
    if not sql_files:
        sys.exit(1)
    
    # 选择文件
    print(f"\n请选择要导入的文件 (1-{len(sql_files)}): ", end="")
    try:
        choice = int(input().strip())
        if choice < 1 or choice > len(sql_files):
            print("无效的选择")
            sys.exit(1)
        selected_file = sql_files[choice - 1]
    except ValueError:
        print("无效的输入")
        sys.exit(1)
    
    # 确认
    print(f"\n将导入文件: {selected_file.name}")
    print(f"到数据库: {LOCAL_DB_NAME}")
    print(f"确认继续? (y/N): ", end="")
    if input().strip().lower() != 'y':
        print("取消操作")
        sys.exit(0)
    
    # 创建数据库
    if not create_database():
        sys.exit(1)
    
    # 导入数据
    if not import_sql_file(selected_file):
        sys.exit(1)
    
    # 验证导入
    verify_import()
    
    # 更新 .env 文件
    update_env_file()
    
    # 总结
    print("\n" + "=" * 60)
    print("导入完成")
    print("=" * 60)
    print(f"✓ 数据已成功导入到本地 PostgreSQL")
    print(f"✓ 数据库名称: {LOCAL_DB_NAME}")
    print(f"✓ 连接地址: {LOCAL_DB_HOST}:{LOCAL_DB_PORT}")
    print("\n下一步:")
    print("1. 测试数据库连接")
    print("2. 启动应用: python run_server.py")
    print("3. 如果需要，运行迁移: python migrations/add_checkpoint_id.py")


if __name__ == "__main__":
    main()
