# demoAPI
## 初始化python虚拟环境
`virtualenv venv`
## windows激活虚拟环境
`venv\Scripts\activate.bat`
## power shell激活虚拟环境
`venv\Scripts\activate.ps1`
## 使用清华镜像安装 fastapi依赖 及  uvicorn 标准启动器
`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi "uvicorn[standard]"`
## 安装数据库依赖 sqlalchemy
`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sqlalchemy`
## 启动命令
`uvicorn sql_app.main:app --reload --port 8000`
## 查看文档访问地址
`http://127.0.0.1:8000/docs`