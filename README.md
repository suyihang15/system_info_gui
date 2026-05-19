# 系统信息采集器 GUI 版本

这是一个基于 Python 的桌面应用程序，用于可视化采集电脑系统信息，并将采集结果整理展示在窗口中。用户可以直接点击“采集信息”按钮，查看系统信息，并导出为 Excel 表格。

## 功能特点

- 可视化采集按钮：点击“采集信息”即可获取电脑信息
- 直接展示：采集结果实时显示在应用窗口中，不使用 HTML/JS
- 支持导出 Excel：将所有信息整理到 `.xlsx` 文件中，方便分享和保存
- 支持 Windows 已安装程序信息采集

## 运行环境

- Windows / macOS / Linux
- Python 3.8 或更高版本
- 安装依赖：`psutil`, `openpyxl`, `pyinstaller`（仅用于打包）

## 使用方法

1. 打开 PowerShell，进入项目目录：

```powershell
cd "d:\zhuomian\新建文件夹 (2)"
```

2. 安装依赖：

```powershell
python -m pip install -r requirements.txt
```

3. 启动应用程序：

```powershell
python system_info_gui.py
```

4. 在窗口中操作：

- 点击“采集信息”按钮开始收集电脑信息
- 等待窗口显示系统、CPU、内存、磁盘、网络、进程、环境变量等信息
- 点击“导出 Excel”按钮，将当前结果保存为 `.xlsx` 文件

## 界面说明

- 采集按钮：按下后程序会读取本机硬件和软件信息
- 状态提示：显示当前是否已完成采集
- 文本输出区域：按模块分节展示采集后的结果
- 导出按钮：将全部信息写入 Excel，保存为表格文件

## 原理与思路

1. `psutil`：获取CPU、内存、磁盘、网络、进程等系统信息
2. `socket` 和 `platform`：获取主机名、操作系统与硬件类型
3. `os.environ`：读取当前环境变量
4. `openpyxl`：生成 Excel 文件并写入多张工作表
5. `tkinter`：创建桌面 GUI 界面，显示结果并提供按钮操作

程序流程：

- 用户点击“采集信息”按钮
- 程序调用信息采集函数，构建一个字典报告
- 将报告格式化为可读文本，显示在窗口中
- 用户点击“导出 Excel”按钮，程序把每个信息模块写入不同工作表

## 打包成 EXE

如果你希望把程序打包成单个可执行文件，请按以下步骤操作：

1. 安装 PyInstaller（如果尚未安装）：

```powershell
python -m pip install pyinstaller
```

2. 执行打包脚本：

```powershell
.\build_exe.ps1
```

3. 完成后，生成的可执行文件位于：

```text
dist\SystemInfoCollector.exe
```

### 直接使用 PyInstaller 命令

```powershell
pyinstaller --onefile --noconsole --name SystemInfoCollector system_info_gui.py
```

如果希望带控制台窗口显示调试信息，可以去掉 `--noconsole`。

## 文件说明

- `system_info_gui.py`：主程序源码
- `requirements.txt`：运行和打包所需依赖
- `README.md`：项目说明与使用方法

## 成品展示   
<img width="1324" height="1095" alt="屏幕截图 2026-05-19 193657" src="https://github.com/user-attachments/assets/ad00a9cc-e020-4390-b5de-7fa49e9f3dbe" />
