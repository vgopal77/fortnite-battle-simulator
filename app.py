import random
import requests
import streamlit as st
from gamedata import SKINS, WEAPONS

st.set_page_config(page_title="Fortnite Battle Simulator", page_icon="💥", layout="wide")

# ── Fetch real Fortnite skin images ───────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_skin_image(skin_name):
    try:
        r = requests.get(
            "https://fortnite-api.com/v2/cosmetics/br/search",
            params={"name": skin_name, "language": "en"},
            timeout=5,
        )
        if r.status_code == 200:
            imgs = r.json().get("data", {}).get("images", {})
            return imgs.get("featured") or imgs.get("icon")
    except Exception:
        pass
    return None

# Pre-warm cache at startup
for _sn in SKINS:
    get_skin_image(_sn)

# ── Styles ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Rajdhani:wght@600;700&display=swap');

/* ── Background: deep blue storm + yellow brush strokes ── */
.stApp {
    background:
        linear-gradient(122deg, transparent 18%, rgba(255,195,0,0.16) 30%,
            rgba(255,195,0,0.09) 44%, transparent 55%),
        linear-gradient(122deg, transparent 42%, rgba(255,185,0,0.07) 55%, transparent 65%),
        radial-gradient(ellipse 70% 55% at 50% 0%, rgba(100,30,220,0.35) 0%, transparent 60%),
        linear-gradient(160deg, #122d8c 0%, #091b60 35%, #050e35 70%, #020819 100%);
    background-attachment: fixed; min-height: 100vh;
}

/* Keep main content above the ghost overlay */
.block-container { position: relative; z-index: 2; padding-top: 1.2rem !important; }

/* Subtle scanlines */
.stApp::before {
    content: ''; position: fixed; inset: 0;
    background: repeating-linear-gradient(0deg, transparent 0px, transparent 3px,
        rgba(0,0,0,0.055) 3px, rgba(0,0,0,0.055) 4px);
    pointer-events: none; z-index: 9999;
}

/* ── Global text ── */
.stApp p, .stApp span, .stApp div, .stApp li { color: #d8eaff; }
label, .stSelectbox label {
    color: #6688bb !important; font-size: 11px !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── Headings ── */
h1 { font-family: 'Bangers', sans-serif !important; letter-spacing: 4px !important; color: #fff !important; }
h2, h3 { font-family: 'Rajdhani', sans-serif !important; color: #d8eaff !important; letter-spacing: 2px !important; }

/* ── Selectboxes ── */
.stSelectbox > div > div {
    background: rgba(5, 10, 40, 0.90) !important;
    border: 1px solid rgba(255, 200, 0, 0.28) !important;
    color: #d8eaff !important; border-radius: 6px !important;
}
.stSelectbox svg { fill: #FFD100 !important; }

/* ── Buttons ── */
.stButton > button {
    background: rgba(5, 10, 40, 0.82) !important; color: #FFD100 !important;
    border: 1.5px solid rgba(255, 209, 0, 0.50) !important; border-radius: 6px !important;
    font-family: 'Rajdhani', sans-serif !important; font-size: 15px !important;
    font-weight: 700 !important; letter-spacing: 2px !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 10px rgba(255,209,0,0.12) !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: rgba(255,209,0,0.08) !important;
    box-shadow: 0 0 24px rgba(255,209,0,0.42) !important;
    border-color: #FFD100 !important; transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FFD100 0%, #FF9500 100%) !important;
    color: #05090d !important; border: 2px solid #FFD100 !important;
    font-size: 16px !important; font-weight: 900 !important;
    box-shadow: 0 4px 22px rgba(255,175,0,0.50) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #ffe040 0%, #ffaa00 100%) !important;
    box-shadow: 0 6px 34px rgba(255,180,0,0.75) !important;
    transform: translateY(-2px) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(5,10,40,0.80) !important;
    border: 1px solid rgba(255,200,0,0.18) !important;
    border-radius: 7px !important; color: #6688bb !important;
    font-family: 'Rajdhani', sans-serif !important;
}
.streamlit-expanderContent {
    background: rgba(5,10,40,0.60) !important;
    border: 1px solid rgba(255,200,0,0.10) !important;
    border-radius: 0 0 7px 7px !important;
}

hr { border-color: rgba(255,200,0,0.15) !important; }

/* ── Ability pill ── */
.ability-pill {
    display: inline-block; border-radius: 4px;
    padding: 3px 14px; font-size: 11px; font-weight: 900;
    color: #05090d; margin: 7px 0 3px; letter-spacing: 1.5px; text-transform: uppercase;
}

/* ── HP bars ── */
.bar-wrap {
    background: rgba(0,0,0,0.45); border-radius: 3px; height: 20px;
    overflow: hidden; margin: 3px 0; border: 1px solid rgba(255,255,255,0.07);
}
.bar-fill {
    height: 100%; border-radius: 2px; display: flex; align-items: center;
    justify-content: center; font-size: 11px; font-weight: 900;
    color: #05090d; min-width: 28px; font-family: 'Rajdhani', sans-serif;
}

/* ── Battle log ── */
.log-row {
    border-left: 3px solid #334; border-radius: 4px; padding: 7px 13px; margin: 3px 0;
    font-size: 13px; font-family: 'Rajdhani', sans-serif; letter-spacing: 0.5px;
    background: rgba(5,10,40,0.70); backdrop-filter: blur(6px);
}

.stApp .stCaption p { color: #1e2d60 !important; }
</style>
""", unsafe_allow_html=True)

# ── Star field + ghost character background overlay ───────────────────────────

def inject_background(s1_name, s2_name):
    img1 = get_skin_image(s1_name) or ""
    img2 = get_skin_image(s2_name) or ""

    img1_tag = (f'<img src="{img1}" style="position:absolute;left:-40px;bottom:0;'
                'height:88vh;opacity:0.10;filter:blur(1px);object-fit:contain;'
                'pointer-events:none;"/>' ) if img1 else ""
    img2_tag = (f'<img src="{img2}" style="position:absolute;right:-40px;bottom:0;'
                'height:88vh;opacity:0.10;filter:blur(1px);object-fit:contain;'
                'pointer-events:none;transform:scaleX(-1);"/>') if img2 else ""

    st.markdown(f"""
<!-- Star field + ghost characters -->
<div style="position:fixed;inset:0;pointer-events:none;z-index:1;overflow:hidden;">

  <!-- SVG star field -->
  <svg width="100%" height="100%" style="position:absolute;inset:0;opacity:0.55;">
    <defs>
      <radialGradient id="sg" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="white" stop-opacity="1"/>
        <stop offset="100%" stop-color="white" stop-opacity="0"/>
      </radialGradient>
    </defs>
    {"".join(
      f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" opacity="{o}"/>'
      for x,y,r,o in [
        (45,120,1.2,0.7),(130,45,1,0.5),(220,180,1.5,0.6),(310,70,1,0.4),
        (420,150,1.2,0.7),(520,30,1,0.5),(610,200,1.8,0.5),(700,90,1,0.6),
        (800,160,1.2,0.4),(900,40,1,0.7),(1000,130,1.5,0.5),(1100,75,1,0.6),
        (1200,190,1.2,0.5),(1300,55,1,0.4),(1400,140,1.8,0.6),(1500,20,1,0.5),
        (80,280,1,0.4),(170,320,1.5,0.6),(260,260,1,0.5),(350,350,1.2,0.7),
        (450,290,1,0.4),(550,370,1.5,0.5),(640,310,1,0.6),(730,250,1.2,0.4),
        (830,380,1,0.5),(930,270,1.8,0.6),(1020,340,1,0.4),(1120,290,1.2,0.5),
        (1220,360,1,0.6),(1320,280,1.5,0.4),(1420,330,1,0.7),(1520,260,1.2,0.5),
        (30,450,1.5,0.5),(120,500,1,0.6),(210,430,1.2,0.4),(300,480,1,0.7),
        (400,420,1.8,0.5),(500,470,1,0.4),(590,510,1.2,0.6),(680,440,1,0.5),
        (780,490,1.5,0.4),(880,425,1,0.7),(970,505,1.2,0.5),(1070,455,1,0.6),
        (1170,520,1.5,0.4),(1270,465,1,0.5),(1370,510,1.2,0.7),(1470,440,1,0.4),
        (60,600,1,0.6),(150,650,1.2,0.4),(240,580,1.5,0.5),(330,640,1,0.7),
        (430,610,1,0.4),(530,660,1.8,0.6),(620,595,1,0.5),(720,645,1.2,0.4),
        (820,615,1,0.6),(920,670,1.5,0.5),(1010,600,1,0.4),(1110,655,1.2,0.6),
        (1210,620,1,0.5),(1310,665,1.8,0.4),(1410,610,1,0.7),(1510,660,1.2,0.5),
      ]
    )}
  </svg>

  <!-- Yellow diagonal brush stroke accent (top-right) -->
  <div style="position:absolute;top:-80px;right:100px;width:600px;height:400px;
    background:linear-gradient(128deg,transparent 30%,rgba(255,200,0,0.07) 45%,
      rgba(255,200,0,0.04) 60%,transparent 75%);
    transform:rotate(-5deg);pointer-events:none;"></div>

  <!-- Ghost character images -->
  {img1_tag}
  {img2_tag}

  <!-- Vignette -->
  <div style="position:absolute;inset:0;
    background:radial-gradient(ellipse 85% 85% at 50% 50%,
      transparent 50%, rgba(2,8,25,0.65) 100%);
    pointer-events:none;"></div>
</div>
""", unsafe_allow_html=True)


skin_names   = list(SKINS.keys())
weapon_names = list(WEAPONS.keys())


def hp_bar_color(pct):
    if pct > 0.60: return "#00e676"
    if pct > 0.30: return "#ff9100"
    return "#ff1744"


def render_bar(emoji, label, value, max_val, is_hp=True):
    pct = value / max_val if max_val > 0 else 0
    color = hp_bar_color(pct) if is_hp else "#40c4ff"
    width = max(int(pct * 100), 2)
    st.markdown(f"""
<div style="margin:5px 0;">
  <span style="font-size:12px;font-weight:700;color:#5577aa;letter-spacing:1.5px;
    font-family:'Rajdhani',sans-serif;text-transform:uppercase;">
    {emoji} {label}: {value} / {max_val}
  </span>
  <div class="bar-wrap">
    <div class="bar-fill" style="width:{width}%;background:{color};
      box-shadow:0 0 8px {color}99;">{value}</div>
  </div>
</div>""", unsafe_allow_html=True)


def render_player_card(skin_name, weapon_name, health=None, shields=None):
    s   = SKINS[skin_name]
    w   = WEAPONS[weapon_name]
    c   = s["color"]
    r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
    img_url = get_skin_image(skin_name) or ""

    bg_img = (f'<img src="{img_url}" style="position:absolute;right:-10px;bottom:0;'
              f'height:100%;max-height:240px;opacity:0.22;object-fit:contain;'
              f'pointer-events:none;filter:drop-shadow(0 0 12px rgba({r},{g},{b},0.8));"/>'
              ) if img_url else ""

    avatar_section = (
        f'<img src="{img_url}" style="width:110px;height:110px;object-fit:contain;'
        f'filter:drop-shadow(0 0 20px rgba({r},{g},{b},1));margin-bottom:6px;"/>'
        if img_url else
        f'<div style="font-size:84px;line-height:1.1;margin-bottom:6px;'
        f'filter:drop-shadow(0 0 22px rgba({r},{g},{b},0.95));">{s["avatar"]}</div>'
    )

    st.markdown(f"""
<div style="position:relative;overflow:hidden;border-radius:10px;margin-bottom:10px;
  background:linear-gradient(155deg,rgba({r},{g},{b},0.16) 0%,rgba(4,8,28,0.96) 60%);
  border:1.5px solid rgba({r},{g},{b},0.65);
  box-shadow:0 0 32px rgba({r},{g},{b},0.22),0 0 0 1px rgba(255,255,255,0.04) inset;
  padding:22px 16px 18px;text-align:center;min-height:260px;">

  <!-- Top glow bar -->
  <div style="position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,transparent,#FFD100 40%,rgba({r},{g},{b},1) 75%,transparent);"></div>

  <!-- HUD corner brackets -->
  <div style="position:absolute;top:8px;left:8px;width:16px;height:16px;
    border-top:2px solid #FFD100;border-left:2px solid #FFD100;border-radius:2px 0 0 0;opacity:0.9;"></div>
  <div style="position:absolute;top:8px;right:8px;width:16px;height:16px;
    border-top:2px solid #FFD100;border-right:2px solid #FFD100;border-radius:0 2px 0 0;opacity:0.9;"></div>
  <div style="position:absolute;bottom:8px;left:8px;width:16px;height:16px;
    border-bottom:2px solid #FFD100;border-left:2px solid #FFD100;border-radius:0 0 0 2px;opacity:0.9;"></div>
  <div style="position:absolute;bottom:8px;right:8px;width:16px;height:16px;
    border-bottom:2px solid #FFD100;border-right:2px solid #FFD100;border-radius:0 0 2px 0;opacity:0.9;"></div>

  <!-- Skin art ghost inside card -->
  {bg_img}

  <!-- Main avatar / skin image -->
  <div style="position:relative;z-index:1;">{avatar_section}</div>

  <!-- Skin name -->
  <div style="position:relative;z-index:1;font-family:'Bangers',sans-serif;font-size:24px;
    letter-spacing:5px;color:#fff;
    text-shadow:-2px -2px 0 #000,2px -2px 0 #000,-2px 2px 0 #000,2px 2px 0 #000,
    0 0 18px {c};margin-bottom:4px;">{skin_name.upper()}</div>

  <!-- Weapon -->
  <div style="position:relative;z-index:1;font-size:13px;color:rgba(170,200,255,0.60);
    margin-bottom:10px;font-family:'Rajdhani',sans-serif;letter-spacing:1.5px;">
    {w['emoji']} &nbsp; {weapon_name.upper()}
  </div>

  <!-- Ability -->
  <div class="ability-pill" style="background:#FFD100;position:relative;z-index:1;">
    ⚡ {s['ability'].upper()}
  </div>
  <div style="position:relative;z-index:1;font-size:11px;color:rgba(170,200,255,0.42);
    margin-top:4px;font-family:'Rajdhani',sans-serif;">{s['ability_desc']}</div>
</div>""", unsafe_allow_html=True)

    if health is not None:
        render_bar("❤️", "HP",      health,  SKINS[skin_name]["health"],  is_hp=True)
        render_bar("🛡️", "Shields", shields, SKINS[skin_name]["shields"], is_hp=False)


# ── State ─────────────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "p1_health":None,"p1_shields":None,"p2_health":None,"p2_shields":None,
        "p1_locked":None,"p2_locked":None,"p1_wpn_locked":None,"p2_wpn_locked":None,
        "battle_log":[],"game_over":False,"winner":None,
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
    log = st.session_state.battle_log
    if log and not isinstance(log[0], tuple): st.session_state.battle_log = []

def start_match(s1, s2, w1, w2):
    st.session_state.p1_health    = SKINS[s1]["health"]
    st.session_state.p1_shields   = SKINS[s1]["shields"]
    st.session_state.p2_health    = SKINS[s2]["health"]
    st.session_state.p2_shields   = SKINS[s2]["shields"]
    st.session_state.p1_locked    = s1; st.session_state.p2_locked    = s2
    st.session_state.p1_wpn_locked = w1; st.session_state.p2_wpn_locked = w2
    st.session_state.battle_log   = []
    st.session_state.game_over    = False; st.session_state.winner = None

def reset_match():
    for k in ["p1_health","p1_shields","p2_health","p2_shields",
              "p1_locked","p2_locked","p1_wpn_locked","p2_wpn_locked","game_over","winner"]:
        st.session_state[k] = None
    st.session_state.battle_log = []

def apply_damage(hp, sh, dmg):
    if sh > 0:
        a = min(sh, dmg); sh -= a; dmg -= a
    return max(0, hp - dmg), sh

def do_attack(atk_skin, def_skin, weapon_name, def_hp_key, def_sh_key, atk_hp_key, atk_sh_key):
    w   = WEAPONS[weapon_name]
    atk = SKINS[atk_skin]
    dfd = SKINS[def_skin]
    log = []
    accuracy = min(0.98, w["accuracy"] + (atk.get("accuracy_bonus",0) if atk_skin=="Renegade Raider" else 0))
    if random.random() >= accuracy:
        log.append(("miss", f"💨 <b>{atk_skin}</b> fired {w['emoji']} {weapon_name} — <b>MISSED!</b>"))
        st.session_state.battle_log = log + st.session_state.battle_log; return
    if def_skin == "Jonesy" and random.random() < dfd.get("dodge_chance", 0):
        log.append(("ability", f"🍀 <b>{def_skin}</b> — <b>LUCKY BREAK!</b> Dodged the attack!"))
        st.session_state.battle_log = log + st.session_state.battle_log; return
    damage = w["damage"]; label = "Hit"; entry_type = "hit"
    if atk_skin == "Midas" and random.random() < atk.get("gold_chance", 0):
        damage = w["damage"] * 3; label = "👑 GOLDEN TOUCH — TRIPLE DMG"; entry_type = "crit"
    elif random.random() < w["crit_chance"]:
        damage = w["damage"] * 2; label = "💥 CRITICAL HIT"; entry_type = "crit"
    prev_hp = st.session_state[def_hp_key]; prev_sh = st.session_state[def_sh_key]
    new_hp, new_sh = apply_damage(prev_hp, prev_sh, damage)
    st.session_state[def_hp_key] = new_hp; st.session_state[def_sh_key] = new_sh
    sh_note = f" | 🛡️ {prev_sh}→{new_sh}" if prev_sh != new_sh else ""
    icon = "💥" if entry_type == "crit" else "🎯"
    log.append((entry_type,
        f"{icon} <b>{atk_skin}</b> → <b>{def_skin}</b> with {w['emoji']} {weapon_name}: "
        f"<b>{label}</b> for <b>{damage} dmg</b> | ❤️ {prev_hp}→{new_hp}{sh_note}"))
    if atk_skin == "Cuddle Team Leader":
        heal = atk.get("heal_amount", 0)
        old_hp = st.session_state[atk_hp_key]
        new_atk_hp = min(SKINS[atk_skin]["health"], old_hp + heal)
        st.session_state[atk_hp_key] = new_atk_hp
        if new_atk_hp > old_hp:
            log.append(("ability", f"🐻 <b>{atk_skin}</b> — <b>BEAR HUG</b> healed +{heal} HP! ({old_hp}→{new_atk_hp})"))
    if new_hp <= 0:
        st.session_state.game_over = True; st.session_state.winner = atk_skin
        log.append(("win", f"🏆 <b>{atk_skin}</b> has <b>ELIMINATED</b> <b>{def_skin}</b>!"))
    st.session_state.battle_log = log + st.session_state.battle_log


# ── Layout ────────────────────────────────────────────────────────────────────

init_state()
game_active = st.session_state.p1_health is not None

# Determine which skins to ghost in background
_s1 = st.session_state.p1_locked or skin_names[0]
_s2 = st.session_state.p2_locked or skin_names[1]
inject_background(_s1, _s2)

# ── Title ──
st.markdown("""
<div style="text-align:center;padding:14px 0 6px;position:relative;z-index:2;">
  <div style="font-family:'Bangers',sans-serif;font-size:52px;letter-spacing:7px;color:#fff;
    text-shadow:-3px -3px 0 #000,3px -3px 0 #000,-3px 3px 0 #000,3px 3px 0 #000,
    0 0 26px rgba(255,209,0,0.9),0 0 70px rgba(100,30,220,0.45);line-height:1.05;">
    💥 FORTNITE BATTLE SIMULATOR
  </div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:13px;color:#FFD100;
    letter-spacing:6px;margin-top:4px;text-transform:uppercase;opacity:0.75;">
    ⚡ &nbsp; Ayaan &nbsp; vs &nbsp; Omer &nbsp; ⚡ &nbsp;·&nbsp; May the best player win
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📖  HOW TO PLAY"):
    st.markdown("""
**Goal:** Reduce your opponent's HP to 0 to win.

**Steps:**
1. Pick your **Skin** — each has a unique special ability.
2. Pick your **Weapon** — different damage, accuracy, and crit chance.
3. Hit **START MATCH** to lock in selections.
4. Take turns pressing your **ATTACK** button and watch the battle log!
5. First player to reach 0 HP loses. 🏆

**Skin Abilities:**
- 🧑 **Jonesy — Lucky Break:** 10% chance to dodge any attack
- 👑 **Midas — Golden Touch:** 20% chance to deal triple damage
- 🐻 **Cuddle Team Leader — Bear Hug:** Heals +8 HP after every attack you land
- ✈️ **Renegade Raider — Aerial Precision:** +20% accuracy on all weapons

**Weapons:**
| Weapon | Damage | Accuracy | Crit |
|---|---|---|---|
| 🔫 Scar | 35 | 85% | 15% |
| 🪖 Pump Shotgun | 70 | 55% | 25% |
| 🚀 Rocket Launcher | 90 | 65% | 10% |
| ⚡ Tactical SMG | 20 | 75% | 20% |
""")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""<div style="font-family:'Bangers',sans-serif;font-size:22px;letter-spacing:4px;
      color:#4da6ff;text-shadow:-1px -1px 0 #000,1px 1px 0 #000,0 0 14px #4da6ff88;
      margin-bottom:6px;">🟦 AYAAN</div>""", unsafe_allow_html=True)
    p1_skin   = st.selectbox("Choose Skin",   skin_names,   key="p1_skin",   disabled=game_active)
    p1_weapon = st.selectbox("Choose Weapon", weapon_names, key="p1_weapon", disabled=game_active)
    locked_s1 = st.session_state.p1_locked    or p1_skin
    locked_w1 = st.session_state.p1_wpn_locked or p1_weapon
    render_player_card(locked_s1, locked_w1,
        st.session_state.p1_health  if game_active else None,
        st.session_state.p1_shields if game_active else None)

with col2:
    st.markdown("""<div style="font-family:'Bangers',sans-serif;font-size:22px;letter-spacing:4px;
      color:#ff5252;text-shadow:-1px -1px 0 #000,1px 1px 0 #000,0 0 14px #ff525288;
      margin-bottom:6px;">🟥 OMER</div>""", unsafe_allow_html=True)
    p2_skin   = st.selectbox("Choose Skin",   skin_names,   index=1, key="p2_skin",   disabled=game_active)
    p2_weapon = st.selectbox("Choose Weapon", weapon_names, index=1, key="p2_weapon", disabled=game_active)
    locked_s2 = st.session_state.p2_locked    or p2_skin
    locked_w2 = st.session_state.p2_wpn_locked or p2_weapon
    render_player_card(locked_s2, locked_w2,
        st.session_state.p2_health  if game_active else None,
        st.session_state.p2_shields if game_active else None)

st.markdown("---")

if not game_active:
    if st.button("🎮  START MATCH", use_container_width=True, type="primary"):
        start_match(p1_skin, p2_skin, p1_weapon, p2_weapon); st.rerun()
else:
    if st.session_state.game_over:
        st.balloons()
        winner = st.session_state.winner
        wc = SKINS[winner]["color"]
        st.markdown(f"""
<div style="text-align:center;padding:14px 0;">
  <div style="font-family:'Bangers',sans-serif;font-size:42px;letter-spacing:6px;color:#FFD100;
    text-shadow:-3px -3px 0 #000,3px -3px 0 #000,-3px 3px 0 #000,3px 3px 0 #000,
    0 0 30px #FFD100,0 0 65px {wc};">
    🏆 &nbsp; {winner.upper()} &nbsp; WINS! &nbsp; 🏆
  </div>
</div>""", unsafe_allow_html=True)
        if st.button("🔄  PLAY AGAIN", use_container_width=True, type="primary"):
            reset_match(); st.rerun()
    else:
        a1, a2 = st.columns(2)
        with a1:
            if st.button("💥  AYAAN ATTACKS!", use_container_width=True, type="primary"):
                do_attack(st.session_state.p1_locked, st.session_state.p2_locked,
                          st.session_state.p1_wpn_locked,
                          "p2_health","p2_shields","p1_health","p1_shields"); st.rerun()
        with a2:
            if st.button("💥  OMER ATTACKS!", use_container_width=True, type="primary"):
                do_attack(st.session_state.p2_locked, st.session_state.p1_locked,
                          st.session_state.p2_wpn_locked,
                          "p1_health","p1_shields","p2_health","p2_shields"); st.rerun()

# ── Battle Log ────────────────────────────────────────────────────────────────

LOG_COLORS = {"hit":"#00e676","crit":"#FFD100","miss":"#334466","ability":"#ff4da6","win":"#FF5722"}

st.markdown("---")
st.markdown("""<div style="font-family:'Bangers',sans-serif;font-size:18px;color:#FFD100;
  letter-spacing:4px;margin-bottom:8px;
  text-shadow:-1px -1px 0 #000,1px 1px 0 #000;">📜 &nbsp; BATTLE LOG</div>""",
  unsafe_allow_html=True)

if st.session_state.battle_log:
    for entry_type, text in st.session_state.battle_log:
        border = LOG_COLORS.get(entry_type, "#334466")
        st.markdown(f'<div class="log-row" style="border-left-color:{border};">{text}</div>',
            unsafe_allow_html=True)
else:
    st.caption("No actions yet — start a match and attack!")
