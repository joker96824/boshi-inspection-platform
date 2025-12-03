"""
机器人业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.robot_repository import RobotRepository
from ..repositories.robotmap_repository import RobotMapRepository
from ..schemas.robot import RobotCreate, RobotUpdate, RobotResponse, RobotListResponse
from ..core.exceptions import ResourceNotFoundError, PermissionDeniedError
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class RobotService:
    """机器人业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.robot_repo = RobotRepository(db)
        self.robotmap_repo = RobotMapRepository(db)
    
    def _format_robot_response(self, robot) -> Dict[str, Any]:
        """格式化机器人响应数据"""
        # 获取关联的地图列表
        maps = []
        if hasattr(robot, 'maps') and robot.maps:
            maps = [
                {
                    "id": rm.map.id if rm.map else None,
                    "map_name": rm.map.map_name if rm.map else None,
                }
                for rm in robot.maps
                if not rm.is_deleted and rm.map and not rm.map.is_deleted
            ]
        
        # 格式化分组信息
        group_info = None
        if robot.group and not robot.group.is_deleted:
            group_info = {
                "id": robot.group.id,
                "group_name": robot.group.group_name,
                "group_description": robot.group.group_description,
            }
        
        return {
            "id": robot.id,
            "robot_name": robot.robot_name,
            "robot_info": robot.robot_info,
            "factory_id": robot.factory_id,
            "group_id": robot.group_id,
            "group": group_info,
            "preview_url": robot.preview_url,
            "control_url": robot.control_url,
            "maps": maps,
            "created_at": robot.created_at.strftime("%Y-%m-%dT%H:%M:%S") if robot.created_at else None,
            "updated_at": robot.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if robot.updated_at else None,
            "created_by": robot.created_by,
            "updated_by": robot.updated_by,
        }
    
    async def create_robot(self, robot_data: RobotCreate, user: dict) -> Dict[str, Any]:
        """创建机器人"""
        try:
            create_data = {
                "robot_name": robot_data.robot_name,
                "robot_info": robot_data.robot_info,
                "factory_id": robot_data.factory_id,
                "group_id": robot_data.group_id,
                "preview_url": robot_data.preview_url,
                "control_url": robot_data.control_url,
                "created_by": user["username"],
                "updated_by": user["username"]
            }
            
            robot = await self.robot_repo.create(create_data)
            
            # 创建机器人-地图关联
            if robot_data.map_ids:
                for map_id in robot_data.map_ids:
                    await self.robotmap_repo.create({
                        "robot_id": robot.id,
                        "map_id": map_id,
                        "created_by": user["username"],
                        "updated_by": user["username"]
                    })
            
            # 重新加载机器人以获取关联数据
            robot = await self.robot_repo.get_by_id(robot.id)
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "create_robot",
                "success",
                f"创建机器人成功，ID: {robot.id}"
            )
            
            return ApiResponse.success(
                data=self._format_robot_response(robot),
                message="创建机器人成功"
            )
            
        except Exception as e:
            logger.error(f"创建机器人失败: {e}")
            log_user_action(
                user["username"],
                "create_robot",
                "failed",
                f"创建机器人失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="创建机器人失败")
    
    async def get_robot_by_id(self, robot_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取机器人"""
        robot = await self.robot_repo.get_by_id(robot_id)
        if not robot:
            raise ResourceNotFoundError(f"机器人 '{robot_id}' 不存在")
        
        return ApiResponse.success(
            data=self._format_robot_response(robot),
            message="获取机器人成功"
        )
    
    async def get_robots_by_ids(self, robot_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取机器人"""
        try:
            robots = await self.robot_repo.get_by_ids(robot_ids)
            
            items_data = [self._format_robot_response(robot) for robot in robots]
            
            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取机器人列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取机器人列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取机器人列表失败")
    
    async def get_user_robots(self, user: Optional[dict], page: Optional[int] = None, size: Optional[int] = None, robot_name: str = None, factory_id: str = None, map_id: str = None) -> Dict[str, Any]:
        """获取所有机器人列表"""
        try:
            # 如果未提供分页参数，返回所有数据
            if page is None or size is None:
                robots, total = await self.robot_repo.get_all(None, None, robot_name, factory_id, map_id)
                items = [self._format_robot_response(robot) for robot in robots]
                return ApiResponse.success(
                    data={"items": items, "total": total},
                    message="获取机器人列表成功"
                )
            
            robots, total = await self.robot_repo.get_all(page, size, robot_name, factory_id, map_id)
            
            # 格式化响应数据
            items = [self._format_robot_response(robot) for robot in robots]
            
            return ApiResponse.paginated(
                items=items,
                total=total,
                page=page,
                size=size,
                message="获取机器人列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取机器人列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取机器人列表失败")
    
    async def update_robot(self, robot_id: str, robot_data: RobotUpdate, user: dict) -> Dict[str, Any]:
        """更新机器人"""
        # 检查机器人是否存在
        robot = await self.robot_repo.get_by_id(robot_id)
        if not robot:
            raise ResourceNotFoundError(f"机器人 '{robot_id}' 不存在")
        
        
        try:
            # 准备更新数据
            update_data = {}
            if robot_data.robot_name is not None:
                update_data["robot_name"] = robot_data.robot_name
            if robot_data.robot_info is not None:
                update_data["robot_info"] = robot_data.robot_info
            if robot_data.factory_id is not None:
                update_data["factory_id"] = robot_data.factory_id
            if robot_data.preview_url is not None:
                update_data["preview_url"] = robot_data.preview_url
            if robot_data.control_url is not None:
                update_data["control_url"] = robot_data.control_url
            if robot_data.group_id is not None:
                update_data["group_id"] = robot_data.group_id
            update_data["updated_by"] = user["username"]
            
            # 更新机器人
            updated_robot = await self.robot_repo.update(robot_id, update_data)
            
            # 更新机器人-地图关联
            if robot_data.map_ids is not None:
                # 获取现有的关联
                existing_maps = await self.robotmap_repo.get_maps_by_robot_id(robot_id)
                existing_map_ids = {rm.map_id for rm in existing_maps}
                new_map_ids = set(robot_data.map_ids)
                
                # 需要删除的关联（在现有中但不在新列表中）
                to_delete = existing_map_ids - new_map_ids
                for map_id in to_delete:
                    await self.robotmap_repo.delete_by_robot_and_map(robot_id, map_id)
                
                # 需要创建的关联（在新列表中但不在现有中）
                to_create = new_map_ids - existing_map_ids
                for map_id in to_create:
                    await self.robotmap_repo.create({
                        "robot_id": robot_id,
                        "map_id": map_id,
                        "created_by": user["username"],
                        "updated_by": user["username"]
                    })
            
            # 重新加载机器人以获取关联数据
            updated_robot = await self.robot_repo.get_by_id(robot_id)
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "update_robot",
                "success",
                f"更新机器人成功，ID: {robot_id}"
            )
            
            return ApiResponse.success(
                data=self._format_robot_response(updated_robot),
                message="更新机器人成功"
            )
            
        except Exception as e:
            logger.error(f"更新机器人失败: {e}")
            log_user_action(
                user["username"],
                "update_robot",
                "failed",
                f"更新机器人失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="更新机器人失败")
    
    async def delete_robot(self, robot_id: str, user: dict) -> Dict[str, Any]:
        """删除机器人"""
        # 检查机器人是否存在
        robot = await self.robot_repo.get_by_id(robot_id)
        if not robot:
            raise ResourceNotFoundError(f"机器人 '{robot_id}' 不存在")
        
        
        try:
            # 软删除机器人
            success = await self.robot_repo.soft_delete(robot_id)
            if not success:
                raise HTTPException(status_code=500, detail="删除机器人失败")
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "delete_robot",
                "success",
                f"删除机器人成功，ID: {robot_id}"
            )
            
            return ApiResponse.success(
                data={"id": robot_id},
                message="删除机器人成功"
            )
            
        except Exception as e:
            logger.error(f"删除机器人失败: {e}")
            log_user_action(
                user["username"],
                "delete_robot",
                "failed",
                f"删除机器人失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="删除机器人失败")
    
    async def get_robot_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取机器人统计信息"""
        try:
            total_count = await self.robot_repo.count_all()
            
            stats = {
                "total_robots": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取机器人统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取机器人统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取机器人统计失败")
    
    async def batch_update_group(self, robot_ids: List[str], group_id: Optional[str], user: dict) -> Dict[str, Any]:
        """批量更新机器人分组"""
        from ..repositories.group_repository import GroupRepository
        
        try:
            # 如果提供了group_id，验证分组是否存在
            if group_id is not None:
                group_repo = GroupRepository(self.db)
                group = await group_repo.get_by_id(group_id)
                if not group:
                    raise ResourceNotFoundError(f"分组 '{group_id}' 不存在")
            
            # 批量更新
            updated_count = await self.robot_repo.batch_update_group(
                robot_ids=robot_ids,
                group_id=group_id,
                updated_by=user["username"]
            )
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "batch_update_robot_group",
                "success",
                f"批量更新机器人分组成功，更新数量: {updated_count}"
            )
            
            return ApiResponse.success(
                data={"updated_count": updated_count},
                message=f"批量更新机器人分组成功，共更新 {updated_count} 个机器人"
            )
            
        except Exception as e:
            logger.error(f"批量更新机器人分组失败: {e}")
            log_user_action(
                user["username"],
                "batch_update_robot_group",
                "failed",
                f"批量更新机器人分组失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail=f"批量更新机器人分组失败: {str(e)}")
    
    async def get_robot_configs(self, robot_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据机器人ID获取所有配置模块数据"""
        try:
            # 验证机器人是否存在
            robot = await self.robot_repo.get_by_id(robot_id)
            if not robot:
                raise ResourceNotFoundError(f"机器人ID '{robot_id}' 不存在")
            
            # 导入所有配置模块的 repository
            from ..repositories.vehiclecontroller_repository import VehicleControllerRepository
            from ..repositories.navigationcontroller_repository import NavigationControllerRepository
            from ..repositories.environmentsensor_repository import EnvironmentSensorRepository
            from ..repositories.dualptz_repository import DualPTZRepository
            from ..repositories.motorstatus_repository import MotorStatusRepository
            from ..repositories.lidar_repository import LidarRepository
            from ..repositories.robotarm_repository import RobotArmRepository
            from ..repositories.ultrasonic_repository import UltrasonicRepository
            from ..repositories.depthcamera_repository import DepthCameraRepository
            
            # 导入所有配置模块的 service（用于格式化响应）
            from ..services.vehicle_controller_service import VehicleControllerService
            from ..services.navigation_controller_service import NavigationControllerService
            from ..services.environment_sensor_service import EnvironmentSensorService
            from ..services.dual_ptz_service import DualPTZService
            from ..services.motor_status_service import MotorStatusService
            from ..services.lidar_service import LidarService
            from ..services.robot_arm_service import RobotArmService
            from ..services.ultrasonic_service import UltrasonicService
            from ..services.depth_camera_service import DepthCameraService
            
            # 创建 repository 实例
            vehicle_controller_repo = VehicleControllerRepository(self.db)
            navigation_controller_repo = NavigationControllerRepository(self.db)
            environment_sensor_repo = EnvironmentSensorRepository(self.db)
            dual_ptz_repo = DualPTZRepository(self.db)
            motor_status_repo = MotorStatusRepository(self.db)
            lidar_repo = LidarRepository(self.db)
            robot_arm_repo = RobotArmRepository(self.db)
            ultrasonic_repo = UltrasonicRepository(self.db)
            depth_camera_repo = DepthCameraRepository(self.db)
            
            # 创建 service 实例（用于格式化）
            vehicle_controller_service = VehicleControllerService(self.db)
            navigation_controller_service = NavigationControllerService(self.db)
            environment_sensor_service = EnvironmentSensorService(self.db)
            dual_ptz_service = DualPTZService(self.db)
            motor_status_service = MotorStatusService(self.db)
            lidar_service = LidarService(self.db)
            robot_arm_service = RobotArmService(self.db)
            ultrasonic_service = UltrasonicService(self.db)
            depth_camera_service = DepthCameraService(self.db)
            
            # 并行查询所有配置模块
            vehicle_controller = await vehicle_controller_repo.get_by_robot_id(robot_id)
            navigation_controller = await navigation_controller_repo.get_by_robot_id(robot_id)
            environment_sensor = await environment_sensor_repo.get_by_robot_id(robot_id)
            # 双光云台、电机状态、超声波、深度相机支持多个配置，使用 get_all_by_robot_id
            dual_ptz_list = await dual_ptz_repo.get_all_by_robot_id(robot_id)
            motor_status_list = await motor_status_repo.get_all_by_robot_id(robot_id)
            lidar = await lidar_repo.get_by_robot_id(robot_id)
            robot_arm = await robot_arm_repo.get_by_robot_id(robot_id)
            ultrasonic_list = await ultrasonic_repo.get_all_by_robot_id(robot_id)
            depth_camera_list = await depth_camera_repo.get_all_by_robot_id(robot_id)
            
            # 调试日志（使用INFO级别确保能看到）
            logger.info(f"查询机器人 {robot_id} 的配置: vehicle_controller={vehicle_controller is not None}, "
                       f"navigation_controller={navigation_controller is not None}, "
                       f"environment_sensor={environment_sensor is not None}, "
                       f"dual_ptz_count={len(dual_ptz_list)}, "
                       f"motor_status_count={len(motor_status_list)}, "
                       f"lidar={lidar is not None}, "
                       f"robot_arm={robot_arm is not None}, "
                       f"ultrasonic_count={len(ultrasonic_list)}, "
                       f"depth_camera_count={len(depth_camera_list)}")
            
            # 格式化响应数据（添加异常处理）
            configs = {}
            try:
                configs["vehicle_controller"] = vehicle_controller_service._format_controller_response(vehicle_controller) if vehicle_controller else None
            except Exception as e:
                logger.error(f"格式化 vehicle_controller 失败: {e}", exc_info=True)
                configs["vehicle_controller"] = None
                
            try:
                configs["navigation_controller"] = navigation_controller_service._format_controller_response(navigation_controller) if navigation_controller else None
            except Exception as e:
                logger.error(f"格式化 navigation_controller 失败: {e}", exc_info=True)
                configs["navigation_controller"] = None
                
            try:
                configs["environment_sensor"] = environment_sensor_service._format_sensor_response(environment_sensor) if environment_sensor else None
            except Exception as e:
                logger.error(f"格式化 environment_sensor 失败: {e}", exc_info=True)
                configs["environment_sensor"] = None
                
            try:
                # 双光云台返回数组
                configs["dual_ptz"] = [dual_ptz_service._format_ptz_response(ptz) for ptz in dual_ptz_list] if dual_ptz_list else []
            except Exception as e:
                logger.error(f"格式化 dual_ptz 失败: {e}", exc_info=True)
                configs["dual_ptz"] = []
                
            try:
                # 电机状态返回数组
                configs["motor_status"] = [motor_status_service._format_status_response(status) for status in motor_status_list] if motor_status_list else []
            except Exception as e:
                logger.error(f"格式化 motor_status 失败: {e}", exc_info=True)
                configs["motor_status"] = []
                
            try:
                configs["lidar"] = lidar_service._format_lidar_response(lidar) if lidar else None
            except Exception as e:
                logger.error(f"格式化 lidar 失败: {e}", exc_info=True)
                configs["lidar"] = None
                
            try:
                configs["robot_arm"] = robot_arm_service._format_arm_response(robot_arm) if robot_arm else None
            except Exception as e:
                logger.error(f"格式化 robot_arm 失败: {e}", exc_info=True)
                configs["robot_arm"] = None
                
            try:
                # 超声波返回数组
                configs["ultrasonic"] = [ultrasonic_service._format_ultrasonic_response(ultrasonic) for ultrasonic in ultrasonic_list] if ultrasonic_list else []
            except Exception as e:
                logger.error(f"格式化 ultrasonic 失败: {e}", exc_info=True)
                configs["ultrasonic"] = []
                
            try:
                # 深度相机返回数组
                configs["depth_camera"] = [depth_camera_service._format_camera_response(camera) for camera in depth_camera_list] if depth_camera_list else []
            except Exception as e:
                logger.error(f"格式化 depth_camera 失败: {e}", exc_info=True)
                configs["depth_camera"] = []
            
            return ApiResponse.success(
                data={
                    "robot_id": robot_id,
                    "configs": configs
                },
                message="获取机器人配置成功"
            )
            
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取机器人配置失败: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"获取机器人配置失败: {str(e)}")
