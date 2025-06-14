# 乐队管理系统

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)

乐队管理系统是一个基于Flask的Web应用，用于管理乐队信息、成员、设备租赁、排练安排和表演活动。

## 主要功能

- **用户认证**：注册、登录和会话管理
- **乐队管理**：创建、编辑、删除乐队信息
- **成员管理**：管理乐队成员信息
- **设备租赁**：跟踪设备状态和租赁记录
- **排练管理**：排练室预约和时间安排
- **表演管理**：表演信息记录和曲目编排

## 使用说明

1. **首次使用**
   - 访问首页，注册管理员账户
   - 创建第一支乐队
   - 添加乐队成员

2. **设备管理**
   - 在设备模块添加设备（如乐器、音响等）
   - 设置设备状态（可用/租出/维修）

3. **租赁管理**
   - 为成员分配设备租赁
   - 跟踪设备归还状态
   - 查看设备租赁历史

4. **排练管理**
   - 预约排练室
   - 查看排练日历
   - 管理排练安排

5. **表演管理**
   - 创建表演记录（名称、时间、地点）
   - 编排表演曲目顺序
   - 管理表演详细信息

## 项目结构

```
BANDMANAGE/
├── auth/                      		# 用户认证模块
│   ├── __pycache__/          		# Python编译缓存
│   └── routes.py             		# 认证路由
├── routes/                   		# 应用路由模块
│   ├── bands/               		# 乐队管理路由
│   ├── equipment/           		# 设备管理路由
│   ├── equipment_rentals/   		# 设备租赁路由
│   │   ├── __pycache__/     		# 缓存
│   │   └── routes.py        		# 租赁业务逻辑
│   ├── members/             		# 成员管理路由
│   ├── performance_songs/    		# 表演曲目路由
│   ├── performances/         		# 表演管理路由
│   ├── rehearsals/           		# 排练管理路由
│   ├── relationships/       		# 关系管理路由
│   └── rooms/               		# 房间管理路由
├── sql/                      		# 数据库脚本
│   ├── fix.sql              		# 数据库修复脚本
│   ├── tables_create.sql    		# 表结构创建脚本
│   └── user.sql             		# 初始用户数据
├── static/                   		# 静态资源
│   ├── css/                 		# CSS样式表
│   └── js/                  		# JavaScript脚本
├── templates/                		# 前端模板
│   ├── auth/                		# 认证模板
│   ├── bands/               		# 乐队管理模板
│   ├── equipment/           		# 设备管理模板
│   ├── equipment_rentals/   		# 设备租赁模板
│   │   └── manage.html      		# 租赁管理主界面
│   ├── members/             		# 成员管理模板
│   ├── performance_songs/    		# 表演曲目模板
│   ├── performances/        		# 表演管理模板
│   ├── rehearsals/          		# 排练管理模板
│   ├── relationships/       		# 关系管理模板
│   ├── rooms/               		# 房间管理模板
│   └── index.html           		# 主页
├── .gitignore               		# Git忽略规则
└── app.py                   		# 应用入口
```

