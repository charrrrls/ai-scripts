import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Dict

console = Console()
s = requests.Session()
s.headers.update({"User-Agent": "simple-client/0.3", "Accept": "application/json", "Content-Type": "application/json"})

def login() -> None:
    """执行登录并设置 Authorization 头。"""
    with console.status("[bold green]登录中...", spinner="dots"):
        try:
            r = s.post(
                "https://gaccode.com/api/login",
                json={"email": "953057856@qq.com", "password": "040819zhou."},
                timeout=8,
            )
        except requests.exceptions.RequestException as e:
            console.print(f"[red]登录请求异常: {e}[/red]")
            return
        if r.status_code == 200:
            try:
                login_data = r.json() or {}
                for key in ["token", "access_token", "jwt", "authToken"]:
                    if key in login_data and login_data[key]:
                        s.headers["Authorization"] = f"Bearer {login_data[key]}"
                        return
            except Exception as e:
                console.print(f"[red]解析登录响应失败: {e}[/red]")
        console.print(f"[red]登录失败，状态码: {r.status_code}[/red]")


def fetch_balance():
    """获取余额与上限。"""
    with console.status("[bold cyan]获取余额中...", spinner="dots"):
        r = s.get("https://gaccode.com/api/credits/balance", timeout=5)
        if r.status_code == 200:
            data = r.json() or {}
            return data.get("balance"), data.get("creditCap")
    return None, None


def fetch_history(hours: int = 24, limit: int = 200) -> List[dict]:
    """获取最近 hours 小时积分变动历史。"""
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(hours=hours)
    params = {
        "page": 1,
        "limit": limit,
        "startTime": start_dt.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "endTime": end_dt.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    }
    with console.status("[bold magenta]获取积分历史中...", spinner="dots"):
        r = s.get("https://gaccode.com/api/credits/history", params=params, timeout=10)
        if r.status_code == 200:
            try:
                payload = r.json()
                # 兼容 API 返回直接是数组或对象里含 history
                if isinstance(payload, list):
                    return payload
                if isinstance(payload, dict):
                    if isinstance(payload.get("history"), list):
                        return payload["history"]
                    # 有时可能用 data 字段
                    if isinstance(payload.get("data"), list):
                        return payload["data"]
                    # 检查其他可能的字段
                    for key in payload:
                        if isinstance(payload[key], list):
                            return payload[key]
            except Exception:
                pass
    return []


def parse_timestamp(item: dict) -> datetime | None:
    ts = None
    for key in ("createdAt", "timestamp", "time", "date"):
        if key in item:
            ts = item[key]
            break
    if ts is None:
        return None
    try:
        if isinstance(ts, (int, float)):
            if ts > 1e12:
                return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        tstr = str(ts)
        if tstr.endswith("Z"):
            tstr = tstr[:-1] + "+00:00"
        dt = datetime.fromisoformat(tstr)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def bucket_usage_refill(history: List[dict], interval_minutes: int = 10) -> Dict[str, List[float]]:
    """按 interval_minutes 桶化，返回 usage(消耗>0), refill(补充>0), net(净变化 可能为±)。"""
    
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(hours=24)
    # 对齐起点到整 interval
    interval = timedelta(minutes=interval_minutes)
    aligned_start = start_dt - timedelta(minutes=start_dt.minute % interval_minutes, seconds=start_dt.second, microseconds=start_dt.microsecond)
    # 生成桶
    buckets: List[datetime] = []
    cur = aligned_start
    while cur <= end_dt:
        buckets.append(cur)
        cur += interval
    usage = [0.0] * len(buckets)
    refill = [0.0] * len(buckets)
    net = [0.0] * len(buckets)

    def find_index(dt: datetime) -> int | None:
        if dt < aligned_start or dt > end_dt:
            return None
        delta = dt - aligned_start
        idx = int(delta.total_seconds() // (interval_minutes * 60))
        if 0 <= idx < len(buckets):
            return idx
        return None

    for item in history:
        dt = parse_timestamp(item)
        if dt is None:
            continue
        idx = find_index(dt)
        if idx is None:
            continue
        amt = item.get("amount")
        try:
            amt = float(amt)
        except Exception:
            continue
        if amt < 0:  # usage
            usage[idx] += -amt
        elif amt > 0:  # refill
            refill[idx] += amt
        net[idx] += amt

    return {
        "buckets": buckets,
        "usage": usage,
        "refill": refill,
        "net": net,
        "interval_minutes": interval_minutes,
    }


def render_usage_refill_chart(bucket_data: Dict[str, List[float]]):
    buckets: List[datetime] = bucket_data["buckets"]
    usage: List[float] = bucket_data["usage"]
    refill: List[float] = bucket_data["refill"]
    net: List[float] = bucket_data["net"]
    if not buckets:
        console.print("[yellow]无积分活动记录。[/yellow]")
        return
    
      
    # 降采样显示，确保在终端宽度内美观显示
    n = len(buckets)
    display_width = min(80, console.width - 10)  # 留出边距
    if n > display_width:
        # 等间隔采样
        step = n / display_width
        indices = [int(i * step) for i in range(display_width)]
        # 对于采样，我们需要聚合数据而不是只取单个点
        sampled_buckets = [buckets[i] for i in indices]
        sampled_usage = []
        sampled_refill = []
        sampled_net = []
        
        for i in range(display_width):
            start_idx = indices[i]
            end_idx = indices[i+1] if i+1 < len(indices) else n
            # 聚合这个范围内的数据
            sampled_usage.append(sum(usage[start_idx:end_idx]))
            sampled_refill.append(sum(refill[start_idx:end_idx]))
            sampled_net.append(sum(net[start_idx:end_idx]))
        
        buckets = sampled_buckets
        usage = sampled_usage
        refill = sampled_refill  
        net = sampled_net
        n = len(buckets)
      
    height = 12
    mid = height // 2
    canvas = [[" " for _ in range(n)] for _ in range(height)]
    max_usage = max(usage) if any(u > 0 for u in usage) else 1
    max_refill = max(refill) if any(r > 0 for r in refill) else 1
    
    # 绘制零基线
    for x in range(n):
        canvas[mid][x] = "─"

    # 绘制 usage (向下红色) 与 refill (向上绿色)
    for x in range(n):
        uh = int((usage[x] / max_usage) * (mid - 1)) if usage[x] > 0 else 0
        rh = int((refill[x] / max_refill) * (mid - 1)) if refill[x] > 0 else 0
        
        # usage: from mid+1 downward
        for y in range(mid + 1, min(height, mid + 1 + uh)):
            canvas[y][x] = "▌"
        # refill: from mid-1 upward  
        for y in range(mid - 1, max(-1, mid - 1 - rh), -1):
            canvas[y][x] = "▐"

    # 创建图表内容
    chart_lines = []
    for y in range(height):
        line_parts = []
        for x in range(n):
            ch = canvas[y][x]
            if ch == "▌":  # usage
                line_parts.append("[red]▌[/red]")
            elif ch == "▐":  # refill
                line_parts.append("[green]▐[/green]")
            elif ch == "─":
                line_parts.append("[dim]─[/dim]")
            else:
                line_parts.append(ch)
        chart_lines.append("".join(line_parts))

    # 时间轴
    time_axis = ""
    if n > 0:
        start_time = buckets[0].astimezone().strftime('%H:%M')
        end_time = buckets[-1].astimezone().strftime('%H:%M')
        mid_time = buckets[n//2].astimezone().strftime('%H:%M')
        
        # 创建对齐的时间轴
        time_axis = start_time + " " * (n//2 - len(start_time)//2 - len(mid_time)//2) + mid_time
        time_axis += " " * (n - len(time_axis) - len(end_time)) + end_time
  
    # 统计信息
    total_usage = sum(usage)
    total_refill = sum(refill)
    net_sum = sum(net)
    
    # 组装图表面板
    chart_content = "\n".join(chart_lines)
    chart_content += "\n" + "[dim]" + time_axis + "[/dim]"
    chart_content += f"\n[red]▌使用:{total_usage:.0f}[/red]  [green]▐补充:{total_refill:.0f}[/green]  [yellow]净变化:{net_sum:+.0f}[/yellow]"

    console.print(Panel(
        chart_content,
        title="📊 24小时积分变化图 (10分钟间隔)",
        title_align="center",
        border_style="cyan",
        padding=(1, 2)
    ))


def ascii_plot(*args, **kwargs):
    """占位：旧函数保留名避免潜在引用"""
    pass


def render_balance_panel(balance, credit_cap):
    if balance is None or credit_cap is None or credit_cap == 0:
        console.print("[red]无法获取余额信息。[/red]")
        return
    percentage = balance / credit_cap
    bar_width = 50
    filled = int(bar_width * percentage)
    bar = "█" * filled + "░" * (bar_width - filled)

    text = Text()
    text.append("💰 余额: ", style="bold cyan")
    text.append(f"{bar} ", style="green")
    text.append(f"{balance}/{credit_cap} ", style="bold white")
    text.append(f"({percentage:.1%})", style="bold green")

    console.print(Panel(text, border_style="blue", padding=(1, 2)))


def main():
    login()
    history = fetch_history(24)
    bucketed = bucket_usage_refill(history, interval_minutes=10)
    render_usage_refill_chart(bucketed)
    balance, credit_cap = fetch_balance()
    render_balance_panel(balance, credit_cap)


if __name__ == "__main__":
    main()