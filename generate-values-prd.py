#!/usr/bin/env python3
"""
Dify Helm Chart Values Generator
交互式生成 values-prd.yaml 配置文件

模块划分和联动关系：
1. 全局配置模块 (global) - 影响所有服务
2. 基础设施模块 - 数据库、存储、缓存（互斥选择）
3. 服务模块 - 应用服务配置
4. 网络模块 - Ingress配置
5. 邮件模块 - 邮件服务配置
"""

import yaml
import os
import subprocess
import sys
import re
import shutil
from typing import Dict, Any, Optional
from copy import deepcopy


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_section(text: str):
    """打印章节"""
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}>>> {text}{Colors.ENDC}")


def print_info(text: str):
    """打印信息"""
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")


def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_warning(text: str):
    """打印警告"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text: str):
    """打印错误"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def prompt(prompt_text: str, default: Optional[str] = None, required: bool = True) -> str:
    """提示用户输入"""
    if default:
        prompt_str = f"{Colors.BOLD}{prompt_text}{Colors.ENDC} [{default}]: "
    else:
        prompt_str = f"{Colors.BOLD}{prompt_text}{Colors.ENDC}: "
    
    while True:
        value = input(prompt_str).strip()
        if value:
            return value
        elif default:
            return default
        elif not required:
            return ""
        else:
            print_error("此字段为必填项，请重新输入")


def prompt_yes_no(prompt_text: str, default: bool = True) -> bool:
    """提示是/否选择"""
    default_str = "Y/n" if default else "y/N"
    prompt_str = f"{Colors.BOLD}{prompt_text}{Colors.ENDC} [{default_str}]: "
    
    while True:
        value = input(prompt_str).strip().lower()
        if not value:
            return default
        if value in ['y', 'yes']:
            return True
        elif value in ['n', 'no']:
            return False
        else:
            print_error("请输入 y 或 n")


def prompt_choice(prompt_text: str, choices: list, default: Optional[str] = None) -> str:
    """提示选择"""
    print(f"\n{Colors.BOLD}{prompt_text}{Colors.ENDC}")
    for i, choice in enumerate(choices, 1):
        marker = " [默认]" if choice == default else ""
        print(f"  {i}. {choice}{marker}")
    
    while True:
        if default:
            prompt_str = f"请选择 [1-{len(choices)}] (默认: {default}): "
        else:
            prompt_str = f"请选择 [1-{len(choices)}]: "
        
        value = input(prompt_str).strip()
        if not value and default:
            return default
        
        try:
            idx = int(value) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        
        print_error(f"请输入 1-{len(choices)} 之间的数字")


def generate_secret(length: int = 42) -> str:
    """生成密钥"""
    try:
        result = subprocess.run(
            ['openssl', 'rand', '-base64', str(length)],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("无法使用 openssl 生成密钥，将使用随机字符串")
        import secrets
        return secrets.token_urlsafe(length)


class ValuesGenerator:
    """Values 生成器"""
    
    def __init__(self, source_file: str):
        """初始化"""
        self.source_file = source_file
        self.values = {}
        self.yaml_data = None  # ruamel.yaml 的数据对象（保留注释和格式）
        self.yaml_loader = None  # ruamel.yaml 加载器实例
        self.load_template()
    
    def load_template(self):
        """加载模板文件"""
        try:
            # 必须使用 ruamel.yaml
            from ruamel.yaml import YAML
            
            self.yaml_loader = YAML()
            self.yaml_loader.preserve_quotes = True
            self.yaml_loader.width = 120
            self.yaml_loader.indent(mapping=2, sequence=4)
            self.yaml_loader.default_flow_style = False
            self.yaml_loader.default_style = None  # 保持原始样式
            
            # 读取原始文件（保留注释和格式）
            with open(self.source_file, 'r', encoding='utf-8') as f:
                self.yaml_data = self.yaml_loader.load(f)
            
            # 同时加载为标准字典用于配置逻辑
            with open(self.source_file, 'r', encoding='utf-8') as f:
                self.values = yaml.safe_load(f)
            
            print_success(f"已加载模板文件: {self.source_file} (使用 ruamel.yaml，保留注释和格式)")
                
        except ImportError:
            print_error("ruamel.yaml 未安装！")
            print_error("请安装: pip install ruamel.yaml")
            sys.exit(1)
        except Exception as e:
            print_error(f"加载模板文件失败: {e}")
            sys.exit(1)
    
    def set_value(self, key_path: str, value: Any):
        """
        设置值（同时更新 yaml_data 和 values）
        
        Args:
            key_path: 键路径，如 'global.appSecretKey'
            value: 新值
        """
        keys = key_path.split('.')
        
        # 更新标准字典
        current = self.values
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        
        # 更新 ruamel.yaml 数据对象
        if self.yaml_data is not None:
            try:
                from ruamel.yaml.comments import CommentedMap
                current = self.yaml_data
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = CommentedMap()
                    current = current[key]
                current[keys[-1]] = value
            except Exception:
                # 如果更新失败，至少标准字典已更新
                pass
    
    def save(self, output_file: str):
        """
        保存到文件 - 使用 ruamel.yaml 保留注释和格式
        """
        try:
            # 必须使用 ruamel.yaml
            from ruamel.yaml import YAML
            
            # 如果已有 yaml_loader，使用它；否则创建新的
            if self.yaml_loader is None:
                yaml_loader = YAML()
                yaml_loader.preserve_quotes = True
                yaml_loader.width = 120
                yaml_loader.indent(mapping=2, sequence=4)
                yaml_loader.default_flow_style = False
                yaml_loader.default_style = None  # 保持原始样式
                
                # 重新加载原始文件（保留注释和格式）
                with open(self.source_file, 'r', encoding='utf-8') as f:
                    data = yaml_loader.load(f)
            else:
                # 使用已加载的数据，或重新加载以确保最新
                if self.yaml_data is not None:
                    data = self.yaml_data
                else:
                    with open(self.source_file, 'r', encoding='utf-8') as f:
                        data = self.yaml_loader.load(f)
                yaml_loader = self.yaml_loader
            
            # 递归更新值（将 self.values 的更改应用到 data）
            self._update_dict_recursive(data, self.values)
            
            # 保存
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml_loader.dump(data, f)
            
            print_success(f"配置已保存到: {output_file}")
            print_info("✓ 已保留原始格式、注释和引号（使用 ruamel.yaml）")
                
        except ImportError:
            print_error("ruamel.yaml 未安装！")
            print_error("请安装: pip install ruamel.yaml")
            sys.exit(1)
        except Exception as e:
            print_error(f"保存文件失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def _update_dict_recursive(self, target: dict, source: dict):
        """递归更新字典，保留 ruamel.yaml 的格式和注释"""
        # 必须使用 ruamel.yaml
        from ruamel.yaml.scalarstring import ScalarString, DoubleQuotedScalarString, SingleQuotedScalarString
        from ruamel.yaml.comments import CommentedMap, CommentedSeq
        
        for key, value in source.items():
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], dict):
                    self._update_dict_recursive(target[key], value)
                elif isinstance(value, list) and isinstance(target[key], list):
                    # 处理列表 - 只在值真正改变时更新
                    if value != target[key]:
                        target[key] = value
                else:
                    # 获取原始值的实际值（去除 ScalarString 包装）
                    original_actual_value = target[key]
                    if isinstance(original_actual_value, ScalarString):
                        original_actual_value = str(original_actual_value)
                    
                    # 只在值真正改变时更新，保留原始格式和注释
                    if str(value) != str(original_actual_value):
                        # 更新标量值，保留原始引号格式
                        original_value = target[key]
                        new_value = value
                        
                        # 检查原始值是否有引号格式
                        if isinstance(original_value, DoubleQuotedScalarString):
                            # 原始值有双引号，新值也应该有双引号
                            new_value = DoubleQuotedScalarString(str(value))
                        elif isinstance(original_value, SingleQuotedScalarString):
                            # 原始值有单引号，新值也应该有单引号
                            new_value = SingleQuotedScalarString(str(value))
                        elif isinstance(original_value, ScalarString):
                            # 原始值是其他类型的 ScalarString，保持格式
                            new_value = type(original_value)(str(value))
                        elif isinstance(value, str) and isinstance(original_value, str):
                            # 原始值是普通字符串，新值也是字符串
                            # 如果新值包含特殊字符，使用双引号以保持格式一致性
                            needs_quotes = (
                                ':' in value or 
                                '/' in value or 
                                ' ' in value or
                                value.startswith('*') or
                                value.startswith('#') or
                                value == '' or
                                value.startswith('http://') or
                                value.startswith('https://') or
                                value.endswith('.local') or
                                value.endswith('.ai') or
                                value.endswith('.com') or
                                value.endswith('.tech') or
                                '+' in value or  # base64 字符串通常包含 +
                                '=' in value     # base64 字符串通常包含 =
                            )
                            
                            if needs_quotes:
                                new_value = DoubleQuotedScalarString(value)
                            # 否则保持普通字符串格式（直接赋值，ruamel.yaml 会自动处理）
                        
                        target[key] = new_value
                    # 如果值没有改变，不更新，保留原始的格式、注释和引号
    
    def _save_with_text_replacement(self, output_file: str):
        """使用文本替换方式保存，保留注释和格式"""
        # 先复制模板文件
        content = self.template_content
        
        # 获取原始值用于比较
        with open(self.source_file, 'r', encoding='utf-8') as f:
            original_data = yaml.safe_load(f)
        
        # 找出所有需要更新的值
        def find_changes(new_dict: dict, old_dict: dict, path: str = ""):
            changes = []
            for k, v in new_dict.items():
                current_path = f"{path}.{k}" if path else k
                if k not in old_dict:
                    changes.append((current_path, v))
                elif isinstance(v, dict) and isinstance(old_dict[k], dict):
                    changes.extend(find_changes(v, old_dict[k], current_path))
                elif v != old_dict[k]:
                    changes.append((current_path, v))
            return changes
        
        changes = find_changes(self.values, original_data)
        
        # 对每个变更进行文本替换
        for path, new_value in changes:
            keys = path.split('.')
            
            # 构建正则表达式匹配模式
            if len(keys) == 1:
                # 简单键：匹配 "key: value" 格式
                # 需要处理多行值（如注释、多行字符串）
                pattern = rf'^(\s*){re.escape(keys[0])}\s*:(.*?)(?=\n\s*\w+\s*:|\n\s*$|\Z)'
                
                def replace_func(match):
                    indent = match.group(1)
                    old_value_part = match.group(2)
                    
                    # 生成新值
                    if new_value is None:
                        return f"{indent}{keys[0]}:"
                    elif isinstance(new_value, str):
                        # 检查原值是否有引号
                        old_stripped = old_value_part.strip()
                        has_quotes = old_stripped.startswith('"') or old_stripped.startswith("'")
                        # 检查是否需要引号
                        needs_quotes = (has_quotes or new_value == '' or 
                                       ':' in new_value or new_value.startswith('*') or
                                       new_value.startswith('#') or ' ' in new_value)
                        if needs_quotes:
                            return f"{indent}{keys[0]}: \"{new_value}\""
                        else:
                            return f"{indent}{keys[0]}: {new_value}"
                    elif isinstance(new_value, bool):
                        return f"{indent}{keys[0]}: {str(new_value).lower()}"
                    elif isinstance(new_value, (int, float)):
                        return f"{indent}{keys[0]}: {new_value}"
                    elif isinstance(new_value, list):
                        if len(new_value) == 0:
                            return f"{indent}{keys[0]}: []"
                        else:
                            result = f"{indent}{keys[0]}:\n"
                            for item in new_value:
                                if isinstance(item, dict):
                                    for k, v in item.items():
                                        result += f"{indent}  {k}: {v}\n"
                                else:
                                    result += f"{indent}  - {item}\n"
                            return result.rstrip()
                    else:
                        return f"{indent}{keys[0]}: {new_value}"
                
                # 使用多行模式匹配
                content = re.sub(pattern, replace_func, content, flags=re.MULTILINE | re.DOTALL)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success(f"配置已保存到: {output_file}")
        print_warning("⚠ 文本替换方式可能无法完美保留所有格式，建议安装 ruamel.yaml")
    
    # ==================== 模块 1: 全局配置 ====================
    def configure_global(self):
        """配置全局设置"""
        print_header("模块 1: 全局配置 (Global Configuration)")
        
        print_info("全局配置影响所有服务的运行")
        
        # Secret Keys - 所有密钥都按注释自动生成
        print_section("密钥配置")
        print_info("appSecretKey 用于安全签名会话cookie和加密数据库敏感信息")
        print_info("将使用 openssl rand -base64 42 自动生成")
        self.values['global']['appSecretKey'] = generate_secret(42)
        print_success(f"已生成 appSecretKey: {self.values['global']['appSecretKey'][:20]}...")
        
        print_info("innerApiKey 用于内部API调用的密钥")
        print_info("将使用 openssl rand -base64 42 自动生成")
        self.values['global']['innerApiKey'] = generate_secret(42)
        print_success(f"已生成 innerApiKey: {self.values['global']['innerApiKey'][:20]}...")
        
        # 域名配置
        print_section("域名配置")
        print_info("如果为空，将使用相同域名")
        
        self.values['global']['consoleApiDomain'] = prompt(
            "Console API 域名", 
            default="console.dify.local", 
            required=False
        )
        
        self.values['global']['consoleWebDomain'] = prompt(
            "Console Web 域名", 
            default="console.dify.local", 
            required=False
        )
        
        self.values['global']['serviceApiDomain'] = prompt(
            "Service API 域名", 
            default="api.dify.local", 
            required=False
        )
        
        self.values['global']['appApiDomain'] = prompt(
            "WebApp API 后端域名", 
            default="app.dify.local", 
            required=False
        )
        
        self.values['global']['appWebDomain'] = prompt(
            "WebApp 域名", 
            default="app.dify.local", 
            required=False
        )
        
        self.values['global']['filesDomain'] = prompt(
            "文件预览/下载域名", 
            default="files.dify.local", 
            required=False
        )
        
        self.values['global']['enterpriseDomain'] = prompt(
            "Enterprise 服务域名", 
            default="enterprise.dify.local", 
            required=False
        )
        
        # 数据库迁移
        self.values['global']['dbMigrationEnabled'] = prompt_yes_no(
            "是否启用数据库迁移?", 
            default=True
        )
        
        # RAG配置
        print_section("RAG 配置")
        rag_etl_type = prompt_choice(
            "RAG ETL 类型",
            ["dify", "Unstructured"],
            default="dify"
        )
        self.values['global']['rag']['etlType'] = rag_etl_type
        
        # 联动关系: 如果选择 dify，则关闭 unstructured 模块
        if rag_etl_type == "dify":
            self.values['unstructured']['enabled'] = False
            print_info("已自动关闭 unstructured 模块（RAG ETL 类型为 dify）")
        else:
            self.values['unstructured']['enabled'] = True
            print_info("已自动启用 unstructured 模块（RAG ETL 类型为 Unstructured）")
        
        # 关键词数据源类型配置 - 添加详细说明
        print_section("关键词数据源类型配置")
        print_info("=" * 60)
        print_info("重要说明：关键词数据源类型")
        print_info("=" * 60)
        print_info("此配置决定 RAG 关键词检索（Keyword Search）时的关键词存储位置。")
        print_info("")
        print_info("选项说明：")
        print_info("  • object_storage: 将关键词存储在对象存储中（如 MinIO、S3）")
        print_info("    - 适合大规模关键词存储")
        print_info("    - 需要配置对象存储服务")
        print_info("")
        print_info("  • database: 将关键词存储在数据库中")
        print_info("    - 适合中小规模关键词存储")
        print_info("    - 使用已配置的 PostgreSQL 数据库")
        print_info("=" * 60)
        print_info("")
        self.values['global']['rag']['keywordDataSourceType'] = prompt_choice(
            "请选择关键词数据源类型",
            ["object_storage", "database"],
            default="object_storage"
        )
        
        top_k = prompt("RAG Top-K 最大值", default="10", required=False)
        try:
            self.values['global']['rag']['topKMaxValue'] = int(top_k)
        except ValueError:
            print_warning("无效的数字，使用默认值 10")
        
        seg_tokens = prompt("文档分块最大token长度", default="4000", required=False)
        try:
            self.values['global']['rag']['indexingMaxSegmentationTokensLength'] = int(seg_tokens)
        except ValueError:
            print_warning("无效的数字，使用默认值 4000")
    
    # ==================== 模块 2: 基础设施配置 ====================
    def configure_infrastructure(self):
        """配置基础设施"""
        print_header("模块 2: 基础设施配置 (Infrastructure)")
        
        # PostgreSQL
        print_section("PostgreSQL 数据库配置")
        print_info("=" * 60)
        print_info("网络地址说明（重要）")
        print_info("=" * 60)
        print_info("如果在 kind 集群中运行，访问集群外（同一主机）的服务：")
        print_info("  • 使用 'host.docker.internal' 访问宿主机服务")
        print_info("  • 或使用宿主机 IP 地址")
        print_info("  • 或使用 'localhost'（如果配置了端口映射）")
        print_info("")
        print_info("如果服务在集群内：")
        print_info("  • 使用服务名，例如: postgresql.default.svc.cluster.local")
        print_info("  • 或使用短服务名，例如: postgresql")
        print_info("=" * 60)
        print_info("")
        # 默认使用外部 PostgreSQL（企业版推荐）
        use_external_postgres = True
        print_info("默认使用外部 PostgreSQL（企业版推荐配置）")
        
        if use_external_postgres:
            self.values['externalPostgres']['enabled'] = True
            self.values['postgresql']['enabled'] = False
            
            print_info("配置外部 PostgreSQL 连接信息")
            print_warning("提示: 如果在 kind 集群中访问宿主机服务，使用 'host.docker.internal'")
            self.values['externalPostgres']['address'] = prompt(
                "PostgreSQL 地址 (kind集群外使用 host.docker.internal 或宿主机IP)", 
                default="host.docker.internal", 
                required=True
            )
            
            port = prompt("PostgreSQL 端口", default="5432", required=False)
            try:
                self.values['externalPostgres']['port'] = int(port)
            except ValueError:
                self.values['externalPostgres']['port'] = 5432
            
            # 配置各个数据库的凭证 - 交互式获取每个数据库的配置信息
            databases_config = [
                {'key': 'dify', 'name': 'dify', 'desc': '主数据库'},
                {'key': 'plugin_daemon', 'name': 'plugin_daemon', 'desc': '插件守护进程数据库'},
                {'key': 'enterprise', 'name': 'enterprise', 'desc': '企业版数据库'},
                {'key': 'audit', 'name': 'audit', 'desc': '审计数据库'}
            ]
            
            for db_config in databases_config:
                print(f"\n{'='*60}")
                print(f"配置数据库: {db_config['name']} ({db_config['desc']})")
                print(f"{'='*60}")
                
                db_key = db_config['key']
                
                self.values['externalPostgres']['credentials'][db_key]['database'] = prompt(
                    f"{db_config['name']} 数据库名", 
                    default=db_config['name'], 
                    required=False
                )
                
                self.values['externalPostgres']['credentials'][db_key]['username'] = prompt(
                    f"{db_config['name']} 用户名", 
                    default="postgres", 
                    required=False
                )
                
                self.values['externalPostgres']['credentials'][db_key]['password'] = prompt(
                    f"{db_config['name']} 密码", 
                    required=True
                )
                
                self.values['externalPostgres']['credentials'][db_key]['sslmode'] = prompt_choice(
                    f"{db_config['name']} SSL 模式",
                    ["disable", "require", "verify-ca", "verify-full"],
                    default="require"
                )
                
                # 设置默认值（不再询问）
                self.values['externalPostgres']['credentials'][db_key]['extras'] = ''
                self.values['externalPostgres']['credentials'][db_key]['charset'] = ''
                self.values['externalPostgres']['credentials'][db_key]['uriScheme'] = 'postgresql'
        else:
            self.values['externalPostgres']['enabled'] = False
            self.values['postgresql']['enabled'] = True
            
            print_info("将使用 Helm Chart 内置的 PostgreSQL")
            if prompt_yes_no("是否配置 PostgreSQL 密码?", default=True):
                if prompt_yes_no("是否自动生成密码?", default=True):
                    self.values['postgresql']['global']['postgresql']['auth']['postgresPassword'] = generate_secret(32)
                    print_success("已生成 PostgreSQL 密码")
                else:
                    self.values['postgresql']['global']['postgresql']['auth']['postgresPassword'] = prompt(
                        "PostgreSQL root 密码", 
                        required=True
                    )
        
        # Redis
        print_section("Redis 缓存配置")
        use_external_redis = prompt_yes_no("是否使用外部 Redis?", default=True)
        
        if use_external_redis:
            self.values['externalRedis']['enabled'] = True
            self.values['redis']['enabled'] = False
            
            print_info("配置外部 Redis 连接信息")
            print_warning("提示: 如果在 kind 集群中访问宿主机服务，使用 'host.docker.internal'")
            self.values['externalRedis']['host'] = prompt(
                "Redis 主机地址 (kind集群外使用 host.docker.internal 或宿主机IP)", 
                default="host.docker.internal", 
                required=True
            )
            
            port = prompt("Redis 端口", default="6379", required=False)
            try:
                self.values['externalRedis']['port'] = int(port)
            except ValueError:
                self.values['externalRedis']['port'] = 6379
            
            self.values['externalRedis']['useSSL'] = prompt_yes_no("是否使用 SSL?", default=False)
            
            self.values['externalRedis']['username'] = prompt(
                "Redis 用户名 (可选)", 
                default="", 
                required=False
            )
            
            self.values['externalRedis']['password'] = prompt(
                "Redis 密码", 
                required=True
            )
            
            db_num = prompt("Redis 数据库编号", default="0", required=False)
            try:
                self.values['externalRedis']['db'] = int(db_num)
            except ValueError:
                self.values['externalRedis']['db'] = 0
            
            # Sentinel/Cluster 配置 - 互斥选择
            use_sentinel = prompt_yes_no("是否使用 Redis Sentinel?", default=False)
            use_cluster = False
            
            if use_sentinel:
                self.values['externalRedis']['sentinel']['enabled'] = True
                self.values['externalRedis']['cluster']['enabled'] = False
                
                self.values['externalRedis']['sentinel']['nodes'] = prompt(
                    "Sentinel 节点列表 (host:port,host:port)", 
                    required=True
                )
                self.values['externalRedis']['sentinel']['serviceName'] = prompt(
                    "Sentinel 服务名", 
                    required=True
                )
                self.values['externalRedis']['sentinel']['username'] = prompt(
                    "Sentinel 用户名 (可选)", 
                    default="", 
                    required=False
                )
                self.values['externalRedis']['sentinel']['password'] = prompt(
                    "Sentinel 密码", 
                    required=True
                )
                socket_timeout = prompt(
                    "Socket 超时时间(秒)", 
                    default="0.1", 
                    required=False
                )
                try:
                    self.values['externalRedis']['sentinel']['socketTimeout'] = float(socket_timeout)
                except ValueError:
                    self.values['externalRedis']['sentinel']['socketTimeout'] = 0.1
            else:
                self.values['externalRedis']['sentinel']['enabled'] = False
                use_cluster = prompt_yes_no("是否使用 Redis Cluster?", default=False)
            
            if use_cluster:
                self.values['externalRedis']['cluster']['enabled'] = True
                self.values['externalRedis']['cluster']['nodes'] = prompt(
                    "Cluster 节点列表 (host:port,host:port)", 
                    required=True
                )
                self.values['externalRedis']['cluster']['password'] = prompt(
                    "Cluster 密码", 
                    required=True
                )
            else:
                self.values['externalRedis']['cluster']['enabled'] = False
        else:
            self.values['externalRedis']['enabled'] = False
            self.values['redis']['enabled'] = True
            
            print_info("将使用 Helm Chart 内置的 Redis")
            if prompt_yes_no("是否配置 Redis 密码?", default=True):
                if prompt_yes_no("是否自动生成密码?", default=True):
                    self.values['redis']['global']['redis']['password'] = generate_secret(32)
                    print_success("已生成 Redis 密码")
                else:
                    self.values['redis']['global']['redis']['password'] = prompt(
                        "Redis 密码", 
                        required=True
                    )
        
        # VectorDB
        print_section("向量数据库配置")
        use_external_vectordb = prompt_yes_no("是否使用外部向量数据库?", default=True)
        
        self.values['vectorDB']['useExternal'] = use_external_vectordb
        
        if use_external_vectordb:
            vectordb_type = prompt_choice(
                "选择向量数据库类型",
                ["qdrant", "weaviate", "milvus", "relyt", "pgvecto-rs", 
                 "tencent", "opensearch", "elasticsearch", "analyticdb", "lindorm"],
                default="qdrant"
            )
            self.values['vectorDB']['externalType'] = vectordb_type
            
            print_info(f"配置外部 {vectordb_type} 连接信息")
            print_warning("提示: 如果在 kind 集群中访问宿主机服务，使用 'host.docker.internal'")
            
            if vectordb_type == "qdrant":
                self.values['vectorDB']['externalQdrant']['endpoint'] = prompt(
                    "Qdrant 端点 URL (kind集群外使用 http://host.docker.internal:6333)", 
                    default="http://host.docker.internal:6333", 
                    required=True
                )
                self.values['vectorDB']['externalQdrant']['apiKey'] = prompt(
                    "Qdrant API Key", 
                    required=False
                )
            elif vectordb_type == "weaviate":
                self.values['vectorDB']['externalWeaviate']['endpoint'] = prompt(
                    "Weaviate 端点 URL", 
                    default="http://weaviate:8080", 
                    required=True
                )
                self.values['vectorDB']['externalWeaviate']['apiKey'] = prompt(
                    "Weaviate API Key", 
                    required=False
                )
            # 其他类型可以类似扩展
        else:
            # 使用内置向量数据库
            vectordb_choice = prompt_choice(
                "选择内置向量数据库",
                ["qdrant", "weaviate"],
                default="qdrant"
            )
            
            if vectordb_choice == "qdrant":
                self.values['qdrant']['enabled'] = True
                self.values['weaviate']['enabled'] = False
                
                api_key = prompt("Qdrant API Key", default="dify123456", required=False)
                self.values['qdrant']['apiKey'] = api_key
                
                replica_count = prompt("Qdrant 副本数", default="3", required=False)
                try:
                    self.values['qdrant']['replicaCount'] = int(replica_count)
                except ValueError:
                    self.values['qdrant']['replicaCount'] = 3
            else:
                self.values['qdrant']['enabled'] = False
                self.values['weaviate']['enabled'] = True
        
        # 存储配置
        print_section("存储配置 (Persistence)")
        storage_type = prompt_choice(
            "选择存储类型",
            ["local", "s3 (AWS S3 和 S3 兼容协议)", "azure-blob", "aliyun-oss", "google-storage", 
             "tencent-cos", "volcengine-tos", "huawei-obs"],
            default="local"
        )
        
        # 处理存储类型选择，将显示名称转换为实际值
        if storage_type == "s3 (AWS S3 和 S3 兼容协议)":
            storage_type = "s3"
        self.values['persistence']['type'] = storage_type
        
        if storage_type == "local":
            print_info("配置本地存储")
            self.values['persistence']['local']['mountPath'] = prompt(
                "挂载路径", 
                default="/app/api/storage", 
                required=False
            )
            
            storage_class = prompt(
                "StorageClass 名称 (留空使用默认)", 
                default="", 
                required=False
            )
            if storage_class:
                self.values['persistence']['local']['persistentVolumeClaim']['storageClass'] = storage_class
            
            size = prompt("存储大小", default="5Gi", required=False)
            self.values['persistence']['local']['persistentVolumeClaim']['size'] = size
            
        elif storage_type == "s3":
            print_info("配置 S3 兼容存储（AWS S3 和 S3 兼容协议）")
            
            # 判断是 AWS S3 还是其他兼容 S3 的服务（如 MinIO）
            s3_provider = prompt_choice(
                "S3 服务提供商",
                ["AWS S3", "MinIO", "Cloudflare R2", "其他兼容S3服务"],
                default="AWS S3"
            )
            
            if s3_provider == "AWS S3":
                self.values['persistence']['s3']['useAwsS3'] = True
                print_info("配置 AWS S3")
                # AWS S3 不需要内置 MinIO
                self.values['minio']['enabled'] = False
                print_info("已自动关闭内置 MinIO（使用 AWS S3）")
            else:
                self.values['persistence']['s3']['useAwsS3'] = False
                print_info(f"配置 {s3_provider} (S3兼容)")
                # 非 AWS S3 需要内置 MinIO
                self.values['minio']['enabled'] = True
                print_info("已自动启用内置 MinIO（useAwsS3=false）")
            
            # MinIO 特殊配置说明
            if s3_provider == "MinIO":
                print_info("")
                print_info("=" * 60)
                print_info("外部 MinIO 配置说明（对象存储）")
                print_info("=" * 60)
                print_info("配置您自建的外部 MinIO 服务作为对象存储：")
                print_info("  • Access Key = MINIO_ROOT_USER（例如: minioadmin）")
                print_info("  • Secret Key = MINIO_ROOT_PASSWORD（例如: minioadmin123）")
                print_info("=" * 60)
                print_info("")
                default_endpoint = "http://host.docker.internal:9000"
                default_access_key = "minioadmin"
                default_secret_key = "minioadmin123"
            else:
                default_endpoint = "https://xxx.r2.cloudflarestorage.com" if s3_provider != "AWS S3" else ""
                default_access_key = ""
                default_secret_key = ""
            
            self.values['persistence']['s3']['endpoint'] = prompt(
                "S3 端点 URL", 
                default=default_endpoint, 
                required=(s3_provider != "AWS S3")
            )
            
            if s3_provider == "MinIO":
                print_info("")
                print_info("MinIO 认证信息：")
                print_info("  • Access Key = MINIO_ROOT_USER")
                print_info("  • Secret Key = MINIO_ROOT_PASSWORD")
                print_info("")
            
            self.values['persistence']['s3']['accessKey'] = prompt(
                f"Access Key{' (MinIO: MINIO_ROOT_USER)' if s3_provider == 'MinIO' else ''}", 
                default=default_access_key,
                required=True
            )
            self.values['persistence']['s3']['secretKey'] = prompt(
                f"Secret Key{' (MinIO: MINIO_ROOT_PASSWORD)' if s3_provider == 'MinIO' else ''}", 
                default=default_secret_key,
                required=True
            )
            self.values['persistence']['s3']['region'] = prompt(
                "区域", 
                default="us-east-1", 
                required=False
            )
            self.values['persistence']['s3']['bucketName'] = prompt(
                "Bucket 名称", 
                default="your-bucket-name", 
                required=True
            )
            
            address_type = prompt(
                "地址类型 (path-style/virtual-hosted-style, 留空使用默认)", 
                default="", 
                required=False
            )
            if address_type:
                self.values['persistence']['s3']['addressType'] = address_type
            
            # 如果启用了 MinIO，配置 MinIO
            if self.values['minio'].get('enabled', False):
                print_section("配置内置 MinIO")
                print_info("=" * 60)
                print_info("重要说明：内置 MinIO")
                print_info("=" * 60)
                print_info("此 MinIO 服务用于 plugin 构建，不用于业务对象存储。")
                print_info("业务对象存储请使用上面配置的外部 S3 服务。")
                print_info("=" * 60)
                print_info("")
                if prompt_yes_no("是否自动生成 MinIO root 密码?", default=True):
                    self.values['minio']['rootPassword'] = generate_secret(32)
                    print_success("已生成 MinIO root 密码")
                else:
                    self.values['minio']['rootPassword'] = prompt(
                        "MinIO root 密码", 
                        required=True
                    )
                
                self.values['minio']['rootUser'] = prompt(
                    "MinIO root 用户", 
                    default="minioadmin", 
                    required=False
                )
        
        # MinIO 配置 - 如果存储类型不是 s3，需要启用内置 MinIO
        if storage_type != "s3":
            print_section("内置 MinIO 配置")
            print_info("=" * 60)
            print_info("重要说明：内置 MinIO")
            print_info("=" * 60)
            print_info("此 MinIO 服务用于 plugin 构建，不用于业务对象存储。")
            print_info("业务对象存储请使用 persistence.type 配置的外部存储服务。")
            print_info("=" * 60)
            print_info("")
            self.values['minio']['enabled'] = True
            
            if prompt_yes_no("是否自动生成 MinIO root 密码?", default=True):
                self.values['minio']['rootPassword'] = generate_secret(32)
                print_success("已生成 MinIO root 密码")
            else:
                self.values['minio']['rootPassword'] = prompt(
                    "MinIO root 密码", 
                    required=True
                )
            
            self.values['minio']['rootUser'] = prompt(
                "MinIO root 用户", 
                default="minioadmin", 
                required=False
            )
    
    # ==================== 模块 3: 网络配置 ====================
    def configure_networking(self):
        """配置网络"""
        print_header("模块 3: 网络配置 (Networking)")
        
        # TLS 配置 - 放在网络配置模块，与 Ingress 联动
        print_section("TLS 配置")
        print_info("TLS 配置影响内部服务通信和 CORS 设置")
        print_warning("注意: TLS 配置必须与 Ingress 配置一致，否则会出现 CORS 跨域问题")
        
        use_tls = prompt_yes_no("是否启用 TLS (内部服务)?", default=False)
        self.values['global']['useTLS'] = use_tls
        
        if use_tls:
            print_info("已启用 TLS，后续 Ingress 配置也需要启用 TLS")
        
        # Ingress 配置
        print_section("Ingress 配置")
        # 企业版默认启用 Ingress
        self.values['ingress']['enabled'] = True
        print_info("已自动启用 Ingress（企业版默认配置）")
        
        # Ingress Class 选择
        print_info("")
        print_info("请选择 Ingress Controller 类型：")
        ingress_class_choice = prompt_choice(
            "Ingress Class 名称",
            ["nginx", "alb", "traefik", "istio", "其他"],
            default="nginx"
        )
        
        if ingress_class_choice == "nginx":
            self.values['ingress']['className'] = "nginx"
            print_info("")
            print_warning("提示: 请确保已安装 NGINX Ingress Controller")
            print_info("安装方法: kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml")
        elif ingress_class_choice == "alb":
            self.values['ingress']['className'] = "alb"
            print_info("")
            print_warning("提示: 请确保已安装 AWS Load Balancer Controller")
            print_info("安装方法: 参考 AWS EKS 文档配置 ALB Ingress Controller")
        elif ingress_class_choice == "traefik":
            self.values['ingress']['className'] = "traefik"
            print_info("")
            print_warning("提示: 请确保已安装 Traefik Ingress Controller")
        elif ingress_class_choice == "istio":
            self.values['ingress']['className'] = "istio"
            print_info("")
            print_warning("提示: 请确保已安装 Istio Gateway")
        else:
            # 其他选项，手动输入
            self.values['ingress']['className'] = prompt(
                "请输入 Ingress Class 名称", 
                default="", 
                required=False
            )
        
        # Ingress TLS 配置 - 与全局 TLS 联动
        if use_tls:
            print_info("由于已启用全局 TLS，建议 Ingress 也启用 TLS")
            ingress_tls = prompt_yes_no("是否在 Ingress 中配置 TLS?", default=True)
        else:
            ingress_tls = prompt_yes_no("是否在 Ingress 中配置 TLS?", default=False)
            
        if ingress_tls:
            print_info("TLS 证书配置:")
            print_info("  1. 可以通过 cert-manager 自动管理 (使用 annotations)")
            print_info("  2. 或者手动配置 TLS Secret")
            
            # TLS 配置示例
            tls_hosts = prompt(
                "TLS 主机列表 (逗号分隔, 例如: dify.example.com,api.dify.example.com)", 
                default="", 
                required=False
            )
            
            if tls_hosts:
                hosts_list = [h.strip() for h in tls_hosts.split(',') if h.strip()]
                if hosts_list:
                    # 创建 TLS 配置
                    if 'tls' not in self.values['ingress'] or not isinstance(self.values['ingress']['tls'], list):
                        self.values['ingress']['tls'] = []
                    
                    self.values['ingress']['tls'].append({
                        'hosts': hosts_list,
                        'secretName': prompt(
                            "TLS Secret 名称", 
                            default=f"{hosts_list[0]}-tls", 
                            required=False
                        ) or f"{hosts_list[0]}-tls"
                    })
            
            # 添加 cert-manager 注解示例
            if prompt_yes_no("是否使用 cert-manager 自动管理证书?", default=False):
                if 'annotations' not in self.values['ingress']:
                    self.values['ingress']['annotations'] = {}
                
                cluster_issuer = prompt(
                    "ClusterIssuer 名称 (例如: letsencrypt-prod)", 
                    default="", 
                    required=False
                )
                if cluster_issuer:
                    self.values['ingress']['annotations']['cert-manager.io/cluster-issuer'] = cluster_issuer
                    print_success(f"已配置 cert-manager ClusterIssuer: {cluster_issuer}")
        
        # 检查 TLS 一致性
        if use_tls and not ingress_tls:
            print_warning("警告: 全局 TLS 已启用，但 Ingress TLS 未启用，可能导致 CORS 问题")
            if prompt_yes_no("是否现在启用 Ingress TLS?", default=True):
                ingress_tls = True
                # 重新配置 TLS
                tls_hosts = prompt(
                    "TLS 主机列表 (逗号分隔)", 
                    default="", 
                    required=False
                )
                if tls_hosts:
                    hosts_list = [h.strip() for h in tls_hosts.split(',') if h.strip()]
                    if hosts_list:
                        if 'tls' not in self.values['ingress'] or not isinstance(self.values['ingress']['tls'], list):
                            self.values['ingress']['tls'] = []
                        self.values['ingress']['tls'].append({
                            'hosts': hosts_list,
                            'secretName': prompt(
                                "TLS Secret 名称", 
                                default=f"{hosts_list[0]}-tls", 
                                required=False
                            ) or f"{hosts_list[0]}-tls"
                        })
        
        if not use_tls and ingress_tls:
            print_warning("警告: Ingress TLS 已启用，但全局 TLS 未启用，建议保持一致")
            if prompt_yes_no("是否启用全局 TLS?", default=True):
                self.values['global']['useTLS'] = True
                use_tls = True
        
        # useIpAsHost 配置 - 企业版不支持，固定为 False
        self.values['ingress']['useIpAsHost'] = False
    
    # ==================== 模块 4: 邮件配置 ====================
    def configure_mail(self):
        """配置邮件"""
        print_header("模块 4: 邮件配置 (Mail Configuration)")
        
        mail_type = prompt_choice(
            "选择邮件服务类型",
            ["", "resend", "smtp"],
            default=""
        )
        
        self.values['mail']['type'] = mail_type
        
        if mail_type:
            self.values['mail']['defaultSender'] = prompt(
                "默认发件人地址 (例如: no-reply <no-reply@dify.ai>)", 
                default="YOUR EMAIL FROM (eg: no-reply <no-reply@dify.ai>)", 
                required=False
            )
            
            if mail_type == "resend":
                self.values['mail']['resend']['apiKey'] = prompt(
                    "Resend API Key", 
                    required=True
                )
                self.values['mail']['resend']['apiUrl'] = prompt(
                    "Resend API URL", 
                    default="https://api.resend.com", 
                    required=False
                )
            elif mail_type == "smtp":
                self.values['mail']['smtp']['server'] = prompt(
                    "SMTP 服务器", 
                    required=True
                )
                port = prompt("SMTP 端口", default="587", required=False)
                try:
                    self.values['mail']['smtp']['port'] = int(port)
                except ValueError:
                    self.values['mail']['smtp']['port'] = 587
                
                self.values['mail']['smtp']['username'] = prompt(
                    "SMTP 用户名", 
                    required=True
                )
                self.values['mail']['smtp']['password'] = prompt(
                    "SMTP 密码", 
                    required=True
                )
                self.values['mail']['smtp']['useTLS'] = prompt_yes_no(
                    "是否使用 TLS?", 
                    default=False
                )
    
    # ==================== 模块 5: 服务配置 ====================
    def configure_services(self):
        """配置服务"""
        print_header("模块 5: 服务配置 (Services Configuration)")
        
        # Enterprise 相关配置
        if self.values.get('enterprise', {}).get('enabled', True):
            print_section("Enterprise 服务配置")
            
            # 所有密钥都按注释自动生成
            print_info("Enterprise appSecretKey 将使用 openssl rand -base64 42 自动生成")
            self.values['enterprise']['appSecretKey'] = generate_secret(42)
            print_success(f"已生成 Enterprise appSecretKey: {self.values['enterprise']['appSecretKey'][:20]}...")
            
            print_info("adminAPIsSecretKeySalt 将使用 openssl rand -base64 42 自动生成")
            self.values['enterprise']['adminAPIsSecretKeySalt'] = generate_secret(42)
            print_success(f"已生成 adminAPIsSecretKeySalt: {self.values['enterprise']['adminAPIsSecretKeySalt'][:20]}...")
            
            print_info("passwordEncryptionKey 将使用 openssl rand -base64 32 自动生成 (32-byte AES-256 key)")
            self.values['enterprise']['passwordEncryptionKey'] = generate_secret(32)
            print_success(f"已生成 passwordEncryptionKey: {self.values['enterprise']['passwordEncryptionKey'][:20]}...")
            
            license_mode = prompt_choice(
                "License 模式",
                ["online", "offline"],
                default="online"
            )
            self.values['enterprise']['licenseMode'] = license_mode
            
            if license_mode == "online":
                # 使用默认 License 服务器 URL，不询问用户
                self.values['enterprise']['licenseServer'] = "https://licenses.dify.ai/server"
                print_info(f"License 服务器 URL: {self.values['enterprise']['licenseServer']}")
        
        print_section("服务启用状态")
        print_info("可以跳过此部分使用默认值，或根据需要调整")
        
        if prompt_yes_no("是否配置服务启用状态?", default=False):
            services = ['api', 'worker', 'workerBeat', 'web', 'sandbox', 
                       'enterprise', 'enterpriseAudit', 'enterpriseFrontend',
                       'ssrfProxy', 'unstructured', 'plugin_daemon', 'plugin_manager']
            
            for service in services:
                if service in self.values:
                    current = self.values[service].get('enabled', True)
                    self.values[service]['enabled'] = prompt_yes_no(
                        f"是否启用 {service}?", 
                        default=current
                    )
    
    # ==================== 主流程 ====================
    def generate(self):
        """生成配置"""
        print_header("Dify Helm Chart Values 生成器")
        print_info("此工具将引导您完成 values-prd.yaml 的配置")
        print_info("您可以随时按 Ctrl+C 退出")
        
        try:
            # 按顺序配置各个模块
            self.configure_global()
            self.configure_infrastructure()
            self.configure_networking()
            self.configure_mail()
            self.configure_services()
            
            # 保存文件
            output_file = "values-prd.yaml"
            if os.path.exists(output_file):
                if not prompt_yes_no(f"{output_file} 已存在，是否覆盖?", default=False):
                    output_file = prompt("请输入新的文件名", default="values-prd.yaml", required=False)
                    if not output_file:
                        output_file = "values-prd.yaml"
            
            self.save(output_file)
            
            print_header("配置完成!")
            print_success(f"配置文件已保存到: {output_file}")
            print_info("请检查配置文件并根据需要进行调整")
            print_info("然后可以使用: helm install <release-name> . -f values-prd.yaml")
            
        except KeyboardInterrupt:
            print("\n\n")
            print_warning("用户中断操作")
            if prompt_yes_no("是否保存当前进度?", default=False):
                output_file = prompt("请输入文件名", default="values-prd-partial.yaml", required=False)
                if output_file:
                    self.save(output_file)
                    print_success(f"部分配置已保存到: {output_file}")
            sys.exit(0)
        except Exception as e:
            print_error(f"生成配置时出错: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """主函数"""
    source_file = "values.yaml"
    
    if not os.path.exists(source_file):
        print_error(f"模板文件不存在: {source_file}")
        sys.exit(1)
    
    generator = ValuesGenerator(source_file)
    generator.generate()


if __name__ == "__main__":
    main()

