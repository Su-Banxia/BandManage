

band_manage/

├── app.py                  # 主应用入口

├── config.py               # 配置信息

├── auth/                   # 认证模块

│   ├── __init__.py

│   └── routes.py           # 登录/注册路由

├── routes/                 # 主要功能路由模块 (二级文件夹)

│   ├── bands/              # 乐队管理

│   │   ├── __init__.py

│   │   └── routes.py

│   ├── members/            # 成员管理

│   │   ├── __init__.py

│   │   └── routes.py

│   └── relationships/      # 关系管理

│       ├── __init__.py

│       └── routes.py

├── templates/              # HTML模板

│   ├── auth/

│   │   ├── login.html

│   │   └── register.html

│   ├── bands/

│   │   └── manage.html

│   ├── members/

│   │   └── manage.html

│   ├── relationships/

│   │   └── manage.html

│   └── index.html          # 主页

└── static/                 # 静态资源

​    ├── css/

​    └── js/

