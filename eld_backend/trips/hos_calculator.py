# from datetime import datetime, timedelta
# from typing import List, Dict, Tuple

# class HOSCalculator:
#     """Calculate Hours of Service compliance based on FMCSA regulations"""
    
#     def __init__(self, current_cycle_hours: float):
#         self.current_cycle_hours = current_cycle_hours
#         self.max_cycle_hours = 70  # 70-hour/8-day rule
#         self.max_daily_driving = 11  # 11-hour driving limit
#         self.max_duty_window = 14   # 14-hour driving window
#         self.min_off_duty = 10      # 10 consecutive hours off duty
#         self.break_requirement = 8  # 30-min break after 8 hours driving
        
#     def calculate_available_hours(self) -> Dict[str, float]:
#         """Calculate how many hours are available for driving and duty"""
#         remaining_cycle = max(0, self.max_cycle_hours - self.current_cycle_hours)
        
#         return {
#             'remaining_cycle_hours': remaining_cycle,
#             'max_daily_driving': self.max_daily_driving,
#             'max_duty_window': self.max_duty_window,
#             'can_drive_today': remaining_cycle >= 11
#         }
    
#     def plan_driving_schedule(self, total_drive_time: float, start_time: datetime = None) -> List[Dict]:
#         """Plan when driving, breaks, and rest periods should occur"""
#         if not start_time:
#             start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        
#         schedule = []
#         current_time = start_time
#         remaining_drive_time = total_drive_time
#         current_cycle_used = self.current_cycle_hours
        
#         day_number = 1
        
#         while remaining_drive_time > 0:
#             available = self.calculate_available_hours()
            
#             if not available['can_drive_today'] or current_cycle_used >= self.max_cycle_hours:
#                 # Need a 34-hour restart
#                 schedule.append({
#                     'type': 'rest_period',
#                     'start_time': current_time,
#                     'end_time': current_time + timedelta(hours=34),
#                     'duration': 34,
#                     'reason': '34-hour restart required'
#                 })
#                 current_time += timedelta(hours=34)
#                 current_cycle_used = 0
#                 continue
            
#             # Plan a day of driving
#             day_schedule = self.plan_single_day(
#                 current_time, 
#                 min(remaining_drive_time, self.max_daily_driving),
#                 day_number
#             )
            
#             schedule.extend(day_schedule)
            
#             # Update counters
#             daily_drive_time = sum(item['duration'] for item in day_schedule if item['type'] == 'driving')
#             daily_total_time = sum(item['duration'] for item in day_schedule if item['type'] != 'off_duty')
            
#             remaining_drive_time -= daily_drive_time
#             current_cycle_used += daily_total_time
            
#             # Move to next day
#             last_item = day_schedule[-1]
#             current_time = last_item['end_time']
            
#             # Add mandatory 10-hour break if more driving needed
#             if remaining_drive_time > 0:
#                 schedule.append({
#                     'type': 'off_duty',
#                     'start_time': current_time,
#                     'end_time': current_time + timedelta(hours=10),
#                     'duration': 10,
#                     'reason': 'Mandatory 10-hour rest'
#                 })
#                 current_time += timedelta(hours=10)
            
#             day_number += 1
        
#         return schedule
    
#     def plan_single_day(self, start_time: datetime, drive_time_needed: float, day_number: int) -> List[Dict]:
#         """Plan a single day's driving schedule"""
#         schedule = []
#         current_time = start_time
#         remaining_drive = drive_time_needed
#         consecutive_drive_time = 0
        
#         # Pre-trip inspection and preparation
#         schedule.append({
#             'type': 'on_duty_not_driving',
#             'start_time': current_time,
#             'end_time': current_time + timedelta(minutes=30),
#             'duration': 0.5,
#             'activity': 'Pre-trip inspection',
#             'day': day_number
#         })
#         current_time += timedelta(minutes=30)
        
#         while remaining_drive > 0 and (current_time - start_time).total_seconds() / 3600 < self.max_duty_window:
#             # Check if we need a 30-minute break
#             if consecutive_drive_time >= self.break_requirement and remaining_drive > 0:
#                 schedule.append({
#                     'type': 'break',
#                     'start_time': current_time,
#                     'end_time': current_time + timedelta(minutes=30),
#                     'duration': 0.5,
#                     'activity': 'Mandatory 30-minute break',
#                     'day': day_number
#                 })
#                 current_time += timedelta(minutes=30)
#                 consecutive_drive_time = 0
            
#             # Calculate how much we can drive this segment
#             max_segment = min(
#                 remaining_drive,
#                 self.break_requirement - consecutive_drive_time if consecutive_drive_time < self.break_requirement else remaining_drive,
#                 self.max_duty_window - (current_time - start_time).total_seconds() / 3600
#             )
            
#             if max_segment <= 0:
#                 break
            
#             # Add driving time
#             drive_duration = min(max_segment, 4)  # Drive in 4-hour chunks max
#             schedule.append({
#                 'type': 'driving',
#                 'start_time': current_time,
#                 'end_time': current_time + timedelta(hours=drive_duration),
#                 'duration': drive_duration,
#                 'activity': 'Driving',
#                 'day': day_number
#             })
            
#             current_time += timedelta(hours=drive_duration)
#             remaining_drive -= drive_duration
#             consecutive_drive_time += drive_duration
        
#         # Post-trip activities
#         schedule.append({
#             'type': 'on_duty_not_driving',
#             'start_time': current_time,
#             'end_time': current_time + timedelta(minutes=30),
#             'duration': 0.5,
#             'activity': 'Post-trip inspection and paperwork',
#             'day': day_number
#         })
        
#         return schedule