import streamlit as st
from datetime import datetime, timedelta
import pytz

# ═══════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════
st.set_page_config(
    page_title="Lamma Ferry Tracker",
    page_icon="🚢",
    layout="wide"
)

# ═══════════════════════════════════════
# REAL FERRY SCHEDULE (from HKKF)
# ═══════════════════════════════════════

# Monday to Saturday (combined schedule)
# * = via Pak Kok Tsuen, # = cargo ferry (passengers also accepted)
# We include ALL times for simplicity

CENTRAL_TO_LAMMA_WEEKDAY = [
    "06:30", "07:00", "07:30", "07:50", "08:10", "08:30", "08:50",
    "09:10", "09:30", "10:10", "11:00", "12:00", "13:00", "13:45",
    "14:30", "15:15", "15:50", "16:30", "17:20", "17:40", "18:00",
    "18:20", "18:40", "19:00", "19:30", "20:00", "20:30", "21:00",
    "21:30", "22:30", "23:30"
]

# Saturday early morning ferry (2:30am)
CENTRAL_TO_LAMMA_SAT_EARLY = ["02:30"]

LAMMA_TO_CENTRAL_WEEKDAY = [
    "05:30", "06:20", "06:40", "07:00", "07:20", "07:40", "08:00",
    "08:20", "08:40", "09:00", "09:20", "09:40", "10:30", "11:20",
    "12:00", "13:00", "13:45", "14:30", "15:15", "16:00", "16:30",
    "17:15", "17:50", "18:10", "18:30", "18:50", "19:20", "20:00",
    "20:30", "21:30", "22:30", "23:30"
]

# Sunday and Public Holidays
CENTRAL_TO_LAMMA_SUNDAY = [
    "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00",
    "14:30", "15:00", "16:00", "16:30", "17:00", "17:30", "18:00",
    "18:30", "19:00", "19:30", "20:00", "20:30", "21:30", "22:30",
    "23:30"
]

# Sunday early morning ferry (2:30am)
CENTRAL_TO_LAMMA_SUN_EARLY = ["02:30"]

LAMMA_TO_CENTRAL_SUNDAY = [
    "05:30", "06:40", "07:30", "08:00", "08:30", "09:00", "09:30",
    "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00",
    "13:30", "14:00", "14:30", "15:30", "16:00", "16:30", "17:00",
    "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
    "21:30", "22:30", "23:30"
]

# Sunday late night ferry from Lamma
LAMMA_TO_CENTRAL_SUN_LATE = ["00:30"]  # 12:30am (next day)

# ═══════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════
def get_hk_time():
    """Get current Hong Kong time"""
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    return datetime.now(hk_tz)

def get_day_type(dt):
    """Determine the schedule type based on day"""
    weekday = dt.weekday()  # 0=Mon, 1=Tue, ..., 5=Sat, 6=Sun
    
    if weekday == 6:  # Sunday
        return "sunday"
    elif weekday == 5:  # Saturday
        return "saturday"
    else:  # Monday to Friday
        return "weekday"

def get_schedule(route, dt):
    """Get the correct schedule based on route, day, and time"""
    day_type = get_day_type(dt)
    current_time_str = dt.strftime("%H:%M")
    
    if route == "Central → Lamma":
        if day_type == "sunday":
            schedule = CENTRAL_TO_LAMMA_SUNDAY.copy()
            # Add 2:30am for Sunday (if current time is late night/early morning)
            schedule = CENTRAL_TO_LAMMA_SUN_EARLY + schedule
            schedule.sort()
            return schedule
        elif day_type == "saturday":
            schedule = CENTRAL_TO_LAMMA_WEEKDAY.copy()
            # Add 2:30am for Saturday early morning
            schedule = CENTRAL_TO_LAMMA_SAT_EARLY + schedule
            schedule.sort()
            return schedule
        else:  # weekday (Mon-Fri)
            return CENTRAL_TO_LAMMA_WEEKDAY
    
    else:  # Lamma → Central
        if day_type == "sunday":
            schedule = LAMMA_TO_CENTRAL_SUNDAY.copy()
            schedule.sort()
            return schedule
        elif day_type == "saturday":
            # Saturday uses weekday schedule + late night ferry?
            schedule = LAMMA_TO_CENTRAL_WEEKDAY.copy()
            schedule.sort()
            return schedule
        else:  # weekday
            return LAMMA_TO_CENTRAL_WEEKDAY

def parse_time(time_str, dt):
    """Convert time string like '06:30' or '02:30' to datetime"""
    hour, minute = map(int, time_str.split(':'))
    
    # Handle late night/early morning times (before 4am = next day)
    ferry_dt = dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # If the ferry time is more than 12 hours in the past, it might be tomorrow's
    if ferry_dt < dt - timedelta(hours=6):
        ferry_dt += timedelta(days=1)
    
    return ferry_dt

def get_next_ferries(route, dt, commute_minutes, num_ferries=10):
    """Get upcoming ferry times with leave-by times"""
    schedule = get_schedule(route, dt)
    ferries = []
    
    # Also check if we need tomorrow's early ferries
    tomorrow = dt + timedelta(days=1)
    tomorrow_schedule = get_schedule(route, tomorrow)
    
    # Combine today's remaining + tomorrow's early
    all_times = []
    
    # Today's remaining
    for time_str in schedule:
        ferry_time = parse_time(time_str, dt)
        if ferry_time > dt:
            all_times.append((time_str, ferry_time))
    
    # Tomorrow's early ferries (if today is almost over)
    for time_str in tomorrow_schedule:
        ferry_time = parse_time(time_str, tomorrow)
        # Only add tomorrow's if today has few ferries left
        if len(all_times) < 5:
            all_times.append((time_str, ferry_time))
    
    # Sort by time
    all_times.sort(key=lambda x: x[1])
    
    for time_str, ferry_time in all_times[:num_ferries]:
        leave_by = ferry_time - timedelta(minutes=commute_minutes)
        minutes_until = int((ferry_time - dt).total_seconds() / 60)
        
        # Determine status
        if leave_by <= dt:
            if minutes_until <= commute_minutes:
                status = "⚠️ Hurry!"
            else:
                status = "⚠️ Late"
        elif minutes_until <= commute_minutes + 5:
            status = "🏃 Leave now!"
        elif minutes_until <= commute_minutes + 15:
            status = "⏰ Soon"
        else:
            status = "✅ OK"
        
        # Format display
        if ferry_time.date() > dt.date():
            display_time = f"{time_str} (+1)"
        else:
            display_time = time_str
        
        ferries.append({
            'ferry_time': ferry_time,
            'display_time': display_time,
            'leave_by': leave_by,
            'minutes_until': minutes_until,
            'status': status,
        })
    
    return ferries

# ═══════════════════════════════════════
# CSS STYLING (Lamma beach vibes)
# ═══════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800;900&display=swap');
    * { font-family: 'Nunito', sans-serif; }
    .stApp { background: linear-gradient(135deg, #e8f8f5 0%, #d5f5e3 50%, #fef9e7 100%); }
    
    .app-header {
        background: linear-gradient(135deg, #0e6655, #1abc9c);
        padding: 25px 35px;
        border-radius: 0 0 30px 30px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(14,102,85,0.3);
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 900;
        color: white;
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.9);
        margin: 5px 0 0 0;
    }
    
    .current-time-box {
        background: white;
        border-radius: 20px;
        padding: 20px 30px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .current-time {
        font-size: 2.5rem;
        font-weight: 900;
        color: #0e6655;
    }
    
    .current-day {
        font-size: 1rem;
        color: #666;
        margin-bottom: 5px;
    }
    
    .ferry-card {
        background: white;
        border-radius: 16px;
        padding: 18px 22px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        transition: all 0.3s;
        border-left: 5px solid #ddd;
    }
    
    .ferry-card.next-ferry {
        border-left: 5px solid #27ae60;
        background: linear-gradient(135deg, #eafaf1, #f0fff0);
        box-shadow: 0 4px 20px rgba(39,174,96,0.2);
        transform: scale(1.02);
    }
    
    .ferry-card.hurry {
        border-left: 5px solid #e74c3c;
        background: #fff5f5;
    }
    
    .ferry-card.soon {
        border-left: 5px solid #f39c12;
        background: #fffdf5;
    }
    
    .ferry-time {
        font-size: 1.5rem;
        font-weight: 900;
        color: #0e6655;
        min-width: 100px;
    }
    
    .leave-by {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e74c3c;
        min-width: 150px;
    }
    
    .leave-by.ok {
        color: #27ae60;
    }
    
    .countdown {
        font-size: 0.9rem;
        color: #666;
    }
    
    .status-badge {
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-align: center;
        min-width: 100px;
        display: inline-block;
    }
    
    .status-badge.next {
        background: #27ae60;
        color: white;
    }
    
    .status-badge.hurry {
        background: #e74c3c;
        color: white;
        animation: pulse 1s infinite;
    }
    
    .status-badge.soon {
        background: #f39c12;
        color: white;
    }
    
    .status-badge.ok {
        background: #ecf0f1;
        color: #666;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .next-ferry-highlight {
        background: #27ae60;
        color: white;
        padding: 3px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-left: 10px;
    }
    
    .route-selector {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        margin-bottom: 20px;
    }
    
    .commute-info {
        background: #e8f8f5;
        border-radius: 12px;
        padding: 15px;
        margin: 15px 0;
        border: 2px solid #1abc9c;
    }
    
    .schedule-note {
        background: #fef9e7;
        border-radius: 8px;
        padding: 10px 15px;
        margin-top: 10px;
        font-size: 0.85rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# GET CURRENT TIME
# ═══════════════════════════════════════
hk_time = get_hk_time()
day_type = get_day_type(hk_time)

day_labels = {
    "weekday": "Monday - Friday",
    "saturday": "Saturday",
    "sunday": "Sunday / Public Holiday"
}
day_name = hk_time.strftime("%A")
schedule_label = day_labels.get(day_type, day_name)

# ═══════════════════════════════════════
# HEADER
# ═══════════════════════════════════════
st.markdown("""
<div class="app-header">
    <h1 class="app-title">🚢 Lamma Ferry Tracker</h1>
    <p class="app-subtitle">Central ↔ Yung Shue Wan • Real schedule from HKKF</p>
</div>
""", unsafe_allow_html=True)

# Current time
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div class="current-time-box">
        <div class="current-day">{day_name} • {schedule_label}</div>
        <div class="current-time">🕐 {hk_time.strftime('%I:%M %p')}</div>
        <div style="color:#999;font-size:0.9rem;">{hk_time.strftime('%d %B %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════
# ROUTE SELECTOR
# ═══════════════════════════════════════
st.markdown('<div class="route-selector">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    route = st.radio(
        "🛣️ Route",
        ["Central → Lamma", "Lamma → Central"],
        horizontal=True,
        help="Select your direction"
    )

with col2:
    if route == "Central → Lamma":
        commute_options = {
            "🏢 Office → Central Pier (45 min)": 45,
            "🏠 Home (outside Lamma) → Central Pier (30 min)": 30,
            "🚇 MTR → Central Pier (20 min)": 20,
            "📍 Already at Central Pier (0 min)": 0,
            "✏️ Custom...": None,
        }
    else:
        commute_options = {
            "🏠 Home → YSW Pier (15 min)": 15,
            "🏖️ Beach → YSW Pier (25 min)": 25,
            "🍽️ Restaurant → YSW Pier (10 min)": 10,
            "📍 Already at YSW Pier (0 min)": 0,
            "✏️ Custom...": None,
        }
    
    commute_label = st.selectbox(
        "🚶 Commute time to pier",
        list(commute_options.keys())
    )
    
    if commute_label == "✏️ Custom...":
        commute_minutes = st.number_input("Enter minutes", min_value=0, max_value=120, value=30)
    else:
        commute_minutes = commute_options[commute_label]

st.markdown('</div>', unsafe_allow_html=True)

# Commute info
st.markdown(f"""
<div class="commute-info">
    <strong>🚶 Commute:</strong> {commute_minutes} min &nbsp;|&nbsp;
    <strong>🚢 Route:</strong> {route} &nbsp;|&nbsp;
    <strong>📅 Schedule:</strong> {schedule_label}
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# FERRY LIST
# ═══════════════════════════════════════
st.markdown("### 🚢 Upcoming Ferries")

ferries = get_next_ferries(route, hk_time, commute_minutes, num_ferries=12)

if not ferries:
    st.warning("😴 No more ferries today! Check tomorrow's schedule or refresh.")
else:
    # Find the NEXT catchable ferry (first one you can actually make)
    next_catchable = None
    for f in ferries:
        if f['status'] in ["✅ OK", "⏰ Soon", "🏃 Leave now!"]:
            next_catchable = f
            break
    
    for ferry in ferries:
        is_next = (ferry == next_catchable)
        
        # Determine card styling
        if is_next:
            card_class = "next-ferry"
            status_class = "next"
        elif ferry['status'] in ["⚠️ Hurry!", "⚠️ Late", "🏃 Leave now!"]:
            card_class = "hurry"
            status_class = "hurry"
        elif ferry['status'] == "⏰ Soon":
            card_class = "soon"
            status_class = "soon"
        else:
            card_class = ""
            status_class = "ok"
        
        # Leave by text
        if ferry['leave_by'] <= hk_time:
            leave_text = "⚠️ Already late!"
        else:
            leave_text = f"🏃 Leave by {ferry['leave_by'].strftime('%I:%M %p')}"
        
        # Countdown
        mins = ferry['minutes_until']
        if mins < 0:
            countdown = "Departed"
        elif mins < 60:
            countdown = f"in {mins} min"
        else:
            hours = mins // 60
            remaining_mins = mins % 60
            countdown = f"in {hours}h {remaining_mins}m"
        
        # Next badge
        next_badge = '<span class="next-ferry-highlight">NEXT</span>' if is_next else ''
        
        # Columns layout
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"""
            <div style="font-size:1.5rem;font-weight:900;color:#0e6655;">
                🚢 {ferry['display_time']} {next_badge}
            </div>
            <div style="font-size:0.85rem;color:#999;">⏱️ {countdown}</div>
            """, unsafe_allow_html=True)
        
        with col2:
            leave_color = "#27ae60" if ferry['status'] == "✅ OK" else "#e74c3c"
            st.markdown(f"""
            <div style="font-size:1.1rem;font-weight:700;color:{leave_color};padding-top:15px;">
                {leave_text}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="padding-top:12px;">
                <span class="status-badge {status_class}">{ferry['status']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:5px 0;opacity:0.3;'>", unsafe_allow_html=True)

# ═══════════════════════════════════════
# SCHEDULE NOTES
# ═══════════════════════════════════════
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background:white;border-radius:16px;padding:20px;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
        <h4>📋 Schedule Notes</h4>
        <ul style="font-size:0.9rem;color:#666;">
            <li><strong>Sat & Sun:</strong> Extra 2:30am ferry from Central</li>
            <li><strong>Mon-Sat:</strong> Regular schedule shown</li>
            <li><strong>Sun/PH:</strong> Different schedule applies</li>
            <li>Schedules may change on public holidays</li>
            <li>Check <a href="https://www.hkkf.com.hk">HKKF website</a> for updates</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background:white;border-radius:16px;padding:20px;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
        <h4>💰 Fare Info</h4>
        <ul style="font-size:0.9rem;color:#666;">
            <li><strong>Adult:</strong> HK$27.50 (Mon-Sat) / HK$40.00 (Sun/PH)</li>
            <li><strong>Child:</strong> HK$13.80 / HK$20.00</li>
            <li><strong>Senior:</strong> HK$13.80 / HK$20.00</li>
            <li>Octopus Card accepted</li>
            <li>Journey: ~25-30 minutes</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#999;padding:20px;">
    <p>🚢 <strong>Lamma Ferry Tracker</strong> • Real schedule from HKKF</p>
    <p style="font-size:0.8rem;">Made with ❤️ for Lamma Islanders • Not affiliated with HKKF</p>
</div>
""", unsafe_allow_html=True)
