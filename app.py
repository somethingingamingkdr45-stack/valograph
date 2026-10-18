import os
import re
import json
import threading
import webbrowser
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import Optional, Dict, List
from engine import HackingGGEngine

app = FastAPI(title="VALOGRAPH")
engine = HackingGGEngine()

LIVE_SCAN = engine.scan_live_game(force_refresh=False)
MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "falkor_memory.json")

CHAT_HISTORY: List[Dict[str, str]] = [
    {
        "sender": "FALKOR",
        "text": "Hey! I'm **FALKOR**, your live Valorant Graph AI. I've loaded your profile, weapons, maps, and match history into FalkorDB. Ask me anything or click a prompt above!"
    }
]

if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            saved_chat = json.load(f)
            if isinstance(saved_chat, list) and len(saved_chat) > 0:
                CHAT_HISTORY = saved_chat
    except Exception:
        pass


def save_chat_memory():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(CHAT_HISTORY[-30:], f, indent=2)
    except Exception:
        pass


# Verified Riot CDN Ability Videos (C, Q, E, X) + Live Scraper for all Agents
OFFICIAL_VIDEOS: Dict[str, Dict[str, str]] = {
    "Sage": {
        "C": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt5a0edb670c30f320/5ecad8732f5c725928765507/Sage_C_v001_web.mp4",
        "Q": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt49b23f9268a43b29/5ecad87152c5395e0f2dd0e8/Sage_Q_v001_web.mp4",
        "E": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/bltf1d16edc36ba3386/5ecad871957e405e09905755/Sage_E_v001_web.mp4",
        "X": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/bltef49762f5c8f5103/5ecad872957e405e09905759/Sage_X_v001_web.mp4"
    },
    "Viper": {
        "C": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt9eb3dd2c03d92282/5ecad893957e405e09905761/Viper_C_v001_web.mp4",
        "Q": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blte5200bab40679f96/5ecad89352c5395e0f2dd0f0/Viper_Q_v001_web.mp4",
        "E": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt66a45c1fe76ca647/5ecad894f5bd13348a6cac95/Viper_E_v001_web.mp4",
        "X": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt41c761118c4b393c/5ecad8944a28e119db5622a6/Viper_X_v001_web.mp4"
    },
    "Jett": {
        "C": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/bltce7928301a67a33a/5ecad7f552c5395e0f2dd0de/Jett_C_v001_web.mp4",
        "Q": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt2c46e5d7a56be140/5ecad7f6957e405e0990574d/Jett_Q_v001_web.mp4",
        "E": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt5368134438181520/5ecad7f7beb6c333c3a0f59d/Jett_E_v001_web.mp4",
        "X": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/bltbbe06825c27b02b1/5ecad7f81b51e3637c926525/Jett_X_v001_web.mp4"
    },
    "Chamber": {
        "C": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt0eb89d191c0f80d7/618d9da0b11220653c600b05/Chamber_C_v001_web.mp4",
        "Q": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt449f7eb3c6677c50/618d9da692311350794309b9/Chamber_Q_v001_web.mp4",
        "E": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt9cb9fb6e1b29a853/618d9db1b8c2642573672940/Chamber_E_v001_web.mp4",
        "X": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt8de0a8c28c883295/618d9db8a8208b1f4c2f3f09/Chamber_X_v001_web.mp4"
    },
    "Reyna": {
        "C": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/bltf6109b8be97e8d96/5ecad85db42d3333c95dd1b2/Reyna_C_v002_web.mp4",
        "Q": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt29e7bf9f8f0f90d2/5ecad85eb42d3333c95dd1b6/Reyna_Q_v001_web.mp4",
        "E": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt7232325782c3b340/5ecad85f52c5395e0f2dd0e4/Reyna_E_v002_web.mp4",
        "X": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt6a07b801972226f5/5ecad860f5bd13348a6cac89/Reyna_X_v001_web.mp4"
    },
    "Omen": {
        "C": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt63486e54ea52945a/5ecad815bab1845d392dfd07/Omen_C_v001_web.mp4",
        "Q": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt5babc7e7c6c24fa0/5ecad8154a28e119db56229e/Omen_Q_v001_web.mp4",
        "E": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt70e2c9db1c0793df/5ecad81652c5395e0f2dd0e0/Omen_E_v001_web.mp4",
        "X": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt65aa85bf6ba5c0e8/5ecad814e2a559592eb0c1b4/Omen_X_v001_web.mp4"
    },
    "Sova": {
        "C": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt2eb66c9638756411/5ecad883f5bd13348a6cac8d/Sova_C_v001_web.mp4",
        "Q": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt7af29765c99f807d/5ecad882e2a559592eb0c1b8/Sova_Q_v001_web.mp4",
        "E": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt664ee1f9a0d2f0a8/5ecad88352c5395e0f2dd0ec/Sova_E_v001_web.mp4",
        "X": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt9fc39c074a5b79b6/5ecad884957e405e0990575d/Sova_X_v001_web.mp4"
    },
    "Killjoy": {
        "C": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt9a8fa11ac887550e/5f21fed949879263218952e4/C-Nanoswarm_1080P.mp4",
        "Q": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt4d14fce93d375232/5f21feda1e22126529c2b2a4/Q-Alarmbot_1080P.mp4",
        "E": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt0fe3462ae9a025a4/5f21fed976b53264d26c656d/E-Turret_1080P.mp4",
        "X": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt1fb1bf6f69f6127c/5f21feda2622a463b9f9793a/X-Lockdown_1080P.mp4"
    },
    "Raze": {
        "C": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt25f9b89103f6c473/5ecad83be2a559592eb0c1b0/Raze_C_v001_web.mp4",
        "Q": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt80eb11f1b761f12a/5ecad83c52c5395e0f2dd0e2/Raze_Q_v001_web.mp4",
        "E": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/bltfe61b8e1c26125b7/5ecad83d957e405e09905751/Raze_E_v001_web.mp4",
        "X": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt60023b671f330740/5ecad83dbeb6c333c3a0f5a1/Raze_X_v001_web.mp4"
    },
    "Cypher": {
        "C": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt019fa05d6b7fddef/5ecad7e5957e405e09905749/Cypher_C_v001_web.mp4",
        "Q": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt47c03800823ce304/5ecad7e62f5c7259287654fb/Cypher_Q_v001_web.mp4",
        "E": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt4d5041142bf23770/5ecad7e74a28e119db56229a/Cypher_E_v001_web.mp4",
        "X": "https://assets.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt29f3591576a3937f/5ecad7e852c5395e0f2dd0da/Cypher_X_v001_web.mp4"
    }
}


class AskReq(BaseModel):
    question: str
    context_info: Optional[str] = ""


def falkor_intelligent_brain(question: str, context_info: str) -> str:
    """
    Conversational FALKOR AI Brain:
    1. Handles greetings ('hi', 'hello', 'hey', 'who are you') naturally using live player telemetry.
    2. Queries FalkorDB / Engine Catalogs for any Agent, Weapon, Map, or Live Player stats.
    3. Optionally enriches via free Pollinations AI without ever failing.
    """
    q_clean = question.strip()
    q_low = q_clean.lower()

    allies = [a for a in LIVE_SCAN.get("ally_slots", []) if a]
    lead_player = allies[0] if allies else None
    p_name = lead_player["name"] if lead_player else "Agent"

    # 1. Conversational Greetings ("hi", "hello", "hey", "sup")
    if q_low in ["hi", "hello", "hey", "yo", "sup", "hii", "heyy"]:
        if lead_player:
            w_str = ", ".join([f"{w['gun']} ({w['kills']}K)" for w in lead_player.get("top_weapons", [])]) or "Vandal"
            m_str = ", ".join([f"{m['map']} ({m['kda']} · {m['acs']} ACS)" for m in lead_player.get("recent_matches", [])[:3]])
            return (
                f"Hey **{p_name}**! 👋 I'm **FALKOR**, connected live to your Valorant Graph.\n\n"
                f"Here is what I have stored in your FalkorDB profile right now:\n"
                f"• **Rank & Level:** {lead_player['rank']} (Lv.{lead_player['level']}) · Main: **{lead_player['agent']}**\n"
                f"• **5v5 Stats:** **{lead_player.get('acs', 130)} ACS** · **{lead_player.get('kd', 0.52)} K/D** · **{lead_player.get('win_rate', 25)}% Win Rate**\n"
                f"• **Top Weapons:** {w_str}\n"
                f"• **Recent Matches:** {m_str}\n\n"
                f"Ask me about any **Agent's C/Q/E/X skills**, **Weapon damage**, **Map callouts**, or how to win your next match!"
            )
        return (
            "Hey there! 👋 I'm **FALKOR**, your Valorant Graph AI assistant.\n"
            "I have all **29 Agents**, **20 Weapons**, and **13 Tactical Maps** loaded in FalkorDB. "
            "Ask me about any Agent build, Weapon TTK, or Map strategy!"
        )

    # 2. Check if user is asking about a specific Agent
    for ag in engine.agents_catalog:
        aname = ag["name"]
        if re.search(rf"\b{re.escape(aname.lower())}\b", q_low):
            sk_lines = [f"• **[{s['key']}] {s['name']} ({s.get('cost', '')}):** {s.get('desc', '')}" for s in ag.get("skills", [])]
            b_maps = ", ".join(ag.get("best_maps", ["Lotus", "Ascent", "Corrode"]))
            dist = ag.get("dist", {"util": 40, "cc": 20, "dmg": 40})
            return (
                f"⚡ **FALKOR AGENT GRAPH — {aname.upper()} [{ag['role']}]**\n"
                f"• **Playstyle:** {ag.get('playstyle', ag['role'])} · Difficulty: **{ag.get('diff', 'Medium')}** ({dist['util']}% Utility / {dist['cc']}% CC / {dist['dmg']}% Damage)\n"
                f"• **Best Maps:** **{b_maps}**\n"
                f"• **Ability Breakdown (C / Q / E / X):**\n" + "\n".join(sk_lines) +
                f"\n• **Pro Tip:** On **{b_maps.split(',')[0]}**, use **[{ag['skills'][0]['key']}] {ag['skills'][0]['name']}** and **[{ag['skills'][2]['key']}] {ag['skills'][2]['name']}** to control main choke points."
            )

    # 3. Check if user is asking about Weapons
    matched_weapons = [w for w in engine.weapons_catalog if re.search(rf"\b{re.escape(w['name'].lower())}\b", q_low)]
    if matched_weapons:
        out = ["🔫 **FALKOR WEAPON BALLISTICS ANALYSIS**"]
        for wp in matched_weapons:
            rng = " | ".join([f"**{r['range']}**: {r['hd']} Head / {r['bd']} Body / {r['ld']} Leg" for r in wp.get("ranges", [])])
            out.append(
                f"• **{wp['name']} ({wp['cat']} · {wp['cost']} Cr):** Fire Rate: **{wp['fr']} rds/s** · Mag: **{wp['mag']}** · Wall Pen: **{wp['pen']}**\n"
                f"  ↳ Damage: {rng}"
            )
        return "\n\n".join(out)

    # 4. Check if user is asking about a specific Map
    for mp in engine.maps_catalog:
        mname = mp["name"]
        if re.search(rf"\b{re.escape(mname.lower())}\b", q_low):
            top_a = ", ".join(mp.get("top_agents", []))
            calls = ", ".join(mp.get("callouts", [])[:12])
            return (
                f"🗺️ **FALKOR MAP INTEL — {mname.upper()} ({mp['sites']})**\n"
                f"• **Win Rate Split:** Attackers **{mp['atk_wr']}%** vs Defenders **{mp['def_wr']}%**\n"
                f"• **Top 5 Meta Agents:** **{top_a}**\n"
                f"• **Key Callout Zones:** {calls}\n"
                f"• **Tactical Summary:** {mp['desc']}"
            )

    # 5. Try Free Keyless Cloud AI (Pollinations) with full context for open-ended questions
    try:
        ctx_summary = f"Player: {lead_player['name']} (Lv.{lead_player['level']}, {lead_player['rank']}, Main: {lead_player['agent']}, ACS: {lead_player.get('acs')}, Weapons: {lead_player.get('top_weapons')}, Matches: {lead_player.get('recent_matches')})" if lead_player else "Valorant Graph Active"
        r = requests.post(
            "https://text.pollinations.ai/",
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            json={
                "model": "openai",
                "messages": [
                    {"role": "system", "content": "You are FALKOR, a smart, friendly Valorant Esports AI Coach powered by FalkorDB. Answer concisely with bullet points using the player's real stats."},
                    {"role": "user", "content": f"Context: {ctx_summary}\nSelected View: {context_info}\nUser Question: {q_clean}"}
                ]
            },
            timeout=4.5
        )
        if r.status_code == 200 and len(r.text.strip()) > 15 and "<!DOCTYPE" not in r.text:
            if r.text.strip().startswith("{"):
                return r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return r.text.strip()
    except Exception:
        pass

    # 6. Smart Personal Match & Stats Coach Fallback
    if lead_player:
        w_str = ", ".join([f"{w['gun']} ({w['kills']}K)" for w in lead_player.get("top_weapons", [])]) or "Vandal"
        best_m = max(lead_player.get("recent_matches", [{"map": "Corrode", "acs": 221, "kda": "4/5/0"}]), key=lambda x: x.get("acs", 0))
        return (
            f"🧠 **FALKOR COACH INSIGHT FOR {p_name.upper()}**\n"
            f"• **Strongest Recent Performance:** **{best_m['map']}** where you hit **{best_m['acs']} ACS** ({best_m['kda']} KDA).\n"
            f"• **Weapon Synergy:** Your top kill weapons in the graph are **{w_str}**. Stick to **Vandal** on full-buys and **Spectre / Ghost** on eco rounds.\n"
            f"• **Next Step:** Click any Match or Agent node on the 3D Graph, or ask me about a specific Agent (e.g. *Sage*, *Viper*, *Chamber*, *Clove*) or Map (*Lotus*, *Corrode*, *Ascent*)!"
        )

    return "⚡ **FALKOR:** Ask me about any Valorant Agent, Weapon, or Map in the graph!"


@app.get("/api/bootstrap")
def api_bootstrap():
    global LIVE_SCAN
    LIVE_SCAN = engine.scan_live_game(force_refresh=False)
    return {
        "falkor_connected": engine.is_connected,
        "falkor_host": engine.falkor_host,
        "last_cypher": engine.last_cypher,
        "live": LIVE_SCAN,
        "agents": engine.agents_catalog,
        "maps": engine.maps_catalog,
        "weapons": engine.weapons_catalog,
        "chat": CHAT_HISTORY
    }


@app.get("/api/agent_videos/{agent_name}")
def api_agent_videos(agent_name: str):
    if agent_name in OFFICIAL_VIDEOS:
        vmap = OFFICIAL_VIDEOS[agent_name]
        return {"videos": [vmap.get("C", ""), vmap.get("Q", ""), vmap.get("E", ""), vmap.get("X", "")], "by_key": vmap}

    slug = agent_name.lower().replace("/", "").replace(" ", "-")
    found = []
    for url in [
        f"https://playvalorant.com/page-data/en-us/agents/{slug}/page-data.json",
        f"https://playvalorant.com/en-us/agents/{slug}/"
    ]:
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3.5)
            if r.status_code == 200:
                for m in re.findall(r"https://[^\s\"'<>\\]+?\.mp4", r.text):
                    if m not in found:
                        found.append(m)
            if len(found) >= 4:
                break
        except Exception:
            pass

    # Fallback to Sage/Jett official demo clips if Riot hasn't uploaded 2026 agent clips yet, so C/Q/E/X video players ALWAYS play live video!
    default_vids = list(OFFICIAL_VIDEOS["Sage"].values())
    vids = found[:4] if len(found) >= 4 else (found + default_vids)[:4]
    by_key = {k: vids[idx] for idx, k in enumerate(["C", "Q", "E", "X"])}
    return {"videos": vids, "by_key": by_key}


@app.post("/api/scan")
def api_scan(force: bool = False):
    global LIVE_SCAN
    LIVE_SCAN = engine.scan_live_game(force_refresh=force)
    return {"live": LIVE_SCAN, "falkor_connected": engine.is_connected, "last_cypher": engine.last_cypher}


@app.get("/api/match/{match_id}")
def api_match_deep_dive(match_id: str, puuid: str = ""):
    details = engine.parse_selected_match_deep_dive(match_id, focus_puuid=puuid)
    return {"match": details, "last_cypher": engine.last_cypher}


@app.post("/api/ask_fallkor")
def api_ask_falkor(req: AskReq):
    q = req.question.strip()
    CHAT_HISTORY.append({"sender": "YOU", "text": q})
    ans = falkor_intelligent_brain(q, req.context_info or "")
    CHAT_HISTORY.append({"sender": "FALKOR", "text": ans})
    save_chat_memory()
    engine.run_cypher("MERGE (m:ChatMemory {q:$q}) SET m.a=$a", {"q": q[:80], "a": ans[:160]})
    return {"chat": CHAT_HISTORY, "last_cypher": engine.last_cypher}


@app.get("/", response_class=HTMLResponse)
def serve_valograph():
    here = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(here, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="text/html", headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    return f"<h1>index.html not found in {here}</h1>"


if __name__ == "__main__":
    import uvicorn
    threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:8095")).start()
    uvicorn.run(app, host="127.0.0.1", port=8095)