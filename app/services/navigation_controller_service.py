"""
导航控制器配置业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import pandas as pd

from ..repositories.navigationcontroller_repository import NavigationControllerRepository
from ..schemas.navigationcontroller import (
    NavigationControllerCreate, NavigationControllerUpdate, NavigationControllerQuery,
    NavigationControllerImportRequest, NavigationControllerImportResponse
)
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError, ValidationError
)
from ..utils.response import ApiResponse
from ..utils.excel_utils import ExcelProcessor
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class NavigationControllerService:
    """导航控制器配置业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NavigationControllerRepository(db)

    async def create_navigation_controller(self, data: NavigationControllerCreate, user: dict) -> Dict[str, Any]:
        """创建导航控制器配置"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建导航控制器配置
            navigation_controller = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_navigation_controller",
                f"创建导航控制器配置: 模块组{navigation_controller.module_group}",
                extra={"controller_id": navigation_controller.id, "module_group": navigation_controller.module_group}
            )

            return ApiResponse.success(
                data=self._format_controller_response(navigation_controller),
                message="导航控制器配置创建成功"
            )

        except Exception as e:
            logger.error(f"创建导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"创建导航控制器配置失败: {str(e)}")

    async def get_navigation_controller_by_id(self, controller_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取导航控制器配置"""
        try:
            navigation_controller = await self.repo.get_by_id(controller_id)
            if not navigation_controller:
                raise ResourceNotFoundError(f"导航控制器配置ID '{controller_id}' 不存在")

            return ApiResponse.success(
                data=self._format_controller_response(navigation_controller),
                message="获取导航控制器配置成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"获取导航控制器配置失败: {str(e)}")

    async def get_navigation_controllers_by_ids(self, navigationcontroller_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取导航控制器配置"""
        try:
            navigation_controllers = await self.repo.get_by_ids(navigationcontroller_ids)
            if not navigation_controllers:
                raise ResourceNotFoundError("未找到任何导航控制器配置")

            return ApiResponse.success(
                data=[self._format_controller_response(controller) for controller in navigation_controllers],
                message=f"成功获取 {len(navigation_controllers)} 个导航控制器配置"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量获取导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"批量获取导航控制器配置失败: {str(e)}")

    async def get_navigation_controllers_by_module_group(self, module_group: int, user: Optional[dict]) -> Dict[str, Any]:
        """根据模块组获取导航控制器配置"""
        try:
            navigation_controllers = await self.repo.get_by_module_group(module_group)
            if not navigation_controllers:
                raise ResourceNotFoundError(f"模块组 {module_group} 没有找到任何导航控制器配置")

            return ApiResponse.success(
                data=[self._format_controller_response(controller) for controller in navigation_controllers],
                message=f"成功获取模块组 {module_group} 的 {len(navigation_controllers)} 个导航控制器配置"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"根据模块组获取导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"根据模块组获取导航控制器配置失败: {str(e)}")

    async def get_navigation_controllers(self, query: NavigationControllerQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取导航控制器配置列表"""
        try:
            navigation_controllers, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                module_group=query.module_group,
                ethernet_ip=query.ethernet_ip,
                ethernet_port=query.ethernet_port,
                baud_rate=query.baud_rate
            )

            return ApiResponse.paginated(
                items=[self._format_controller_response(controller) for controller in navigation_controllers],
                total=total,
                page=query.page,
                size=query.size,
                message="获取导航控制器配置列表成功"
            )

        except Exception as e:
            logger.error(f"获取导航控制器配置列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取导航控制器配置列表失败: {str(e)}")

    async def update_navigation_controller(self, controller_id: str, data: NavigationControllerUpdate, user: dict) -> Dict[str, Any]:
        """更新导航控制器配置"""
        try:
            # 检查导航控制器配置是否存在
            existing_controller = await self.repo.get_by_id(controller_id)
            if not existing_controller:
                raise ResourceNotFoundError(f"导航控制器配置ID '{controller_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新导航控制器配置
            navigation_controller = await self.repo.update(controller_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_navigation_controller",
                f"更新导航控制器配置: 模块组{navigation_controller.module_group}",
                extra={"controller_id": navigation_controller.id, "module_group": navigation_controller.module_group}
            )

            return ApiResponse.success(
                data=self._format_controller_response(navigation_controller),
                message="导航控制器配置更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"更新导航控制器配置失败: {str(e)}")

    async def delete_navigation_controller(self, controller_id: str, user: dict) -> Dict[str, Any]:
        """删除导航控制器配置"""
        try:
            # 检查导航控制器配置是否存在
            existing_controller = await self.repo.get_by_id(controller_id)
            if not existing_controller:
                raise ResourceNotFoundError(f"导航控制器配置ID '{controller_id}' 不存在")

            # 软删除导航控制器配置
            success = await self.repo.soft_delete(controller_id, user["username"])
            if not success:
                raise BusinessError(f"删除导航控制器配置失败: 软删除操作返回失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_navigation_controller",
                f"删除导航控制器配置: 模块组{existing_controller.module_group}",
                extra={"controller_id": controller_id, "module_group": existing_controller.module_group}
            )

            return ApiResponse.success(
                data={"id": controller_id},
                message="导航控制器配置删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"删除导航控制器配置失败: {str(e)}")

    async def get_navigation_controller_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取导航控制器配置统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取导航控制器配置统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取导航控制器配置统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取导航控制器配置统计信息失败: {str(e)}")

    async def download_template(self) -> Any:
        """下载导航控制器配置模板"""
        try:
            # 定义模板列
            columns = [
                {"name": "模块组", "key": "module_group", "description": "模块组编号(1-10)"},
                {"name": "以太网IP", "key": "ethernet_ip", "description": "以太网通讯IP地址，如：192.168.1.100"},
                {"name": "子网掩码", "key": "subnet_mask", "description": "子网掩码，如：255.255.255.0"},
                {"name": "网关地址", "key": "gateway", "description": "网关地址，如：192.168.1.1"},
                {"name": "以太网端口", "key": "ethernet_port", "description": "以太网通讯端口号(1-65535)"},
                {"name": "波特率", "key": "baud_rate", "description": "波特率，可选值：9600,19200,38400,57600,115200,230400,460800,921600"},
                {"name": "减速距离", "key": "deceleration_distance", "description": "减速距离(mm)，范围：0-10000"},
                {"name": "停止距离", "key": "stop_distance", "description": "停止距离(mm)，范围：0-10000，必须大于减速距离"},
                {"name": "最大线速度", "key": "max_linear_velocity", "description": "路径最大线速度(m/s)，范围：0.001-10.000"},
                {"name": "最大角速度", "key": "max_angular_velocity", "description": "路径最大角速度(rad/s)，范围：0.001-10.000"},
                {"name": "加速度", "key": "acceleration", "description": "加速度(m/s²)，范围：0.001-10.000"},
                {"name": "减速度", "key": "deceleration", "description": "减速度(m/s²)，范围：0.001-10.000"},
                {"name": "膨胀系数", "key": "expansion_coefficient", "description": "膨胀系数，范围：0-2.0"}
            ]
            
            return ExcelProcessor.create_template(columns, "导航控制器配置模板")
            
        except Exception as e:
            logger.error(f"下载导航控制器配置模板失败: {e}", exc_info=True)
            raise BusinessError(f"下载模板失败: {str(e)}")

    async def export_navigation_controllers_by_filter(self, module_group: Optional[int] = None, 
                                                     ethernet_ip: Optional[str] = None,
                                                     ethernet_port: Optional[int] = None,
                                                     baud_rate: Optional[int] = None,
                                                     user: Optional[dict] = None) -> Any:
        """根据筛选条件导出导航控制器配置数据"""
        try:
            # 根据筛选条件获取数据
            navigation_controllers, total = await self.repo.get_all(
                page=1,
                size=10000,
                module_group=module_group,
                ethernet_ip=ethernet_ip,
                ethernet_port=ethernet_port,
                baud_rate=baud_rate
            )
            
            # 构建文件名
            sheet_name = "导航控制器配置数据(筛选)"
            filter_desc = []
            if module_group:
                filter_desc.append(f"模块组={module_group}")
            if ethernet_ip:
                filter_desc.append(f"IP={ethernet_ip}")
            if ethernet_port:
                filter_desc.append(f"端口={ethernet_port}")
            if baud_rate:
                filter_desc.append(f"波特率={baud_rate}")
            
            if filter_desc:
                sheet_name += f"({','.join(filter_desc)})"
            else:
                sheet_name += "(全部)"

            # 格式化数据
            data = [self._format_controller_response(controller) for controller in navigation_controllers]
            
            # 定义导出列
            columns = self._get_export_columns()
            
            # 记录操作日志
            if user:
                log_user_action(
                    logger, user["username"], "export_navigation_controllers_by_filter",
                    f"根据筛选条件导出导航控制器配置数据，共{len(data)}条记录"
                )
            
            return ExcelProcessor.export_data(data, columns, sheet_name)
            
        except Exception as e:
            logger.error(f"根据筛选条件导出导航控制器配置数据失败: {e}", exc_info=True)
            raise BusinessError(f"导出数据失败: {str(e)}")

    async def export_navigation_controllers_by_ids(self, controller_ids: List[str], 
                                                   user: Optional[dict] = None) -> Any:
        """根据ID列表导出导航控制器配置数据"""
        try:
            # 根据ID列表获取数据
            navigation_controllers = await self.repo.get_by_ids(controller_ids)
            
            if not navigation_controllers:
                raise ResourceNotFoundError("未找到任何导航控制器配置")
            
            # 构建文件名
            sheet_name = f"导航控制器配置数据(ID列表-{len(controller_ids)}个)"
            
            # 格式化数据
            data = [self._format_controller_response(controller) for controller in navigation_controllers]
            
            # 定义导出列
            columns = self._get_export_columns()
            
            # 记录操作日志
            if user:
                log_user_action(
                    logger, user["username"], "export_navigation_controllers_by_ids",
                    f"根据ID列表导出导航控制器配置数据，共{len(data)}条记录"
                )
            
            return ExcelProcessor.export_data(data, columns, sheet_name)
            
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"根据ID列表导出导航控制器配置数据失败: {e}", exc_info=True)
            raise BusinessError(f"导出数据失败: {str(e)}")

    def _get_export_columns(self) -> List[Dict[str, str]]:
        """获取导出列定义"""
        return [
            {"name": "模块组", "key": "module_group", "description": "模块组编号(1-10)"},
            {"name": "以太网IP", "key": "ethernet_ip", "description": "以太网通讯IP地址，如：192.168.1.100"},
            {"name": "子网掩码", "key": "subnet_mask", "description": "子网掩码，如：255.255.255.0"},
            {"name": "网关地址", "key": "gateway", "description": "网关地址，如：192.168.1.1"},
            {"name": "以太网端口", "key": "ethernet_port", "description": "以太网通讯端口号(1-65535)"},
            {"name": "波特率", "key": "baud_rate", "description": "波特率，可选值：9600,19200,38400,57600,115200,230400,460800,921600"},
            {"name": "减速距离", "key": "deceleration_distance", "description": "减速距离(mm)，范围：0-10000"},
            {"name": "停止距离", "key": "stop_distance", "description": "停止距离(mm)，范围：0-10000，必须大于减速距离"},
            {"name": "最大线速度", "key": "max_linear_velocity", "description": "路径最大线速度(m/s)，范围：0.001-10.000"},
            {"name": "最大角速度", "key": "max_angular_velocity", "description": "路径最大角速度(rad/s)，范围：0.001-10.000"},
            {"name": "加速度", "key": "acceleration", "description": "加速度(m/s²)，范围：0.001-10.000"},
            {"name": "减速度", "key": "deceleration", "description": "减速度(m/s²)，范围：0.001-10.000"},
            {"name": "膨胀系数", "key": "expansion_coefficient", "description": "膨胀系数，范围：0-2.0"},
            {"name": "创建时间", "key": "created_at", "description": "创建时间"},
            {"name": "创建者", "key": "created_by", "description": "创建者"}
        ]

    async def import_navigation_controllers(self, file_content: bytes, user: dict) -> Dict[str, Any]:
        """导入导航控制器配置数据"""
        try:
            # 解析Excel文件
            raw_data = ExcelProcessor.parse_excel(file_content)
            
            if not raw_data:
                raise ValidationError("Excel文件中没有有效数据")
            
            # 验证必填字段
            required_fields = ["模块组", "以太网IP", "以太网端口"]
            validation_errors = ExcelProcessor.validate_data(raw_data, required_fields)
            
            if validation_errors:
                return ApiResponse.success(
                    data={
                        "success_count": 0,
                        "failed_count": len(raw_data),
                        "errors": validation_errors,
                        "message": f"数据验证失败，共{len(validation_errors)}个错误"
                    },
                    message="导入失败"
                )
            
            # 转换数据格式
            success_count = 0
            failed_count = 0
            errors = []
            
            for idx, row in enumerate(raw_data, 1):
                try:
                    # 映射字段名
                    mapped_data = {
                        "module_group": int(row.get("模块组", 1)),
                        "ethernet_ip": str(row.get("以太网IP", "")),
                        "subnet_mask": str(row.get("子网掩码", "255.255.255.0")),
                        "gateway": str(row.get("网关地址", "192.168.1.1")),
                        "ethernet_port": int(row.get("以太网端口", 0)),
                        "baud_rate": int(row.get("波特率", 9600)),
                        "deceleration_distance": float(row.get("减速距离", 800.0)),
                        "stop_distance": float(row.get("停止距离", 1500.0)),
                        "max_linear_velocity": float(row.get("最大线速度", 0.8)),
                        "max_angular_velocity": float(row.get("最大角速度", 0.1)),
                        "acceleration": float(row.get("加速度", 0.8)),
                        "deceleration": float(row.get("减速度", 0.8)),
                        "expansion_coefficient": float(row.get("膨胀系数", 0.0)),
                        "created_by": user["username"],
                        "updated_by": user["username"]
                    }
                    
                    # 创建导航控制器配置
                    await self.repo.create(mapped_data)
                    success_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    errors.append(f"第{idx}行数据导入失败: {str(e)}")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "import_navigation_controllers",
                f"导入导航控制器配置数据，成功{success_count}条，失败{failed_count}条"
            )
            
            message = f"导入完成，成功{success_count}条，失败{failed_count}条"
            if errors:
                message += f"，错误详情：{'; '.join(errors[:5])}"  # 只显示前5个错误
                if len(errors) > 5:
                    message += f"等{len(errors)}个错误"
            
            return ApiResponse.success(
                data={
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "errors": errors,
                    "message": message
                },
                message="导入完成"
            )
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"导入导航控制器配置数据失败: {e}", exc_info=True)
            raise BusinessError(f"导入数据失败: {str(e)}")

    def _format_controller_response(self, navigation_controller) -> Dict[str, Any]:
        """格式化导航控制器配置响应数据"""
        return {
            "id": navigation_controller.id,
            "module_group": navigation_controller.module_group,
            "ethernet_ip": navigation_controller.ethernet_ip,
            "subnet_mask": navigation_controller.subnet_mask,
            "gateway": navigation_controller.gateway,
            "ethernet_port": navigation_controller.ethernet_port,
            "baud_rate": navigation_controller.baud_rate,
            "deceleration_distance": float(navigation_controller.deceleration_distance) if navigation_controller.deceleration_distance else 0.0,
            "stop_distance": float(navigation_controller.stop_distance) if navigation_controller.stop_distance else 0.0,
            "max_linear_velocity": float(navigation_controller.max_linear_velocity) if navigation_controller.max_linear_velocity else 0.0,
            "max_angular_velocity": float(navigation_controller.max_angular_velocity) if navigation_controller.max_angular_velocity else 0.0,
            "acceleration": float(navigation_controller.acceleration) if navigation_controller.acceleration else 0.0,
            "deceleration": float(navigation_controller.deceleration) if navigation_controller.deceleration else 0.0,
            "expansion_coefficient": float(navigation_controller.expansion_coefficient) if navigation_controller.expansion_coefficient else 0.0,
            "created_at": navigation_controller.created_at.strftime("%Y-%m-%dT%H:%M:%S") if navigation_controller.created_at else None,
            "updated_at": navigation_controller.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if navigation_controller.updated_at else None,
            "created_by": navigation_controller.created_by,
            "updated_by": navigation_controller.updated_by,
        }
