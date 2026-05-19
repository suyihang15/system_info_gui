#!/usr/bin/env python3
import datetime
import getpass
import platform
import socket
import os
import sys
from tkinter import Tk, Button, Label, messagebox, filedialog
from tkinter import scrolledtext

try:
    import psutil
except ImportError:
    psutil = None

try:
    from openpyxl import Workbook
except ImportError:
    Workbook = None

try:
    import winreg
except ImportError:
    winreg = None


def bytes_to_human(value):
    if value is None or value < 0:
        return "未知"
    units = ["B", "KB", "MB", "GB", "TB"]
    number = float(value)
    for unit in units:
        if number < 1024 or unit == units[-1]:
            return f"{number:.2f} {unit}"
        number /= 1024
    return f"{number:.2f} PB"


def seconds_to_human(seconds):
    if seconds is None or seconds < 0:
        return "未知"
    delta = datetime.timedelta(seconds=int(seconds))
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, sec = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}天")
    if hours:
        parts.append(f"{hours}小时")
    if minutes:
        parts.append(f"{minutes}分钟")
    if sec or not parts:
        parts.append(f"{sec}秒")
    return "".join(parts)


def mhz_to_human(mhz):
    if mhz is None or mhz <= 0:
        return "未知"
    number = float(mhz)
    if number >= 1000:
        return f"{number / 1000:.2f} GHz"
    return f"{number:.2f} MHz"


def get_general_info():
    return {
        "主机名": socket.gethostname(),
        "操作系统": platform.system(),
        "系统版本": platform.version(),
        "发行版": platform.platform(),
        "体系结构": platform.machine(),
        "处理器": platform.processor(),
        "Python 版本": platform.python_version(),
        "当前用户": getpass.getuser(),
        "开机时长": seconds_to_human(datetime.datetime.now().timestamp() - psutil.boot_time()) if psutil else "未知",
    }


def get_cpu_info():
    if not psutil:
        return {"错误": "psutil 未安装，无法获取 CPU 信息"}
    freq = psutil.cpu_freq()
    return {
        "物理核心数": psutil.cpu_count(logical=False),
        "逻辑处理器数": psutil.cpu_count(logical=True),
        "当前 CPU 使用率": f"{psutil.cpu_percent(interval=1)}%",
        "当前频率": mhz_to_human(freq.current) if freq else "未知",
        "最大频率": mhz_to_human(freq.max) if freq else "未知",
    }


def get_memory_info():
    if not psutil:
        return {"错误": "psutil 未安装，无法获取内存信息"}
    vm = psutil.virtual_memory()
    return {
        "物理内存总量": bytes_to_human(vm.total),
        "可用内存": bytes_to_human(vm.available),
        "已用内存": bytes_to_human(vm.used),
        "内存使用率": f"{vm.percent}%",
        "交换区总量": bytes_to_human(psutil.swap_memory().total),
    }


def get_disk_info():
    if not psutil:
        return [{"错误": "psutil 未安装，无法获取磁盘信息"}]
    result = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, FileNotFoundError):
            continue
        result.append({
            "盘符": part.device,
            "挂载点": part.mountpoint,
            "文件系统": part.fstype,
            "总大小": bytes_to_human(usage.total),
            "已用": bytes_to_human(usage.used),
            "可用": bytes_to_human(usage.free),
            "使用率": f"{usage.percent}%",
        })
    return result


def get_network_info():
    if not psutil:
        return {"错误": "psutil 未安装，无法获取网络信息"}
    interfaces = {}
    for name, addrs in psutil.net_if_addrs().items():
        interfaces[name] = [addr.address for addr in addrs if addr.address]
    return {
        "网卡数量": len(interfaces),
        "网卡地址": interfaces,
        "总发送字节": bytes_to_human(psutil.net_io_counters().bytes_sent),
        "总接收字节": bytes_to_human(psutil.net_io_counters().bytes_recv),
    }


def get_process_info(max_items=15):
    if not psutil:
        return [{"错误": "psutil 未安装，无法获取进程信息"}]
    processes = []
    for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
        processes.append(proc.info)
    processes.sort(key=lambda item: item.get("cpu_percent", 0), reverse=True)
    return processes[:max_items]


def get_env_vars():
    return dict(os.environ)


def get_installed_programs_windows():
    if winreg is None:
        return [{"提示": "非 Windows 系统或无法读取注册表"}]
    programs = []
    paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for path in paths:
            try:
                with winreg.OpenKey(root, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, name) as subkey:
                                display_name, display_version = None, None
                                try:
                                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                except OSError:
                                    continue
                                try:
                                    display_version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                except OSError:
                                    display_version = "未知"
                                programs.append({"名称": display_name, "版本": display_version})
                        except OSError:
                            continue
            except OSError:
                continue
    return programs


def build_report():
    return {
        "系统信息": get_general_info(),
        "CPU 信息": get_cpu_info(),
        "内存信息": get_memory_info(),
        "磁盘信息": get_disk_info(),
        "网络信息": get_network_info(),
        "进程信息": get_process_info(),
        "环境变量": get_env_vars(),
        "已安装程序": get_installed_programs_windows(),
    }


def format_report(report):
    lines = []
    lines.append("=== 系统信息 ===")
    for key, value in report["系统信息"].items():
        lines.append(f"{key}: {value}")
    lines.append("\n=== CPU 信息 ===")
    for key, value in report["CPU 信息"].items():
        lines.append(f"{key}: {value}")
    lines.append("\n=== 内存信息 ===")
    for key, value in report["内存信息"].items():
        lines.append(f"{key}: {value}")
    lines.append("\n=== 磁盘信息 ===")
    for disk in report["磁盘信息"]:
        if isinstance(disk, dict):
            lines.append("- 磁盘分区：")
            for key, value in disk.items():
                lines.append(f"    {key}: {value}")
    lines.append("\n=== 网络信息 ===")
    for key, value in report["网络信息"].items():
        if key == "网卡地址":
            lines.append(f"{key}:")
            for nic, addrs in value.items():
                lines.append(f"    {nic}: {', '.join(addrs)}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("\n=== 重要进程（CPU 排名前 15） ===")
    for proc in report["进程信息"]:
        lines.append(f"PID {proc.get('pid')}  {proc.get('name')}  CPU {proc.get('cpu_percent')}%  内存 {proc.get('memory_percent'):.2f}%")
    lines.append("\n=== 环境变量（仅显示前 20 条） ===")
    env_items = list(report["环境变量"].items())[:20]
    for name, value in env_items:
        lines.append(f"{name}: {value}")
    lines.append("... (环境变量数量: {} )".format(len(report["环境变量"])))
    if isinstance(report["已安装程序"], list):
        lines.append("\n=== 已安装程序（仅展示前 20 条） ===")
        for program in report["已安装程序"][:20]:
            lines.append(f"{program.get('名称', program.get('display_name', '未知'))} {program.get('版本', program.get('display_version', ''))}")
    return "\n".join(lines)


def export_to_excel(report, filename):
    if Workbook is None:
        raise RuntimeError("openpyxl 未安装，请先安装 requirements.txt 中的依赖")
    wb = Workbook()
    wb.remove(wb.active)

    def write_dict(sheet_name, data):
        sheet = wb.create_sheet(title=sheet_name[:31])
        if isinstance(data, dict):
            sheet.append(["字段", "值"])
            for key, value in data.items():
                sheet.append([key, str(value)])
        elif isinstance(data, list):
            if not data:
                sheet.append(["提示", "无数据"])
                return
            headers = set()
            for item in data:
                if isinstance(item, dict):
                    headers.update(item.keys())
            headers = list(headers)
            sheet.append(headers)
            for item in data:
                if isinstance(item, dict):
                    row = [item.get(col, "") for col in headers]
                    sheet.append(row)
                else:
                    sheet.append([str(item)])
        else:
            sheet.append(["值"])
            sheet.append([str(data)])

    write_dict("系统信息", report["系统信息"])
    write_dict("CPU 信息", report["CPU 信息"])
    write_dict("内存信息", report["内存信息"])
    write_dict("磁盘信息", report["磁盘信息"])
    write_dict("网络信息", report["网络信息"])
    write_dict("进程信息", report["进程信息"])
    write_dict("环境变量", [{"变量名": k, "值": v} for k, v in report["环境变量"].items()])
    if isinstance(report["已安装程序"], list):
        write_dict("已安装程序", report["已安装程序"])

    wb.save(filename)


def collect_and_show():
    if psutil is None:
        messagebox.showerror("缺少依赖", "psutil 未安装，请先运行：pip install -r requirements.txt")
        return
    data = build_report()
    global current_report
    current_report = data
    output = format_report(data)
    text_area.config(state="normal")
    text_area.delete("1.0", "end")
    text_area.insert("end", output)
    text_area.config(state="disabled")
    export_button.config(state="normal")
    status_label.config(text="已完成信息采集，您可以导出为 Excel。")


def export_current_report():
    if current_report is None:
        messagebox.showwarning("未采集", "请先点击“采集信息”按钮收集系统信息。")
        return
    if Workbook is None:
        messagebox.showerror("缺少依赖", "openpyxl 未安装，请先运行：pip install -r requirements.txt")
        return
    filepath = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel 文件", "*.xlsx")],
        initialfile="system_info_report.xlsx",
        title="保存 Excel 文件",
    )
    if not filepath:
        return
    try:
        export_to_excel(current_report, filepath)
        messagebox.showinfo("导出成功", f"系统信息已导出到 Excel：\n{filepath}")
    except Exception as exc:
        messagebox.showerror("导出失败", f"导出 Excel 失败：{exc}")


def create_gui():
    root = Tk()
    root.title("系统信息采集器")
    root.geometry("900x700")
    root.resizable(True, True)

    Label(root, text="系统信息采集器", font=("微软雅黑", 18, "bold")).pack(pady=10)
    Label(root, text="点击下方按钮即可收集电脑上的硬件和软件信息，结果会直接显示在窗口中。").pack(pady=5)

    collect = Button(root, text="采集信息", width=15, command=collect_and_show)
    collect.pack(pady=8)

    global export_button
    export_button = Button(root, text="导出 Excel", width=15, state="disabled", command=export_current_report)
    export_button.pack(pady=8)

    global status_label
    status_label = Label(root, text="请先点击“采集信息”开始收集。", anchor="w")
    status_label.pack(fill="x", padx=10, pady=6)

    global text_area
    text_area = scrolledtext.ScrolledText(root, wrap="word", font=("Consolas", 11), state="disabled")
    text_area.pack(fill="both", expand=True, padx=10, pady=10)

    return root


current_report = None


def main():
    root = create_gui()
    root.mainloop()


if __name__ == "__main__":
    main()
