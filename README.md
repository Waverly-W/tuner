# Novel-to-Audio Interactive Studio

An intelligent, human-in-the-loop tool for converting novels (TXT/EPUB) into high-quality audiobooks with multi-speaker support and emotion analysis.

## 🚀 Getting Started

### Prerequisites
- **Python** 3.10+
- **Node.js** 20.19.5 (Recommended to use `nvm`)
- **FFmpeg** (Required for audio processing)

### 1. Start the Backend
The backend is built with FastAPI and handles file processing, LLM analysis, and TTS synthesis.

```bash
# Navigate to project root
cd /home/waverly/workspace/tuner

# Activate virtual environment
source backend/venv/bin/activate

# Install dependencies (if not already installed)
pip install -r backend/requirements.txt

# Start the server
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8002 --reload
```
*Backend will run at `http://localhost:8002`*

### 2. Start the Frontend
The frontend is a React application using shadcn/ui for the interactive studio interface.

```bash
# Navigate to frontend directory
cd frontend

# Use correct Node version
# If you have nvm installed:
nvm use 20.19.5

# Install dependencies
npm install

# Start development server
npm run dev
```
*Frontend will run at `http://localhost:5173`*

## 📖 User Workflow

The studio follows a 4-stage interactive process:

### Stage 1: Import & Structure (结构化)
1.  **Create Project**: Upload your novel file (`.txt` or `.epub`).
2.  **Review Structure**: The system automatically splits the text into chapters and sentences.
3.  **Edit**: You can manually edit the text segments in the sidebar if needed.
4.  **Action**: Click **"Run AI Analysis"** to proceed.

### Stage 2: AI Analysis (智能分析)
1.  **Review Tags**: The system identifies:
    *   **Noise**: Non-narrative text (grayed out).
    *   **Speakers**: Character assignments for dialogue.
    *   **Emotions**: Emotional tone for each sentence.
2.  **Action**: Review the analysis results.
3.  **Action**: Click **"Start Synthesis"** to generate audio.

### Stage 3: Audio Workbench (合成与预览)
1.  **Listen**: Inline audio players will appear for each sentence.
2.  **Verify**: Play individual clips to check quality and character voices.
3.  **Regenerate**: Re-generate specific clips if needed (Feature in progress).

### Stage 4: Export (导出)
1.  **Finalize**: Click **"Export Audiobook"**.
2.  **Download**: Get a ZIP file containing the full audiobook and metadata.

## 🛠️ Tech Stack
- **Backend**: FastAPI, Python, LangChain (LLM), Edge-TTS / OpenAI TTS
- **Frontend**: React, TypeScript, Vite, Zustand, Tailwind CSS, shadcn/ui
- **Persistence**: File-based (JSON) for MVP
