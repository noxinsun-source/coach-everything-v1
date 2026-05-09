"""
Timer & Analytics Module
- Pomodoro timer with break tracking
- Task duration recording
- Gantt chart generation
- Time statistics
"""

import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional
import statistics

logger = logging.getLogger(__name__)


@dataclass
class TaskTimeLog:
    """Record of task time"""
    task_id: str
    task_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: int = 0
    estimated_minutes: int = 120
    pomodoros_completed: int = 0  # Number of 25-min pomodoros

    def complete(self):
        """Mark task as complete"""
        self.end_time = datetime.now()
        self.duration_minutes = int(
            (self.end_time - self.start_time).total_seconds() / 60
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'estimated_minutes': self.estimated_minutes,
            'pomodoros_completed': self.pomodoros_completed,
            'variance_percent': self._calculate_variance(),
        }

    def _calculate_variance(self) -> float:
        """Calculate variance from estimate"""
        if self.duration_minutes == 0:
            return 0
        return ((self.duration_minutes - self.estimated_minutes) / self.estimated_minutes) * 100


class PomodoroTimer:
    """
    Pomodoro Timer (25 min work + 5 min break)
    """

    WORK_DURATION = 25  # minutes
    SHORT_BREAK = 5    # minutes
    LONG_BREAK = 15    # minutes (every 4 pomodoros)

    def __init__(self, task_id: str, task_name: str, estimated_minutes: int = 120):
        self.task_id = task_id
        self.task_name = task_name
        self.estimated_minutes = estimated_minutes
        self.current_pomodoro = 0
        self.is_running = False
        self.start_time = None

    def start_work_session(self):
        """Start a 25-minute work session"""
        self.is_running = True
        self.start_time = datetime.now()
        self.current_pomodoro += 1

        message = f"""
🍅 Pomodoro #{self.current_pomodoro} 开始！
⏱️  工作时间：{self.WORK_DURATION} 分钟
📌 任务：{self.task_name}

专注时间！不要分心，到点了会提醒你。
        """
        return message

    def end_work_session(self) -> Dict:
        """End current work session and suggest break"""
        self.is_running = False
        elapsed = datetime.now() - self.start_time

        is_long_break = (self.current_pomodoro % 4 == 0)
        break_duration = self.LONG_BREAK if is_long_break else self.SHORT_BREAK

        message = f"""
✅ Pomodoro #{self.current_pomodoro} 完成！
⏱️  工作时长：{elapsed.total_seconds() / 60:.1f} 分钟

休息一下（{break_duration} 分钟）
"""
        if is_long_break:
            message += f"🎉 4 个 Pomodoro 完成！长休息 {break_duration} 分钟吧。"

        return {
            'message': message,
            'pomodoro': self.current_pomodoro,
            'break_minutes': break_duration,
            'elapsed_minutes': elapsed.total_seconds() / 60,
        }

    def get_status(self) -> str:
        """Get current status"""
        if self.is_running:
            elapsed = datetime.now() - self.start_time
            return f"⏱️  正在工作... {elapsed.total_seconds() / 60:.1f} / {self.WORK_DURATION} 分钟"
        return f"✅ 已完成 {self.current_pomodoro} 个 Pomodoro"


class TimeAnalytics:
    """
    Analytics for task time tracking and Gantt chart generation
    """

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.logs: List[TaskTimeLog] = []
        self._load_logs()

    def _load_logs(self):
        """Load time logs from file"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                data = json.load(f)
                # Reconstruct TaskTimeLog objects
                # (simplified - in production, use proper deserialization)

    def add_log(self, log: TaskTimeLog):
        """Add a time log entry"""
        self.logs.append(log)
        self._save_logs()

    def _save_logs(self):
        """Save logs to file"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump([log.to_dict() for log in self.logs], f, indent=2)

    def generate_gantt_chart(self) -> str:
        """
        Generate ASCII Gantt chart for task timeline
        """
        if not self.logs:
            return "No time logs yet."

        # Sort by start time
        sorted_logs = sorted(self.logs, key=lambda x: x.start_time)

        chart = "📊 任务完成甘特图\n\n"
        chart += "时间轴 (左←→右)\n"
        chart += "=" * 80 + "\n\n"

        min_time = sorted_logs[0].start_time
        max_time = max(log.end_time or datetime.now() for log in sorted_logs)
        total_duration = (max_time - min_time).total_seconds() / 3600  # hours

        for log in sorted_logs:
            # Calculate position in chart
            start_offset = (log.start_time - min_time).total_seconds() / 3600
            if log.end_time:
                bar_length = (log.end_time - log.start_time).total_seconds() / 3600
            else:
                bar_length = 1

            # Create visual bar
            bar = "█" * max(1, int(bar_length * 10))
            spaces = " " * max(0, int(start_offset * 10))

            variance = log._calculate_variance()
            variance_str = f"({variance:+.0f}%)" if log.duration_minutes > 0 else ""

            chart += f"{log.task_name[:20]:20} {spaces}{bar} {log.duration_minutes}min {variance_str}\n"

        chart += "\n" + "=" * 80
        chart += f"\n总耗时: {(max_time - min_time).total_seconds() / 3600:.1f} 小时\n"

        return chart

    def generate_statistics(self) -> Dict:
        """Generate time statistics"""
        if not self.logs:
            return {}

        durations = [log.duration_minutes for log in self.logs if log.duration_minutes > 0]
        estimates = [log.estimated_minutes for log in self.logs]

        return {
            'total_tasks': len(self.logs),
            'completed_tasks': len([l for l in self.logs if l.duration_minutes > 0]),
            'average_duration': statistics.mean(durations) if durations else 0,
            'median_duration': statistics.median(durations) if durations else 0,
            'total_time_hours': sum(durations) / 60 if durations else 0,
            'estimation_accuracy': self._calculate_accuracy(durations, estimates),
            'time_trend': self._calculate_trend(durations),
        }

    def _calculate_accuracy(self, actuals: List[int], estimates: List[int]) -> float:
        """Calculate estimation accuracy percentage"""
        if not actuals:
            return 0
        variances = [abs(a - e) / e for a, e in zip(actuals, estimates) if e > 0]
        if not variances:
            return 0
        avg_variance = statistics.mean(variances)
        return max(0, 100 - (avg_variance * 100))

    def _calculate_trend(self, durations: List[int]) -> str:
        """Analyze if tasks are getting faster or slower"""
        if len(durations) < 2:
            return "insufficient_data"

        first_half_avg = statistics.mean(durations[:len(durations)//2])
        second_half_avg = statistics.mean(durations[len(durations)//2:])

        if second_half_avg < first_half_avg * 0.9:
            return "improving"  # 快了 10%
        elif second_half_avg > first_half_avg * 1.1:
            return "slowing"    # 慢了 10%
        else:
            return "stable"

    def generate_time_report(self) -> str:
        """Generate comprehensive time report"""
        stats = self.generate_statistics()

        if not stats:
            return "No time data yet. Start a task to begin tracking!"

        report = f"""
⏱️  时间统计报告

📊 任务数据：
   ✅ 已完成任务: {stats['completed_tasks']}/{stats['total_tasks']}
   ⏱️  平均耗时: {stats['average_duration']:.0f} 分钟
   📈 中位数: {stats['median_duration']:.0f} 分钟
   🕐 总耗时: {stats['total_time_hours']:.1f} 小时

🎯 估算准确度: {stats['estimation_accuracy']:.0f}%
📈 进度趋势: {self._get_trend_emoji(stats['time_trend'])} {stats['time_trend']}
"""
        return report

    @staticmethod
    def _get_trend_emoji(trend: str) -> str:
        """Get emoji for trend"""
        return {
            "improving": "⬇️",
            "slowing": "⬆️",
            "stable": "→",
            "insufficient_data": "❓"
        }.get(trend, "?")


def sync_to_ios_calendar(tasks: List[TaskTimeLog]) -> str:
    """
    Generate iCalendar format for iOS sync
    """
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Coach Everything//Task Schedule//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
"""

    for task in tasks:
        if task.start_time and task.end_time:
            start_str = task.start_time.strftime('%Y%m%dT%H%M%SZ')
            end_str = task.end_time.strftime('%Y%m%dT%H%M%SZ')

            ics_content += f"""BEGIN:VEVENT
UID:{task.task_id}@coach-everything
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:{task.task_name}
DESCRIPTION:Completed in {task.duration_minutes} minutes (estimated {task.estimated_minutes} min)
STATUS:COMPLETED
END:VEVENT
"""

    ics_content += "END:VCALENDAR"
    return ics_content
