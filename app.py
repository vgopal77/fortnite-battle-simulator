import random
import streamlit as st
from gamedata import SKINS, WEAPONS

st.set_page_config(page_title="Fortnite Battle Simulator", page_icon="💥", layout="wide")

st.markdown("""
<style>
.ability-pill {
    display: inline-block;
    border-radius: 999px;
    padding: 3px 14px;
    font-size: 12px;
    font-weight: 700;
    color: white;
    margin: 6px 0 2px;
}
.bar-wrap {
    background: #ddd;
    border-radius: 8px;
    height: 22px;
    overflow: hidden;
    margin: 3px 0;
}
.bar-fill {
    height: 100%;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: white;
    min-width: 28px;
    transition: width 0.3s;
}
.log-row {
    border-left: 4px solid #ccc;
    border-radius: 4px;
    padding: 6px 12px;
    margin: 3px 0;
    font-size: 13px;
    background: rgba(0,0,0,0.03);
}
</style>
""", unsafe_allow_html=True)

skin_names = list(SKINS.keys())
weapon_names = list(WEAPONS.keys())


def hp_bar_color(pct):
    if pct > 0.6:
        return "#4CAF50"
    elif pct > 0.3:
        return "#FF9800"
    return "#F44336"


def render_bar(emoji, label, value, max_val, color):
    pct = value / max_val if max_val > 0 else 0
    bar_color = hp_bar_color(pct) if emoji == "❤️" else color
    width = max(int(pct * 100), 2)
    st.markdown(f"""
<div style="margin:4px 0;">
  <span style="font-size:13px; font-weight:600;">{emoji} {label}: {value}/{max_val}</span>
  <div class="bar-wrap">
    <div class="bar-fill" style="width:{width}%; background:{bar_color};">{value}</div>
  </div>
</div>""", unsafe_allow_html=True)


def render_player_card(skin_name, weapon_name, health=None, shields=None):
    s = SKINS[skin_name]
    w = WEAPONS[weapon_name]
    color = s["color"]
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    bg = f"rgba({r},{g},{b},0.07)"
    st.markdown(f"""
<div style="background:{bg}; border:2px solid {color}; border-radius:16px;
     padding:20px; text-align:center; margin-bottom:10px;">
  <div style="font-size:76px; line-height:1.1;">{s['avatar']}</div>
  <h3 style="color:{color}; margin:8px 0 2px;">{skin_name}</h3>
  <div style="font-size:13px; opacity:0.75;">{w['emoji']} {weapon_name}</div>
  <div class="ability-pill" style="background:{color};">⚡ {s['ability']}</div>
  <div style="font-size:11px; opacity:0.6; margin-top:2px;">{s['ability_desc']}</div>
</div>""", unsafe_allow_html=True)

    if health is not None:
        render_bar("❤️", "HP", health, SKINS[skin_name]["health"], color)
        render_bar("🛡️", "Shields", shields, SKINS[skin_name]["shields"], "#2196F3")


def init_state():
    defaults = {
        "p1_health": None, "p1_shields": None,
        "p2_health": None, "p2_shields": None,
        "p1_locked": None, "p2_locked": None,
        "p1_wpn_locked": None, "p2_wpn_locked": None,
        "battle_log": [], "game_over": False, "winner": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def start_match(s1, s2, w1, w2):
    st.session_state.p1_health = SKINS[s1]["health"]
    st.session_state.p1_shields = SKINS[s1]["shields"]
    st.session_state.p2_health = SKINS[s2]["health"]
    st.session_state.p2_shields = SKINS[s2]["shields"]
    st.session_state.p1_locked = s1
    st.session_state.p2_locked = s2
    st.session_state.p1_wpn_locked = w1
    st.session_state.p2_wpn_locked = w2
    st.session_state.battle_log = []
    st.session_state.game_over = False
    st.session_state.winner = None


def reset_match():
    for k in ["p1_health", "p1_shields", "p2_health", "p2_shields",
              "p1_locked", "p2_locked", "p1_wpn_locked", "p2_wpn_locked",
              "game_over", "winner"]:
        st.session_state[k] = None
    st.session_state.battle_log = []


def apply_damage(hp, sh, dmg):
    if sh > 0:
        absorbed = min(sh, dmg)
        sh -= absorbed
        dmg -= absorbed
    hp = max(0, hp - dmg)
    return hp, sh


def do_attack(atk_skin, def_skin, weapon_name,
              def_hp_key, def_sh_key, atk_hp_key, atk_sh_key):
    w = WEAPONS[weapon_name]
    atk = SKINS[atk_skin]
    dfd = SKINS[def_skin]
    log = []

    accuracy = w["accuracy"]
    if atk_skin == "Renegade Raider":
        accuracy = min(0.98, accuracy + atk.get("accuracy_bonus", 0))

    if random.random() >= accuracy:
        log.append(("miss", f"💨 **{atk_skin}** fired {w['emoji']} {weapon_name} — **MISSED!**"))
        st.session_state.battle_log = log + st.session_state.battle_log
        return

    if def_skin == "Jonesy" and random.random() < dfd.get("dodge_chance", 0):
        log.append(("ability", f"🍀 **{def_skin}** triggered **Lucky Break** — dodged the attack!"))
        st.session_state.battle_log = log + st.session_state.battle_log
        return

    damage = w["damage"]
    label = "Hit"
    entry_type = "hit"

    if atk_skin == "Midas" and random.random() < atk.get("gold_chance", 0):
        damage = w["damage"] * 3
        label = "👑 GOLDEN TOUCH — TRIPLE DAMAGE"
        entry_type = "crit"
    elif random.random() < w["crit_chance"]:
        damage = w["damage"] * 2
        label = "💥 CRITICAL HIT"
        entry_type = "crit"

    prev_hp = st.session_state[def_hp_key]
    prev_sh = st.session_state[def_sh_key]
    new_hp, new_sh = apply_damage(prev_hp, prev_sh, damage)
    st.session_state[def_hp_key] = new_hp
    st.session_state[def_sh_key] = new_sh

    sh_note = f" | 🛡️ {prev_sh}→{new_sh}" if prev_sh != new_sh else ""
    log.append((entry_type,
        f"{'💥' if entry_type == 'crit' else '🎯'} **{atk_skin}** → **{def_skin}** "
        f"with {w['emoji']} {weapon_name}: **{label}** for **{damage} dmg** | "
        f"❤️ {prev_hp}→{new_hp}{sh_note}"
    ))

    if atk_skin == "Cuddle Team Leader":
        heal = atk.get("heal_amount", 0)
        old_atk_hp = st.session_state[atk_hp_key]
        max_hp = SKINS[atk_skin]["health"]
        new_atk_hp = min(max_hp, old_atk_hp + heal)
        st.session_state[atk_hp_key] = new_atk_hp
        if new_atk_hp > old_atk_hp:
            log.append(("ability",
                f"🐻 **{atk_skin}** activated **Bear Hug** — healed +{heal} HP! ({old_atk_hp}→{new_atk_hp})"
            ))

    if new_hp <= 0:
        st.session_state.game_over = True
        st.session_state.winner = atk_skin
        log.append(("win", f"🏆 **{atk_skin}** has eliminated **{def_skin}**!"))

    st.session_state.battle_log = log + st.session_state.battle_log


# ── Layout ────────────────────────────────────────────────────────────────────

init_state()
game_active = st.session_state.p1_health is not None

st.markdown("<h1 style='text-align:center;'>💥 Fortnite Battle Simulator</h1>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟦 Player 1")
    p1_skin = st.selectbox("Choose Skin", skin_names, key="p1_skin", disabled=game_active)
    p1_weapon = st.selectbox("Choose Weapon", weapon_names, key="p1_weapon", disabled=game_active)
    locked_s1 = st.session_state.p1_locked or p1_skin
    locked_w1 = st.session_state.p1_wpn_locked or p1_weapon
    render_player_card(
        locked_s1, locked_w1,
        st.session_state.p1_health if game_active else None,
        st.session_state.p1_shields if game_active else None,
    )

with col2:
    st.markdown("### 🟥 Player 2")
    p2_skin = st.selectbox("Choose Skin", skin_names, index=1, key="p2_skin", disabled=game_active)
    p2_weapon = st.selectbox("Choose Weapon", weapon_names, index=1, key="p2_weapon", disabled=game_active)
    locked_s2 = st.session_state.p2_locked or p2_skin
    locked_w2 = st.session_state.p2_wpn_locked or p2_weapon
    render_player_card(
        locked_s2, locked_w2,
        st.session_state.p2_health if game_active else None,
        st.session_state.p2_shields if game_active else None,
    )

st.markdown("---")

if not game_active:
    if st.button("🎮 Start Match!", use_container_width=True, type="primary"):
        start_match(p1_skin, p2_skin, p1_weapon, p2_weapon)
        st.rerun()
else:
    if st.session_state.game_over:
        st.balloons()
        winner = st.session_state.winner
        color = SKINS[winner]["color"]
        st.markdown(
            f"<h2 style='text-align:center; color:{color};'>🏆 {winner} WINS THE MATCH! 🏆</h2>",
            unsafe_allow_html=True,
        )
        if st.button("🔄 Play Again", use_container_width=True, type="primary"):
            reset_match()
            st.rerun()
    else:
        a1, a2 = st.columns(2)
        with a1:
            if st.button("💥 P1 ATTACKS!", use_container_width=True, type="primary"):
                do_attack(
                    st.session_state.p1_locked, st.session_state.p2_locked,
                    st.session_state.p1_wpn_locked,
                    "p2_health", "p2_shields", "p1_health", "p1_shields",
                )
                st.rerun()
        with a2:
            if st.button("💥 P2 ATTACKS!", use_container_width=True, type="primary"):
                do_attack(
                    st.session_state.p2_locked, st.session_state.p1_locked,
                    st.session_state.p2_wpn_locked,
                    "p1_health", "p1_shields", "p2_health", "p2_shields",
                )
                st.rerun()

# ── Battle Log ────────────────────────────────────────────────────────────────

LOG_COLORS = {
    "hit": "#4CAF50",
    "crit": "#FFD700",
    "miss": "#9E9E9E",
    "ability": "#E91E63",
    "win": "#FF5722",
}

st.markdown("---")
st.markdown("### 📜 Battle Log")
if st.session_state.battle_log:
    for entry_type, text in st.session_state.battle_log:
        border = LOG_COLORS.get(entry_type, "#ccc")
        st.markdown(
            f'<div class="log-row" style="border-left-color:{border};">{text}</div>',
            unsafe_allow_html=True,
        )
else:
    st.caption("No actions yet — start a match and attack!")
