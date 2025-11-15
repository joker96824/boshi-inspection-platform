"""
任务数据模型
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Task(BaseModel):
    """任务模型"""
    
    __tablename__ = "tb_task"
    
    # 基础字段
    task_name = Column(String(100), nullable=False, comment="任务名称")
    robot_id = Column(String(36), ForeignKey("tb_robot.id", ondelete="CASCADE"), nullable=False, comment="执行机器人ID")
    task_items = Column(JSON, nullable=True, comment="任务巡检项目ID列表")
    task_order = Column(Integer, nullable=False, default=0, comment="任务执行顺序")
    task_res_prior = Column(Integer, nullable=False, default=1, comment="响应优先级")
    task_int_prior = Column(Integer, nullable=False, default=1, comment="打断优先级")
    
    # 关系
    robot = relationship("Robot", back_populates="tasks")
    schedules = relationship("TaskSchedule", back_populates="task")
    taskhistories = relationship("TaskHistory", back_populates="task")
    
    def __repr__(self):
        return f"<Task(id='{self.id}', task_name='{self.task_name}', robot_id='{self.robot_id}')>"
