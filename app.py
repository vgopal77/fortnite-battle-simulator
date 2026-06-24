import random
import streamlit as st
from gamedata import SKINS, WEAPONS

st.set_page_config(page_title="Fortnite Battle Simulator", page_icon="💥", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Rajdhani:wght@600;700&display=swap');

/* ── Fortnite Blue + Yellow Background ── */
.stApp {
    background:
        linear-gradient(128deg, transparent 22%, rgba(255,195,0,0.13) 34%, rgba(255,195,0,0.07) 46%, transparent 56%),
        linear-gradient(128deg, transparent 44%, rgba(255,195,0,0.06) 56%, transparent 64%),
        linear-gradient(158deg, #163b9e 0%, #0b2168 35%, #06143a 70%, #020a1c 100%);
    background-attachment: fixed;
    min-height: 100vh;
}

/* Subtle scanlines */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background: repeating-linear-gradient(0deg, transparent 0px, transparent 3px,
        rgba(0,0,0,0.06) 3px, rgba(0,0,0,0.06) 4px);
    pointer-events: none; z-index: 9999;
}

/* ── Block container ── */
.block-container { padding-top: 1.2rem !important; }

/* ── Global text ── */
.stApp, .stApp p, .stApp span, .stApp div, .stApp li { color: #ddeeff; }
label, .stSelectbox label {
    color: #7799cc !important; font-size: 11px !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── Headings ── */
h1 { font-family: 'Bangers', sans-serif !important; letter-spacing: 4px !important; color: #fff !important; }
h2, h3 {
    font-family: 'Rajdhani', sans-serif !important;
    color: #ddeeff !important; letter-spacing: 2px !important;
}

/* ── Selectboxes ── */
.stSelectbox > div > div {
    background: rgba(6, 14, 50, 0.88) !important;
    border: 1px solid rgba(255, 200, 0, 0.25) !important;
    color: #ddeeff !important; border-radius: 6px !important;
}
.stSelectbox svg { fill: #FFD100 !important; }

/* ── All buttons base ── */
.stButton > button {
    background: rgba(6, 14, 50, 0.80) !important;
    color: #FFD100 !important;
    border: 1.5px solid rgba(255, 209, 0, 0.55) !important;
    border-radius: 6px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important; font-weight: 700 !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    box-shadow: 0 0 12px rgba(255,209,0,0.15) !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: rgba(255,209,0,0.10) !important;
    box-shadow: 0 0 26px rgba(255,209,0,0.45) !important;
    border-color: #FFD100 !important; transform: translateY(-1px) !important;
}
/* Primary: solid yellow — Fortnite CTA style */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FFD100 0%, #FF9500 100%) !important;
    color: #05090d !important;
    border: 2px solid #FFD100 !important;
    font-size: 16px !important; font-weight: 900 !important;
    box-shadow: 0 4px 22px rgba(255,180,0,0.50), 0 1px 0 rgba(255,255,255,0.15) inset !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #ffe040 0%, #ffaa00 100%) !important;
    box-shadow: 0 6px 32px rgba(255,180,0,0.75) !important;
    transform: translateY(-2px) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(6, 14, 50, 0.75) !important;
    border: 1px solid rgba(255, 200, 0, 0.18) !important;
    border-radius: 7px !important; color: #7799cc !important;
    font-family: 'Rajdhani', sans-serif !important;
}
.streamlit-expanderContent {
    background: rgba(6, 14, 50, 0.55) !important;
    border: 1px solid rgba(255,200,0,0.10) !important;
    border-radius: 0 0 7px 7px !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,200,0,0.15) !important; }

/* ── Ability pill ── */
.ability-pill {
    display: inline-block; border-radius: 4px;
    padding: 3px 14px; font-size: 11px; font-weight: 700;
    color: #05090d; margin: 7px 0 3px; letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* ── HP bars ── */
.bar-wrap {
    background: rgba(0,0,0,0.40); border-radius: 3px;
    height: 20px; overflow: hidden; margin: 3px 0;
    border: 1px solid rgba(255,255,255,0.08);
}
.bar-fill {
    height: 100%; border-radius: 2px;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 900; color: #05090d; min-width: 28px;
    font-family: 'Rajdhani', sans-serif; letter-spacing: 1px;
}

/* ── Battle log ── */
.log-row {
    border-left: 3px solid #444; border-radius: 4px;
    padding: 7px 13px; margin: 3px 0; font-size: 13px;
    font-family: 'Rajdhani', sans-serif; letter-spacing: 0.5px;
    background: rgba(6, 14, 50, 0.65); backdrop-filter: blur(6px);
}

.stApp .stCaption p { color: #22336a !important; }

@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}
</style>
""", unsafe_allow_html=True)

skin_names   = list(SKINS.keys())
weapon_names = list(WEAPONS.keys())


def hp_bar_color(pct):
    if pct > 0.60: return "#00e676"   # Fortnite green
    if pct > 0.30: return "#ff9100"   # orange warning
    return "#ff1744"                   # red critical


def render_bar(emoji, label, value, max_val, is_hp=True):
    pct = value / max_val if max_val > 0 else 0
    bar_color = hp_bar_color(pct) if is_hp else "#40c4ff"
    width = max(int(pct * 100), 2)
    st.markdown(f"""
<div style="margin:5px 0;">
  <span style="font-size:12px;font-weight:700;color:#7799cc;letter-spacing:1.5px;
    font-family:'Rajdhani',sans-serif;text-transform:uppercase;">
    {emoji} {label}: {value} / {max_val}
  </span>
  <div class="bar-wrap">
    <div class="bar-fill" style="width:{width}%;background:{bar_color};
      box-shadow:0 0 8px {bar_color}bb;">{value}</div>
  </div>
</div>""", unsafe_allow_html=True)


def render_player_card(skin_name, weapon_name, health=None, shields=None):
    s = SKINS[skin_name]
    w = WEAPONS[weapon_name]
    c = s["color"]
    r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)

    # Ability pill uses skin color tinted yellow
    st.markdown(f"""
<div style="
  position:relative; overflow:hidden; border-radius:10px; margin-bottom:10px;
  background:linear-gradient(160deg, rgba({r},{g},{b},0.18) 0%, rgba(5,9,30,0.95) 55%);
  border:1.5px solid rgba({r},{g},{b},0.70);
  box-shadow:0 0 30px rgba({r},{g},{b},0.20), 0 0 0 1px rgba(255,255,255,0.04) inset;
  padding:26px 18px 20px; text-align:center;">

  <!-- Yellow top bar (Fortnite UI) -->
  <div style="position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,transparent 0%,#FFD100 40%,rgba({r},{g},{b},1) 70%,transparent 100%);"></div>

  <!-- Corner HUD brackets -->
  <div style="position:absolute;top:8px;left:8px;width:18px;height:18px;
    border-top:2px solid #FFD100;border-left:2px solid #FFD100;border-radius:2px 0 0 0;opacity:0.8;"></div>
  <div style="position:absolute;top:8px;right:8px;width:18px;height:18px;
    border-top:2px solid #FFD100;border-right:2px solid #FFD100;border-radius:0 2px 0 0;opacity:0.8;"></div>
  <div style="position:absolute;bottom:8px;left:8px;width:18px;height:18px;
    border-bottom:2px solid #FFD100;border-left:2px solid #FFD100;border-radius:0 0 0 2px;opacity:0.8;"></div>
  <div style="position:absolute;bottom:8px;right:8px;width:18px;height:18px;
    border-bottom:2px solid #FFD100;border-right:2px solid #FFD100;border-radius:0 0 2px 0;opacity:0.8;"></div>

  <!-- Avatar -->
  <div style="font-size:90px;line-height:1.05;margin-bottom:8px;
    filter:drop-shadow(0 0 24px rgba({r},{g},{b},1)) drop-shadow(0 4px 12px rgba(0,0,0,0.8));">
    {s['avatar']}
  </div>

  <!-- Skin name — Fortnite bold style -->
  <div style="font-family:'Bangers',sans-serif;font-size:26px;letter-spacing:5px;
    color:#fff;text-shadow:-2px -2px 0 #000,2px -2px 0 #000,-2px 2px 0 #000,2px 2px 0 #000,
    0 0 20px {c};margin-bottom:4px;">
    {skin_name.upper()}
  </div>

  <!-- Weapon -->
  <div style="font-size:13px;color:rgba(180,210,255,0.60);margin-bottom:10px;
    font-family:'Rajdhani',sans-serif;letter-spacing:1.5px;">
    {w['emoji']} &nbsp; {weapon_name.upper()}
  </div>

  <!-- Ability badge -->
  <div class="ability-pill" style="background:#FFD100;">
    ⚡ {s['ability'].upper()}
  </div>
  <div style="font-size:11px;color:rgba(180,210,255,0.42);margin-top:4px;
    font-family:'Rajdhani',sans-serif;">
    {s['ability_desc']}
  </div>
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
        log.append(("ability", f"🍀 <b>{def_skin}</b> — <b>LUCKY BREAK</b>! Dodged the attack!"))
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

# ── Title (Fortnite bold outlined style) ──
st.markdown("""
<div style="text-align:center;padding:14px 0 6px;">
  <div style="font-family:'Bangers',sans-serif;font-size:52px;letter-spacing:7px;
    color:#fff;
    text-shadow:
      -3px -3px 0 #000, 3px -3px 0 #000, -3px 3px 0 #000, 3px 3px 0 #000,
      0 0 24px rgba(255,209,0,0.9), 0 0 60px rgba(255,140,0,0.4);
    line-height:1.05;">
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
**Goal:** Reduce your opponent's HP to 0 to win the match.

**Steps:**
1. Pick your **Skin** — each has a unique special ability.
2. Pick your **Weapon** — each has different damage, accuracy, and crit chance.
3. Hit **START MATCH** to lock in selections.
4. Take turns pressing your **ATTACK** button. Watch the battle log!
5. First player to reach 0 HP loses. 🏆

**Skin Abilities:**
- 🧑 **Jonesy — Lucky Break:** 10% chance to dodge any attack
- 👑 **Midas — Golden Touch:** 20% chance to deal triple damage
- 🐻 **Cuddle Team Leader — Bear Hug:** Heals +8 HP after every attack you land
- ✈️ **Renegade Raider — Aerial Precision:** +20% accuracy on all weapons

**Weapons:**
| Weapon | Damage | Accuracy | Crit Chance |
|---|---|---|---|
| 🔫 Scar | 35 | 85% | 15% |
| 🪖 Pump Shotgun | 70 | 55% | 25% |
| 🚀 Rocket Launcher | 90 | 65% | 10% |
| ⚡ Tactical SMG | 20 | 75% | 20% |

**Battle Log:** 🟡 Crit/Gold · 🟢 Hit · ⚫ Miss · 🔴 Elimination · 🩷 Ability
""")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""<div style="font-family:'Bangers',sans-serif;font-size:22px;
      letter-spacing:4px;color:#4da6ff;text-shadow:-1px -1px 0 #000,1px 1px 0 #000,
      0 0 14px #4da6ff88;margin-bottom:6px;">🟦 AYAAN</div>""", unsafe_allow_html=True)
    p1_skin   = st.selectbox("Choose Skin",   skin_names,   key="p1_skin",   disabled=game_active)
    p1_weapon = st.selectbox("Choose Weapon", weapon_names, key="p1_weapon", disabled=game_active)
    locked_s1 = st.session_state.p1_locked    or p1_skin
    locked_w1 = st.session_state.p1_wpn_locked or p1_weapon
    render_player_card(locked_s1, locked_w1,
        st.session_state.p1_health  if game_active else None,
        st.session_state.p1_shields if game_active else None)

with col2:
    st.markdown("""<div style="font-family:'Bangers',sans-serif;font-size:22px;
      letter-spacing:4px;color:#ff5252;text-shadow:-1px -1px 0 #000,1px 1px 0 #000,
      0 0 14px #ff525288;margin-bottom:6px;">🟥 OMER</div>""", unsafe_allow_html=True)
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
        c = SKINS[winner]["color"]
        st.markdown(f"""
<div style="text-align:center;padding:14px 0;">
  <div style="font-family:'Bangers',sans-serif;font-size:40px;letter-spacing:6px;
    color:#FFD100;
    text-shadow:-3px -3px 0 #000,3px -3px 0 #000,-3px 3px 0 #000,3px 3px 0 #000,
    0 0 28px #FFD100,0 0 60px {c};">
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
st.markdown("""<div style="font-family:'Bangers',sans-serif;font-size:18px;
  color:#FFD100;letter-spacing:4px;margin-bottom:8px;
  text-shadow:-1px -1px 0 #000,1px 1px 0 #000;">
  📜 &nbsp; BATTLE LOG</div>""", unsafe_allow_html=True)

if st.session_state.battle_log:
    for entry_type, text in st.session_state.battle_log:
        border = LOG_COLORS.get(entry_type, "#334466")
        st.markdown(
            f'<div class="log-row" style="border-left-color:{border};">{text}</div>',
            unsafe_allow_html=True)
else:
    st.caption("No actions yet — start a match and attack!")
