# 🚦 Real-Time Feature Flag & Remote Config Engine

A lightweight, zero-dependency, full-stack architecture for managing feature flags, percentage-based rollouts, and remote configurations. This system provides a real-time Server-Sent Events (SSE) pipeline to instantly push UI updates to client applications without requiring browser refreshes or aggressive polling.

## 🏗️ System Architecture

This project is decoupled into three primary components:

1. **The Evaluation Engine (FastAPI):** A high-concurrency backend powered by an SQLite database. It utilizes deterministic SHA-256 modulo hashing to guarantee stable percentage rollouts and maintains an active SSE pipeline for real-time state broadcasting.

2. **The Control Plane (Textual):** A CLI-native, terminal-based admin dashboard. It features real-time asynchronous database mutations and a built-in JSON editor for managing complex, nested targeting rules without needing a web dashboard.

3. **The Client SDK (Flutter/Dart):** A strictly typed integration featuring persistent local caching, native unboxing wrappers, and a state-aware, non-blocking background telemetry loop.

## ✨ Key Features

* **Zero Heavy Infrastructure:** Runs entirely on Python, FastAPI, and SQLite. No Redis, Postgres, or Docker required.
* **Deterministic Rollouts:** Users are assigned to percentage buckets using a strict `SHA-256` hashing algorithm (`hash(userId + flagId) % 100`). This ensures zero UI flickering across app reboots.
* **Contextual Group Targeting:** Serve features exclusively to specific user cohorts (e.g., `beta_testers`, `internal_admins`) via nested JSON payload evaluations.
* **State-Aware Telemetry:** The SDK tracks the last evaluated state of every flag and only fires HTTP `POST` metrics when a value actively changes, completely eliminating DDOS risks during high-frequency UI repaints.
* **CanvasKit Safe:** The Dart client handles SSE socket closures gracefully, preventing WebGL context crashes during hot-restarts.

## 📌 Assumptions & Design Decisions
To ensure portability and ease of verification, the following architectural assumptions and decisions were made:
* **Storage Assumption (SQLite):** It is assumed that for this scope, horizontal database scaling is not immediately required. SQLite was intentionally chosen to provide a zero-dependency, instantly runnable environment for reviewers without requiring Docker or Postgres setups.
* **Protocol Decision (SSE vs. WebSockets):** Server-Sent Events (SSE) were chosen over WebSockets because feature flags inherently require a one-way data flow (Server -> Client). SSE operates over standard HTTP/1.1, avoiding the overhead and firewall complexities of full-duplex WebSockets.
* **Client Environment:** It is assumed the client application is built on Flutter/Dart, utilizing `SharedPreferences` for local persistence to survive cold boots.

## 🚀 Quick Start & Compilation

### 1. Boot the Backend Engine
The backend serves the API, handles evaluation math, and maintains the SSE connections.

```bash
# Install required Python dependencies
pip install -r requirements.txt

# Boot the FastAPI server (auto-generates the local SQLite db)
uvicorn main:app --reload
```
*Server runs on `http://localhost:8000`*

### 2. Launch the Control Plane (TUI)
Manage your flags locally through the terminal interface. Open a new terminal window and run:

```bash
# Run the Textual admin dashboard
python tui/app.py 
```
* **Navigation:** Use arrow keys to select flags.
* **Toggle State:** Press `Space` to flip a boolean flag ON/OFF.
* **Edit Rules:** Press `e` to open the JSON targeting editor.

### 3. Run the Flutter Client
Ensure you have the Flutter SDK installed and an emulator running (or Chrome for web testing).

```bash
# Get Dart dependencies
flutter pub get

# Run the application
flutter run
```

## 🧪 Testing & Mathematical Verification

This engine was built with rigorous mathematical distribution testing. To verify the integrity of the deterministic hashing engine at scale without needing to launch thousands of Flutter clients, a Monte Carlo simulation script is included.

**To run the distribution test:**
```bash
# Execute the hash verification script
python verify_math.py
```

**Test Protocol:** The script processes $10,000$ unique UUID strings through the core targeting algorithm:
$$
H = \text{SHA-256}(\text{userId} + \text{":"} + \text{flagId})
$$
$$
Bucket = \text{int}(H, 16) \pmod{100}
$$

**Expected Results (for a 10% Target):**
* Target Rollout: `10.00%`
* Actual Distribution: `~9.8% - 10.2%`
* **Result:** The avalanche effect of the cryptographic hash successfully guarantees uniform distribution without algorithmic bias, proving the mathematical soundness of the backend.