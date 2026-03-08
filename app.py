"""
╔══════════════════════════════════════════════════════╗
║      AI RESUME ANALYZER - Groq Edition (FREE)        ║
║                                                      ║
║  STEP 1 - Install (run once in terminal):            ║
║    pip install fastapi uvicorn groq pdfplumber       ║
║               python-multipart                       ║
║                                                      ║
║  STEP 2 - Get FREE Groq API Key:                     ║
║    Go to: console.groq.com → Sign up → API Keys      ║
║    Paste your key below                              ║
║                                                      ║
║  STEP 3 - Run:                                       ║
║    python app.py                                     ║
║                                                      ║
║  OPEN:  http://localhost:8000                        ║
╚══════════════════════════════════════════════════════╝
"""

# ─── CONFIG ───────────────────────────────────────────
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your_actual_gsk_key_here")
PORT = 8000
# ──────────────────────────────────────────────────────

import os, io, json, re, webbrowser, threading, time
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from groq import Groq
import pdfplumber, uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
client = Groq(api_key=GROQ_API_KEY)

# ─── HTML FRONTEND ────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>AI Resume Analyzer</title>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #080c18; --surface: rgba(255,255,255,0.033); --border: rgba(255,255,255,0.07);
    --green: #00f5a0; --blue: #00c8f5; --red: #ff5e7a; --text: #dde4f0; --muted: #6a7a90; --radius: 14px;
  }
  body {
    background: var(--bg); color: var(--text); font-family: 'Sora', sans-serif;
    min-height: 100vh; padding: 40px 16px 80px;
    background-image: radial-gradient(ellipse at 20% 20%, rgba(0,245,160,0.05) 0%, transparent 60%),
                      radial-gradient(ellipse at 80% 80%, rgba(0,200,245,0.05) 0%, transparent 60%);
  }
  ::selection { background: rgba(0,245,160,0.2); }
  .header { text-align: center; margin-bottom: 52px; }
  .badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0,245,160,0.08); border: 1px solid rgba(0,245,160,0.2);
    border-radius: 100px; padding: 6px 18px; margin-bottom: 22px;
  }
  .badge-dot { width: 7px; height: 7px; background: var(--green); border-radius: 50%; animation: blink 2s infinite; }
  .badge span { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--green); letter-spacing: 2.5px; }
  @keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
  h1 {
    font-size: clamp(36px, 6vw, 62px); font-weight: 800; line-height: 1.1;
    background: linear-gradient(135deg, #dde4f0 40%, #6a7a90 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 14px;
  }
  .subtitle { color: var(--muted); font-size: 15px; font-weight: 300; }
  .free-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,209,102,0.1); border: 1px solid rgba(255,209,102,0.25);
    border-radius: 100px; padding: 4px 14px; margin-top: 12px;
    font-size: 12px; color: #ffd166; font-family: 'DM Mono', monospace;
  }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 26px 28px; backdrop-filter: blur(12px); }
  .section-label { font-family: 'DM Mono', monospace; font-size: 10px; font-weight: 500; letter-spacing: 3px; color: var(--muted); text-transform: uppercase; margin-bottom: 14px; }
  .wrap { max-width: 960px; margin: 0 auto; }
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  @media(max-width:680px){ .grid2 { grid-template-columns: 1fr; } }
  .upload-zone { border: 2px dashed #2a3350; border-radius: 12px; padding: 40px 20px; text-align: center; cursor: pointer; transition: all 0.25s; }
  .upload-zone:hover, .upload-zone.drag { border-color: rgba(0,245,160,0.5); background: rgba(0,245,160,0.04); }
  .upload-zone.has-file { border-color: rgba(0,245,160,0.4); background: rgba(0,245,160,0.04); }
  .upload-icon { font-size: 44px; margin-bottom: 12px; }
  .upload-main { font-weight: 600; font-size: 14px; margin-bottom: 5px; }
  .upload-sub { color: var(--muted); font-size: 12px; }
  .file-name { color: var(--green); font-weight: 600; font-size: 14px; margin-bottom: 4px; }
  textarea {
    width: 100%; height: 186px; background: rgba(255,255,255,0.03); border: 1px solid #2a3350;
    border-radius: 10px; color: var(--text); font-family: 'Sora', sans-serif; font-size: 13px;
    padding: 14px 16px; resize: none; line-height: 1.65; transition: border-color 0.2s;
  }
  textarea:focus { outline: none; border-color: rgba(0,245,160,0.4); }
  textarea::placeholder { color: var(--muted); }
  .char-count { color: var(--muted); font-size: 11px; margin-top: 7px; font-family: 'DM Mono', monospace; }
  .btn {
    width: 100%; padding: 17px; border: none; border-radius: 12px;
    background: linear-gradient(135deg, var(--green), var(--blue));
    color: #070b14; font-family: 'Sora', sans-serif; font-size: 15px;
    font-weight: 700; cursor: pointer; transition: all 0.25s; margin-top: 6px;
  }
  .btn:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 10px 36px rgba(0,245,160,0.3); }
  .btn:disabled { opacity: 0.45; cursor: not-allowed; transform: none; }
  .error-box { background: rgba(255,94,122,0.08); border: 1px solid rgba(255,94,122,0.25); border-radius: 10px; padding: 13px 18px; color: #ff8fa0; font-size: 13px; margin-bottom: 16px; text-align: center; }
  .score-wrap { text-align: center; padding: 10px 0; }
  .score-ring-container { position: relative; width: 150px; height: 150px; margin: 0 auto 16px; }
  .score-ring-container svg { transform: rotate(-90deg); }
  .score-center { position: absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align: center; }
  .score-num { font-size: 42px; font-weight: 800; font-family: 'DM Mono', monospace; line-height: 1; }
  .score-lbl { font-size: 10px; color: var(--muted); letter-spacing: 2px; margin-top: 2px; font-family:'DM Mono',monospace; }
  .score-verdict { font-size: 13px; font-weight: 600; margin-top: 8px; }
  .results { animation: fadeUp 0.6s ease; }
  @keyframes fadeUp { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:translateY(0)} }
  .results-top { display: grid; grid-template-columns: 200px 1fr; gap: 18px; margin-bottom: 18px; }
  @media(max-width:680px){ .results-top { grid-template-columns: 1fr; } }
  .results-mid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px; }
  @media(max-width:680px){ .results-mid { grid-template-columns: 1fr; } }
  .tag { display: inline-block; border-radius: 6px; padding: 3px 11px; font-size: 12px; font-family: 'DM Mono', monospace; font-weight: 500; margin: 3px 4px 3px 0; }
  .tag-red { background: rgba(255,94,122,0.12); color: var(--red); border: 1px solid rgba(255,94,122,0.25); }
  .check-list { list-style: none; padding: 0; }
  .check-list li { padding: 6px 0; color: #b0bdd0; font-size: 13px; line-height: 1.6; border-bottom: 1px solid rgba(255,255,255,0.04); }
  .check-list li:last-child { border-bottom: none; }
  .check-list li::before { content: '›'; color: var(--green); margin-right: 10px; font-weight: 700; }
  .improve-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; }
  .improve-item { background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 14px 16px; }
  .improve-section { font-family:'DM Mono',monospace; font-size:11px; color: var(--green); font-weight:600; margin-bottom:7px; letter-spacing:1px; }
  .improve-text { color: #b0bdd0; font-size: 13px; line-height: 1.6; }
  .rewrite-box { background: rgba(0,245,160,0.04); border: 1px solid rgba(0,245,160,0.15); border-radius: 12px; padding: 22px 24px 18px; color: #c0d0e0; font-size: 14px; line-height: 1.8; font-style: italic; position: relative; }
  .rewrite-box::before { content: '"'; font-size: 60px; color: rgba(0,245,160,0.15); position:absolute; top:-10px; left:14px; font-family:Georgia,serif; line-height:1; }
  .loading { text-align: center; padding: 60px 20px; }
  .spinner { width: 48px; height: 48px; border: 3px solid rgba(0,245,160,0.1); border-top-color: var(--green); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 20px; }
  @keyframes spin { to{transform:rotate(360deg)} }
  .loading-text { color: var(--muted); font-size: 14px; }
  .loading-sub { color: #3a4a5a; font-size: 12px; margin-top: 8px; font-family:'DM Mono',monospace; }
  .btn-outline { width: 100%; padding: 14px; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; background: transparent; color: var(--muted); font-family:'Sora',sans-serif; font-size: 14px; cursor: pointer; transition: all 0.2s; margin-top: 6px; }
  .btn-outline:hover { border-color: rgba(255,255,255,0.2); color: var(--text); }
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div class="badge"><div class="badge-dot"></div><span>AI POWERED</span></div>
    <h1>Resume Analyzer</h1>
    <p class="subtitle">Match your resume to any job description — get scored, improved & ATS-ready</p>
    <div class="free-badge">⚡ 100% FREE · Powered by Groq AI</div>
  </div>

  <div id="form-section">
    <div class="grid2">
      <div class="card">
        <div class="section-label">📄 Upload Resume</div>
        <div class="upload-zone" id="dropzone" onclick="document.getElementById('file-input').click()">
          <input type="file" id="file-input" accept=".pdf,.txt" style="display:none" onchange="handleFile(this.files[0])"/>
          <div id="upload-content">
            <div class="upload-icon">📁</div>
            <div class="upload-main">Drop your resume here</div>
            <div class="upload-sub">PDF or TXT &nbsp;·&nbsp; Click to browse</div>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="section-label">💼 Job Description</div>
        <textarea id="job-desc" placeholder="Paste the full job description here...&#10;&#10;e.g. We're looking for a Senior React Developer with 3+ years of experience in..."></textarea>
        <div class="char-count" id="char-count">0 characters</div>
      </div>
    </div>
    <div id="error-box" class="error-box" style="display:none;margin-top:16px;"></div>
    <button class="btn" onclick="analyze()" style="margin-top:16px;">✨ Analyze Resume — It's Free!</button>
  </div>

  <div id="loading-section" style="display:none">
    <div class="loading">
      <div class="spinner"></div>
      <div class="loading-text">Analyzing your resume with Groq AI...</div>
      <div class="loading-sub">Usually takes 5–10 seconds</div>
    </div>
  </div>

  <div id="results-section" style="display:none" class="results">
    <div class="results-top">
      <div class="card score-wrap" id="score-card"></div>
      <div class="card" id="summary-card"></div>
    </div>
    <div class="results-mid">
      <div class="card" id="keywords-card"></div>
      <div class="card" id="ats-card"></div>
    </div>
    <div class="card" id="improvements-card" style="margin-bottom:18px;"></div>
    <div class="card" id="rewrite-card" style="margin-bottom:20px;"></div>
    <button class="btn-outline" onclick="reset()">🔄 Analyze Another Resume</button>
  </div>
</div>

<script>
  let selectedFile = null;
  const dz = document.getElementById('dropzone');
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('drag'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('drag'));
  dz.addEventListener('drop', e => { e.preventDefault(); dz.classList.remove('drag'); handleFile(e.dataTransfer.files[0]); });
  document.getElementById('job-desc').addEventListener('input', function() {
    document.getElementById('char-count').textContent = this.value.length + ' characters';
  });
  function handleFile(file) {
    if (!file) return;
    if (!file.name.match(/\\.(pdf|txt)$/i)) { showError('Please upload a PDF or TXT file.'); return; }
    selectedFile = file;
    document.getElementById('upload-content').innerHTML = `
      <div class="upload-icon">✅</div>
      <div class="file-name">${file.name}</div>
      <div class="upload-sub">${(file.size/1024).toFixed(1)} KB · Click to change</div>`;
    dz.classList.add('has-file'); hideError();
  }
  function showError(msg) { const e = document.getElementById('error-box'); e.textContent = msg; e.style.display = 'block'; }
  function hideError() { document.getElementById('error-box').style.display = 'none'; }
  async function analyze() {
    const jobDesc = document.getElementById('job-desc').value.trim();
    if (!selectedFile) { showError('Please upload a resume file.'); return; }
    if (!jobDesc) { showError('Please enter a job description.'); return; }
    hideError();
    document.getElementById('form-section').style.display = 'none';
    document.getElementById('loading-section').style.display = 'block';
    const fd = new FormData();
    fd.append('resume', selectedFile);
    fd.append('job_description', jobDesc);
    try {
      const res = await fetch('/analyze', { method: 'POST', body: fd });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      renderResults(data);
    } catch(e) {
      document.getElementById('loading-section').style.display = 'none';
      document.getElementById('form-section').style.display = 'block';
      showError('Analysis failed: ' + e.message);
    }
  }
  function getColor(s) { return s >= 75 ? '#00f5a0' : s >= 50 ? '#ffd166' : '#ff5e7a'; }
  function renderResults(d) {
    document.getElementById('loading-section').style.display = 'none';
    const color = getColor(d.match_score);
    const verdict = d.match_score >= 75 ? '🚀 Strong Match' : d.match_score >= 50 ? '⚡ Good Potential' : '🔧 Needs Work';
    const r = 58, circ = 2 * Math.PI * r, offset = circ - (d.match_score / 100) * circ;
    document.getElementById('score-card').innerHTML = `
      <div class="section-label" style="text-align:center">Match Score</div>
      <div class="score-ring-container">
        <svg width="150" height="150" viewBox="0 0 150 150">
          <circle cx="75" cy="75" r="${r}" fill="none" stroke="#1a2035" stroke-width="13"/>
          <circle cx="75" cy="75" r="${r}" fill="none" stroke="${color}" stroke-width="13"
            stroke-dasharray="${circ}" stroke-dashoffset="${offset}" stroke-linecap="round"
            style="transition:stroke-dashoffset 1.5s ease"/>
        </svg>
        <div class="score-center">
          <div class="score-num" style="color:${color}">${d.match_score}</div>
          <div class="score-lbl">SCORE</div>
        </div>
      </div>
      <div class="score-verdict" style="color:${color};text-align:center">${verdict}</div>`;
    document.getElementById('summary-card').innerHTML = `
      <div class="section-label">📋 Assessment</div>
      <p style="color:#b0bdd0;font-size:14px;line-height:1.7;margin-bottom:18px">${d.summary}</p>
      <div class="section-label">💪 Strengths</div>
      <ul class="check-list">${(d.strengths||[]).map(s=>`<li>${s}</li>`).join('')}</ul>`;
    document.getElementById('keywords-card').innerHTML = `
      <div class="section-label">🔍 Missing Keywords</div>
      <div>${(d.missing_keywords||[]).map(k=>`<span class="tag tag-red">${k}</span>`).join('')}</div>
      <p style="color:var(--muted);font-size:12px;margin-top:14px">Add these to boost your ATS score</p>`;
    document.getElementById('ats-card').innerHTML = `
      <div class="section-label">🤖 ATS Optimization Tips</div>
      <ul class="check-list">${(d.ats_tips||[]).map(t=>`<li>${t}</li>`).join('')}</ul>`;
    document.getElementById('improvements-card').innerHTML = `
      <div class="section-label">🛠 Suggested Improvements</div>
      <div class="improve-grid">${(d.improvements||[]).map(i=>`
        <div class="improve-item">
          <div class="improve-section">${(i.section||'').toUpperCase()}</div>
          <div class="improve-text">${i.suggestion}</div>
        </div>`).join('')}</div>`;
    document.getElementById('rewrite-card').innerHTML = `
      <div class="section-label">✍️ AI-Rewritten Professional Summary</div>
      <div class="rewrite-box">${d.rewritten_summary}</div>`;
    document.getElementById('results-section').style.display = 'block';
  }
  function reset() {
    selectedFile = null;
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('form-section').style.display = 'block';
    document.getElementById('job-desc').value = '';
    document.getElementById('char-count').textContent = '0 characters';
    document.getElementById('upload-content').innerHTML = `
      <div class="upload-icon">📁</div>
      <div class="upload-main">Drop your resume here</div>
      <div class="upload-sub">PDF or TXT &nbsp;·&nbsp; Click to browse</div>`;
    dz.classList.remove('has-file');
  }
</script>
</body>
</html>"""

# ─── API ROUTES ───────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML

@app.post("/analyze")
async def analyze(resume: UploadFile = File(...), job_description: str = Form(...)):
    try:
        data = await resume.read()
        if resume.filename.lower().endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                resume_text = "".join(p.extract_text() or "" for p in pdf.pages)
        else:
            resume_text = data.decode("utf-8", errors="ignore")

        prompt = f"""You are an expert ATS specialist and career coach.
Analyze this resume against the job description. Return ONLY valid JSON — no markdown, no extra text.

RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
{job_description[:2000]}

Return exactly this JSON:
{{
  "match_score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "missing_keywords": ["<kw1>", "<kw2>", "<kw3>", "<kw4>", "<kw5>"],
  "improvements": [
    {{"section": "<section name>", "suggestion": "<specific actionable suggestion>"}},
    {{"section": "<section name>", "suggestion": "<specific actionable suggestion>"}},
    {{"section": "<section name>", "suggestion": "<specific actionable suggestion>"}}
  ],
  "ats_tips": ["<tip 1>", "<tip 2>", "<tip 3>"],
  "rewritten_summary": "<Optimized professional summary for this role>"
}}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3,
        )
        text = re.sub(r"```json|```", "", response.choices[0].message.content).strip()
        return JSONResponse(json.loads(text))

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ─── START ────────────────────────────────────────────
def open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://localhost:{PORT}")

if __name__ == "__main__":
    print("\n" + "="*52)
    print("  AI Resume Analyzer  (Groq - FREE)")
    print(f"  -->  http://localhost:{PORT}")
    print("="*52 + "\n")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=PORT)