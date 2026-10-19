
# 🎯 VALOGRAPH (ValGraph AI) — Tactical Graph Intelligence & Persistent Memory Engine

Built for the **WeMakeDevs x FalkorDB Graph Hacks Hackathon**.  
**Repository:** `https://github.com`  
**Tracks Entered:**
* **Track 1:** Agents That Act on Connected Data
* **Track 2:** Agent Memory and Coordination

---

## 🚀 Overview & Problem Solved

Competitive Valorant players, IGLs (In-Game Leaders), and esports analysts rely on fragmented, static stat trackers and external wikis that only display isolated flat tables. Standard LLMs fail at live tactical coaching because they hallucinate patch stats, cannot traverse multi-hop relationships across map geometry, agent skill synergies, and weapon damage profiles simultaneously, and forget player context between sessions.

**VALOGRAPH** solves this by modeling the entire Valorant tactical ecosystem inside **FalkorDB (`hacking_gg_valorant`)** and rendering an interactive, zero-redirect 3D/2D tactical graph command center directly in the browser. Users can inspect Agents, Skills, Weapons, Maps, and Live 10-Player Match Rosters, while interacting with **Ask Falkor** and **AI Team Combo** powered by FalkorDB and Groq.

---

## 🧠 Graph Data Model (FalkorDB Schema)

Our FalkorDB Cloud instance (`hacking_gg_valorant`) powers the entire application in real time (~1.36ms query latency across 145+ nodes and 116+ edges).

### Node Labels & Properties
* **`(:Agent)`** — `name`, `role`, `descr`, `atk_wr`, `def_wr`, `diff`
* **`(:Skill)`** — `key` (`C`, `Q`, `E`, `X`), `name`, `descr`
* **`(:Weapon)`** — `name`, `cat`, `cost`, `fire_rate`, `mag`, `pen`
* **`(:Map)`** — `name`, `sites`, `atk_wr`, `def_wr`
* **`(:Player)`** — `riot_id`, `name`, `level`, `rank`, `agent`, `acs`, `kd`, `kda`, `playstyle`
* **`(:Match)`** — `mid`, `map`, `result`, `kda`, `acs`
* **`(:Memory)`** — `id`, `question`, `ans`, `text`, `ts`

### Relationships (Edges)
* `(:Agent)-[:HAS_SKILL]->(:Skill)` — Links each Agent to their C, Q, E, and X tactical abilities.
* `(:Player)-[:PLAYS]->(:Agent)` — Tracks which Agent a player mains or runs in a live match.
* `(:Player)-[:PLAYED]->(:Match)` — Connects players to recent match performances (`K/D/A`, `ACS`, `WIN/LOSS`, `Map`).
* `(:Player)-[:REMEMBERS]->(:Memory)` — Persistent cross-session AI coaching memory stored in FalkorDB.

---

## 🔍 Core Cypher Queries Used

VALOGRAPH executes real-time parameterized OpenCypher queries on every node click and AI request (visible in the live Cypher telemetry bar at the bottom of the UI):

```cypher
-- 1. Fetch Agent & Connected Skills Subgraph
MATCH p=(a:Agent)-[:HAS_SKILL]->(s:Skill) RETURN p

-- 2. Upsert & Hydrate Live 10-Player Match Roster
MERGE (p:Player {riot_id: $rid})
SET p.name = $n, p.level = $lv, p.rank = $rk, p.agent = $ag, p.acs = $acs, p.kd = $kd

-- 3. Upsert & Query Weapon Telemetry
MERGE (w:Weapon {name: $n})
SET w.cat = $c, w.cost = $cost

-- 4. Retrieve Persistent Agent Memory Across Sessions
MATCH (p:Player)-[:REMEMBERS]->(m:Memory)
RETURN m.question, m.ans, m.ts ORDER BY m.ts DESC LIMIT 5
```

---

## 💻 Local Setup Instructions (How to Run `python app.py`)

VALOGRAPH runs locally via Python and connects directly to FalkorDB Cloud (or local Docker).

### 1. Clone the Repository
```bash
git clone https://github.com.git
cd valograph
```

### 2. Install Dependencies
```bash
pip install flask falkordb groq requests python-dotenv flask-cors
```

### 3. Configure Credentials
Set your environment variables (or configure your FalkorDB & Groq keys inside `.env` / `app.py`):
```env
FALKORDB_HOST=your-falkordb-instance.cloud
FALKORDB_PORT=60049
FALKORDB_USERNAME=falkordb
FALKORDB_PASSWORD=your_falkordb_password
GROQ_API_KEY=your_groq_api_key
```

### 4. Run the Application
```bash
python app.py
```
Then open the local URL shown in your terminal (e.g., `http://127.0.0.1:8095` or `http://127.0.0.1:5000`) in your browser. *(Note: Ensure `index.html` is placed in the `templates/` folder if running via standard Flask `render_template`, or in the root directory as configured in `app.py`.)*

---

## 🤖 AI Assistance Disclosure (Rule 11)
AI coding assistants (Google Gemini) were used during development to assist with UI styling, debugging, and documentation structuring. All graph modeling, architecture design, and feature integrations were directed, verified, and tested by the developer.
