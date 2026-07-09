import streamlit as st
from datetime import datetime, timedelta
import pytz

# ═══════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════
st.set_page_config(
    page_title="Lamma Ferry",
    page_icon="🚢",
    layout="wide"
)

# ═══════════════════════════════════════
# FERRY SCHEDULE (HKKF)
# ═══════════════════════════════════════
CENTRAL_TO_LAMMA_WEEKDAY = [
    "06:30", "07:00", "07:30", "07:50", "08:10", "08:30", "08:50",
    "09:10", "09:30", "10:10", "11:00", "12:00", "13:00", "13:45",
    "14:30", "15:15", "15:50", "16:30", "17:20", "17:40", "18:00",
    "18:20", "18:40", "19:00", "19:30", "20:00", "20:30", "21:00",
    "21:30", "22:30", "23:30"
]

CENTRAL_TO_LAMMA_SAT_EARLY = ["02:30"]

LAMMA_TO_CENTRAL_WEEKDAY = [
    "05:30", "06:20", "06:40", "07:00", "07:20", "07:40", "08:00",
    "08:20", "08:40", "09:00", "09:20", "09:40", "10:30", "11:20",
    "12:00", "13:00", "13:45", "14:30", "15:15", "16:00", "16:30",
    "17:15", "17:50", "18:10", "18:30", "18:50", "19:20", "20:00",
    "20:30", "21:30", "22:30", "23:30"
]

CENTRAL_TO_LAMMA_SUNDAY = [
    "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00",
    "14:30", "15:00", "16:00", "16:30", "17:00", "17:30", "18:00",
    "18:30", "19:00", "19:30", "20:00", "20:30", "21:30", "22:30",
    "23:30"
]

CENTRAL_TO_LAMMA_SUN_EARLY = ["02:30"]

LAMMA_TO_CENTRAL_SUNDAY = [
    "05:30", "06:40", "07:30", "08:00", "08:30", "09:00", "09:30",
    "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00",
    "13:30", "14:00", "14:30", "15:30", "16:00", "16:30", "17:00",
    "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
    "21:30", "22:30", "23:30"
]

# ═══════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════
def get_hk_time():
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    return datetime.now(hk_tz)

def get_day_type(dt):
    weekday = dt.weekday()
    if weekday == 6:
        return "sunday"
    elif weekday == 5:
        return "saturday"
    else:
        return "weekday"

def get_schedule(route, dt):
    day_type = get_day_type(dt)
    
    if route == "Central → Lamma":
        if day_type == "sunday":
            sched = CENTRAL_TO_LAMMA_SUN_EARLY + CENTRAL_TO_LAMMA_SUNDAY
        elif day_type == "saturday":
            sched = CENTRAL_TO_LAMMA_SAT_EARLY + CENTRAL_TO_LAMMA_WEEKDAY
        else:
            sched = CENTRAL_TO_LAMMA_WEEKDAY
    else:
        if day_type == "sunday":
            sched = LAMMA_TO_CENTRAL_SUNDAY
        elif day_type == "saturday":
            sched = LAMMA_TO_CENTRAL_WEEKDAY
        else:
            sched = LAMMA_TO_CENTRAL_WEEKDAY
    
    sched.sort()
    return sched

def parse_time(time_str, dt):
    hour, minute = map(int, time_str.split(':'))
    ferry_dt = dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if ferry_dt < dt - timedelta(hours=6):
        ferry_dt += timedelta(days=1)
    return ferry_dt

def get_all_ferries(route, dt, commute_minutes):
    """Get previous (missed) + upcoming ferries"""
    schedule = get_schedule(route, dt)
    tomorrow = dt + timedelta(days=1)
    tomorrow_schedule = get_schedule(route, tomorrow)
    
    all_ferries = []
    
    # Today's ferries (both past and future)
    for time_str in schedule:
        ferry_time = parse_time(time_str, dt)
        leave_by = ferry_time - timedelta(minutes=commute_minutes)
        minutes_until = int((ferry_time - dt).total_seconds() / 60)
        
        if minutes_until < -120:  # Skip ferries more than 2 hours ago
            continue
            
        status = get_status(minutes_until, commute_minutes, leave_by, dt)
        
        all_ferries.append({
            'ferry_time': ferry_time,
            'display_time': time_str,
            'leave_by': leave_by,
            'minutes_until': minutes_until,
            'status': status,
            'is_past': minutes_until < 0
        })
    
    # Tomorrow's early ferries if needed
    if len([f for f in all_ferries if not f['is_past']]) < 5:
        for time_str in tomorrow_schedule[:3]:
            ferry_time = parse_time(time_str, tomorrow)
            leave_by = ferry_time - timedelta(minutes=commute_minutes)
            minutes_until = int((ferry_time - dt).total_seconds() / 60)
            status = get_status(minutes_until, commute_minutes, leave_by, dt)
            
            all_ferries.append({
                'ferry_time': ferry_time,
                'display_time': f"{time_str} (+1)",
                'leave_by': leave_by,
                'minutes_until': minutes_until,
                'status': status,
                'is_past': False
            })
    
    all_ferries.sort(key=lambda x: x['ferry_time'])
    return all_ferries

def get_status(minutes_until, commute_minutes, leave_by, dt):
    if minutes_until < 0:
        return "missed"
    elif leave_by <= dt:
        if minutes_until <= commute_minutes:
            return "hurry"
        else:
            return "late"
    elif minutes_until <= commute_minutes + 5:
        return "leave_now"
    elif minutes_until <= commute_minutes + 15:
        return "soon"
    else:
        return "ok"

# ═══════════════════════════════════════
# CSS - Clean, Lamma beach vibe
# ═══════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
    
    * { font-family: 'Nunito', sans-serif; }
    
    .stApp { 
        background: #f5f7f5; 
    }
    
    /* Header */
    .app-header {
        background: linear-gradient(135deg, #0e6655, #148f77);
        padding: 20px 25px;
        border-radius: 0 0 25px 25px;
        margin-bottom: 15px;
    }
    .app-title { font-size: 2rem; font-weight: 900; color: #fff; margin: 0; }
    .app-subtitle { font-size: 0.9rem; color: #a3e4d7; margin: 2px 0 0 0; }
    
    /* Status Panel - THE QUICK GLANCE */
    .status-panel {
        background: #fff;
        border-radius: 20px;
        padding: 20px 25px;
        margin-bottom: 15px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        text-align: center;
    }
    
    .status-panel .next-ferry-time {
        font-size: 3rem;
        font-weight: 900;
        color: #0e6655;
        line-height: 1;
    }
    
    .status-panel .leave-label {
        font-size: 0.85rem;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    
    .status-panel .leave-time {
        font-size: 1.8rem;
        font-weight: 800;
        color: #e74c3c;
    }
    
    .status-panel .leave-time.ok {
        color: #27ae60;
    }
    
    .status-panel .status-msg {
        font-size: 0.95rem;
        color: #666;
        margin-top: 5px;
    }
    
    .status-panel.missed {
        border: 3px solid #e74c3c;
        background: #fff5f5;
    }
    
    .status-panel.hurry {
        border: 3px solid #e74c3c;
        animation: urgentPulse 1.5s infinite;
    }
    
    .status-panel.soon {
        border: 3px solid #f39c12;
    }
    
    .status-panel.ok {
        border: 3px solid #27ae60;
    }
    
    @keyframes urgentPulse {
        0%, 100% { border-color: #e74c3c; }
        50% { border-color: #ff9999; }
    }
    
    /* Current time */
    .time-badge {
        background: #fff;
        border-radius: 12px;
        padding: 10px 18px;
        text-align: center;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
        margin-bottom: 15px;
    }
    .time-badge .now { font-size: 1.3rem; font-weight: 800; color: #0e6655; }
    .time-badge .day { font-size: 0.8rem; color: #999; }
    
    /* Ferry list */
    .ferry-row {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        margin: 4px 0;
        border-radius: 12px;
        background: #fff;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        font-size: 0.95rem;
    }
    
    .ferry-row.missed {
        opacity: 0.4;
        text-decoration: line-through;
    }
    
    .ferry-row.next-ferry {
        background: #eafaf1;
        border: 2px solid #27ae60;
        font-weight: 700;
    }
    
    .ferry-row .ferry-icon { width: 35px; font-size: 1.2rem; }
    .ferry-row .ferry-time { width: 80px; font-weight: 700; color: #333; }
    .ferry-row .leave-col { width: 140px; color: #e74c3c; font-weight: 600; font-size: 0.85rem; }
    .ferry-row .leave-col.ok { color: #27ae60; }
    .ferry-row .countdown-col { width: 80px; color: #999; font-size: 0.8rem; text-align: right; }
    .ferry-row .status-col { width: 90px; text-align: right; }
    
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge.next { background: #27ae60; color: #fff; }
    .badge.missed { background: #e0e0e0; color: #999; }
    .badge.hurry { background: #e74c3c; color: #fff; }
    .badge.soon { background: #f39c12; color: #fff; }
    .badge.ok { background: #e8e8e8; color: #888; }
    
    /* Selector */
    .selector-box {
        background: #fff;
        border-radius: 16px;
        padding: 15px 20px;
        margin-bottom: 15px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }
    
    /* Divider */
    .section-label {
        font-size: 0.8rem;
        color: #aaa;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 10px 15px 5px 15px;
    }
    
    /* Override Streamlit */
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stButton > button[kind="primary"] { background: #0e6655; }
    .stButton > button[kind="secondary"] { background: #e8e8e8; color: #333; }
    
    /* Radio buttons */
    .stRadio > div { gap: 5px; }
    .stRadio label { color: #555; font-weight: 600; }
    
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# GET CURRENT TIME
# ═══════════════════════════════════════
hk_time = get_hk_time()
day_type = get_day_type(hk_time)

day_labels = {
    "weekday": "Mon - Fri",
    "saturday": "Sat",
    "sunday": "Sun / PH"
}
schedule_label = day_labels.get(day_type, "")

# ═══════════════════════════════════════
# HEADER
# ═══════════════════════════════════════
st.markdown("""
<div class="app-header">
    <h1 class="app-title">🚢 Lamma Ferry</h1>
    <p class="app-subtitle">Central ↔ Yung Shue Wan</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# ROUTE & COMMUTE SELECTOR
# ═══════════════════════════════════════
st.markdown('<div class="selector-box">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    route = st.radio(
        "Route",
        ["Central → Lamma", "Lamma → Central"],
        horizontal=True
    )

with col2:
    if route == "Central → Lamma":
        commute_options = {
            "🏢 Office (45 min)": 45,
            "🚇 MTR (35 min)": 35,
            "🏠 Home (30 min)": 30,
            "📍 At pier (0 min)": 0,
        }
    else:
        commute_options = {
            "🏠 Home (15 min)": 15,
            "🏖️ Beach (25 min)": 25,
            "🍽️ Restaurant (10 min)": 10,
            "📍 At pier (0 min)": 0,
        }
    
    commute_label = st.selectbox("Commute", list(commute_options.keys()), label_visibility="collapsed")
    commute_minutes = commute_options[commute_label]

st.markdown('</div>', unsafe_allow_html=True)

# Time badge
st.markdown(f"""
<div class="time-badge">
    <span class="now">🕐 {hk_time.strftime('%I:%M %p')}</span>
    <span class="day"> • {hk_time.strftime('%A')} • {schedule_label}</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# GET ALL FERRIES
# ═══════════════════════════════════════
all_ferries = get_all_ferries(route, hk_time, commute_minutes)

# Separate past and future
past_ferries = [f for f in all_ferries if f['is_past']]
future_ferries = [f for f in all_ferries if not f['is_past']]

# Find next catchable ferry
next_ferry = None
for f in future_ferries:
    if f['status'] in ['ok', 'soon', 'leave_now']:
        next_ferry = f
        break

# If all remaining are late/hurry, pick the first future one
if not next_ferry and future_ferries:
    next_ferry = future_ferries[0]

# ═══════════════════════════════════════
# STATUS PANEL - Quick Glance
# ═══════════════════════════════════════
if next_ferry:
    panel_status = next_ferry['status']
    leave_class = "ok" if panel_status in ['ok', 'soon'] else ""
    
    if next_ferry['minutes_until'] <= 0:
        status_msg = "⚠️ Already departed!"
        panel_class = "missed"
    elif panel_status == "hurry":
        status_msg = "🏃 RUN! You might make it!"
        panel_class = "hurry"
    elif panel_status == "leave_now":
        status_msg = "🚶 Leave right now!"
        panel_class = "hurry"
    elif panel_status == "late":
        status_msg = "😞 Probably too late..."
        panel_class = "missed"
    elif panel_status == "soon":
        status_msg = "⏰ Get ready to leave"
        panel_class = "soon"
    else:
        mins_until_leave = int((next_ferry['leave_by'] - hk_time).total_seconds() / 60)
        status_msg = f"☕ Relax, leave in {mins_until_leave} min"
        panel_class = "ok"
    
    leave_display = next_ferry['leave_by'].strftime('%I:%M %p') if next_ferry['leave_by'] > hk_time else "NOW!"
    
    st.markdown(f"""
    <div class="status-panel {panel_class}">
        <div class="leave-label">NEXT FERRY</div>
        <div class="next-ferry-time">🚢 {next_ferry['display_time']}</div>
        <div style="margin-top:8px;">
            <span style="color:#999;">Leave by</span>
            <span class="leave-time {leave_class}"> {leave_display}</span>
        </div>
        <div class="status-msg">{status_msg}</div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════
# UPCOMING FERRIES
# ═══════════════════════════════════════
st.markdown('<div class="section-label">📋 Upcoming Ferries</div>', unsafe_allow_html=True)

for ferry in future_ferries[:8]:
    is_next = (ferry == next_ferry)
    
    if ferry['minutes_until'] < 0:
        countdown = "Departed"
    elif ferry['minutes_until'] < 60:
        countdown = f"{ferry['minutes_until']} min"
    else:
        h = ferry['minutes_until'] // 60
        m = ferry['minutes_until'] % 60
        countdown = f"{h}h {m}m"
    
    if ferry['leave_by'] <= hk_time:
        leave_text = "NOW"
        leave_ok = ""
    else:
        leave_text = ferry['leave_by'].strftime('%I:%M %p')
        leave_ok = "ok" if ferry['status'] == 'ok' else ""
    
    # Badge
    if is_next:
        badge_class = "next"
        badge_text = "NEXT"
    elif ferry['status'] in ['hurry', 'leave_now']:
        badge_class = "hurry"
        badge_text = "HURRY"
    elif ferry['status'] == 'soon':
        badge_class = "soon"
        badge_text = "SOON"
    else:
        badge_class = "ok"
        badge_text = ferry['status'].replace('_', ' ').upper()
    
    row_class = "next-ferry" if is_next else ""
    
    st.markdown(f"""
    <div class="ferry-row {row_class}">
        <span class="ferry-icon">🚢</span>
        <span class="ferry-time">{ferry['display_time']}</span>
        <span class="leave-col {leave_ok}">🏃 {leave_text}</span>
        <span class="countdown-col">⏱ {countdown}</span>
        <span class="status-col"><span class="badge {badge_class}">{badge_text}</span></span>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════
# PREVIOUS (MISSED) FERRIES
# ═══════════════════════════════════════
if past_ferries:
    with st.expander(f"📭 Missed Ferries ({len(past_ferries)})", expanded=False):
        for ferry in past_ferries[-4:]:  # Show last 4 missed
            st.markdown(f"""
            <div class="ferry-row missed">
                <span class="ferry-icon">🚢</span>
                <span class="ferry-time">{ferry['display_time']}</span>
                <span class="leave-col">Left {abs(ferry['minutes_until'])} min ago</span>
                <span class="countdown-col"></span>
                <span class="status-col"><span class="badge missed">MISSED</span></span>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#bbb;font-size:0.75rem;padding:10px;">
    🚢 Schedule from HKKF • Made for Lamma Islanders
</div>
""", unsafe_allow_html=True)
