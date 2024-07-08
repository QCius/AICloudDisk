# AI云盘后端仓库

**版本号**: 1.0.2

**说明**:后端实现的仓库

> [!NOTE]
>
> 如果你对后端代码作了修改，请更新版本号并补充README文档以及项目设计文档
>
> [项目设计文档](https://docs.qq.com/doc/DWENkYmJudmpzTHR1?scene=665ee40978d603bf2a0ba7bbwd6Ss1)

下面的链接是版本1.0.2的后端API（已部署公网，直接打开即可）

[后端API](http://115.29.186.14:8000/docs)

## 一、项目启动

**在linux上激活虚拟环境(请先忽略此步，出现依赖出错时执行此操作可能解决问题)**

```
source ./venv/bin/activate
```

**使用清华镜像安装 fastapi依赖 及  uvicorn 标准启动器**

```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi "uvicorn[standard]"
```

**安装数据库依赖 sqlalchemy**

```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sqlalchemy
```

**启动命令**

```
uvicorn AICloudDisk.main:app --reload --host 0.0.0.0 --port 8000
```

**查看文档访问地址**

```
http://127.0.0.1:8000/docs
```

## 二、版本更新内容

### 框架建构

基于`Fast API` 和所给代码给出了原始框架

### **用户管理**

用户注册、登录、退出登录、用户信息查看和修改

### 网盘管理

- 文件上传、下载、删除 （新增：只有验证过的用户才能对文件操作，用户独立操作自己的文件）
- 文件夹创建和删除（未实现）

### AI 助手

- 提供了AI聊天接口（支持单论对话和多轮对话）
- AI文件总结（参数：文件编号，额外要求信息（可选））

