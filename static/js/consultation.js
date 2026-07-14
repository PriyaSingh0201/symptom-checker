// static/js/consultation.js – Phase 3 Smart Consultation JS
'use strict';

const token = localStorage.getItem('token') || localStorage.getItem('jwt_token');
let consultationId = null;
let questionNumber = 0;
let conversationLog = []; // { role, content, timestamp }
let finalResult = null;

// ── DOM refs ──────────────────────────────────────────────────────────────────
const formSection = document.getElementById('consult-form-section');
const chatSection = document.getElementById('consult-chat-section');
const resultSection = document.getElementById('consult-result-section');
const chatWindow = document.getElementById('consult-chat-window');
const answerInput = document.getElementById('consult-answer-input');
const sendBtn = document.getElementById('consult-send-btn');
const progressBar = document.getElementById('consult-progress-bar');
const progressText = document.getElementById('consult-progress-text');
const finalizingDiv = document.getElementById('consult-finalizing');
const inputArea = document.getElementById('consult-input-area');
const emergencyBanner = document.getElementById('triage-emergency-banner');
const emergencyText = document.getElementById('triage-emergency-text');

// ── Pain slider ───────────────────────────────────────────────────────────────
const painSlider = document.getElementById('consult-pain');
const painVal = document.getElementById('consult-pain-val');
if (painSlider) painSlider.addEventListener('input', () => { painVal.textContent = painSlider.value; });

// ── Start consultation ────────────────────────────────────────────────────────
document.getElementById('consult-start-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Starting consultation...';

  const payload = {
    symptoms: document.getElementById('consult-symptoms').value.trim(),
    age: document.getElementById('consult-age').value,
    gender: document.getElementById('consult-gender').value,
    duration: document.getElementById('consult-duration').value,
    pain_level: document.getElementById('consult-pain').value,
    medical_conditions: document.getElementById('consult-conditions').value,
    medications: document.getElementById('consult-medications').value,
    allergies: document.getElementById('consult-allergies').value,
  };

  try {
    const res = await fetch('/api/consultation/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.emergency) {
      showEmergency(data.emergency_message || data.message);
      btn.disabled = false;
      btn.textContent = 'Start AI Consultation';
      return;
    }

    if (data.error) {
      alert(data.error);
      btn.disabled = false;
      btn.textContent = 'Start AI Consultation';
      return;
    }

    consultationId = data.consultation_id;
    questionNumber = 1;

    // Switch to chat view
    formSection.classList.add('hidden');
    chatSection.classList.remove('hidden');

    // Add initial symptom message from user context
    appendMessage('user', payload.symptoms);
    appendMessage('ai', data.question);
    conversationLog.push({ role: 'assistant', content: data.question });

    updateProgress(1);
    answerInput.focus();
  } catch (err) {
    alert('Failed to start consultation. Please try again.');
    btn.disabled = false;
    btn.textContent = 'Start AI Consultation';
  }
});

// ── Send answer ───────────────────────────────────────────────────────────────
sendBtn.addEventListener('click', sendAnswer);
answerInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendAnswer(); });

// Quick answer chips
document.querySelectorAll('.consult-quick-answers .chat-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    answerInput.value = chip.dataset.val;
    sendAnswer();
  });
});

async function sendAnswer() {
  const answer = answerInput.value.trim();
  if (!answer || !consultationId) return;

  answerInput.value = '';
  sendBtn.disabled = true;
  appendMessage('user', answer);
  conversationLog.push({ role: 'user', content: answer });

  // Show typing indicator
  const typingId = showTyping();

  try {
    const res = await fetch('/api/consultation/reply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify({ consultation_id: consultationId, answer })
    });
    const data = await res.json();
    removeTyping(typingId);

    if (data.emergency) {
      showEmergency(data.emergency_message);
      inputArea.classList.add('hidden');
      return;
    }

    if (data.done) {
      // Finalize
      inputArea.classList.add('hidden');
      finalizingDiv.classList.remove('hidden');
      await finalizeConsultation();
    } else {
      appendMessage('ai', data.question);
      conversationLog.push({ role: 'assistant', content: data.question });
      questionNumber = data.question_number || questionNumber + 1;
      updateProgress(questionNumber);
      sendBtn.disabled = false;
      answerInput.focus();
    }
  } catch (err) {
    removeTyping(typingId);
    appendMessage('ai', 'Sorry, there was an error. Please try again.');
    sendBtn.disabled = false;
  }
}

// ── Finalize ──────────────────────────────────────────────────────────────────
async function finalizeConsultation() {
  try {
    const res = await fetch('/api/consultation/finalize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
      body: JSON.stringify({ consultation_id: consultationId })
    });
    const data = await res.json();
    finalResult = data;

    finalizingDiv.classList.add('hidden');
    chatSection.classList.add('hidden');
    resultSection.classList.remove('hidden');

    renderResults(data);
  } catch (err) {
    finalizingDiv.classList.add('hidden');
    alert('Failed to generate assessment. Please try again.');
  }
}

// ── Render results ────────────────────────────────────────────────────────────
function renderResults(data) {
  if (data.emergency_flag) {
    showEmergency(data.emergency_message);
  }

  const top = (data.top5_conditions || [])[0] || {};
  const condition = data.possible_condition || top.condition || 'Assessment Complete';
  const severity = data.severity || top.severity || 'Moderate';
  const confidence = data.confidence_score || top.probability || 0;

  document.getElementById('consult-primary-condition').textContent = condition;
  document.getElementById('consult-confidence-val').textContent = Math.round(confidence) + '%';
  document.getElementById('consult-summary').textContent = data.summary || data.explanation || '';
  document.getElementById('consult-timeline-summary').textContent = `${conversationLog.filter(m => m.role === 'assistant').length} questions asked • ${conversationLog.filter(m => m.role === 'user').length} answers recorded`;
  document.getElementById('consult-findings').textContent = (data.top5_conditions || []).slice(0, 2).map(c => c.condition).join(' • ') || 'Clinical review pending';
  document.getElementById('consult-evidence-count').textContent = (data.evidence_sources || []).length;

  // Severity badge
  const badge = document.getElementById('consult-severity-badge');
  badge.textContent = severity;
  badge.className = 'severity-badge ' + severity.toLowerCase();

  // Confidence bar
  document.getElementById('consult-conf-bar').style.width = confidence + '%';
  document.getElementById('consult-conf-pct').textContent = Math.round(confidence) + '%';

  // Specialist
  document.getElementById('consult-specialist-name').textContent = data.recommended_specialist || data.recommended_doctor || '—';
  document.getElementById('consult-specialist-reason').textContent = data.specialist_reason || '';

  // Appointment link with specialist pre-filled
  const apptLink = document.querySelector('#consult-specialist-card a');
  if (apptLink && data.recommended_specialist) {
    apptLink.href = '/appointment?specialist=' + encodeURIComponent(data.recommended_specialist);
  }

  // Top 5 conditions
  renderTop5(data.top5_conditions || []);

  // Q&A Timeline
  renderQATimeline();

  // Evidence
  renderEvidence(data.evidence_sources || []);
}

function renderTop5(conditions) {
  const list = document.getElementById('consult-top5-list');
  if (!conditions.length) { list.innerHTML = '<p style="color:var(--muted);">No conditions data.</p>'; return; }

  list.innerHTML = conditions.map((c, i) => `
    <div class="top5-condition-card">
      <div class="top5-header">
        <div class="top5-rank">#${i + 1}</div>
        <div class="top5-name">${c.condition}</div>
        <span class="severity-badge ${(c.severity || 'moderate').toLowerCase()}">${c.severity || 'Moderate'}</span>
        <div class="top5-prob">${Math.round(c.probability || 0)}%</div>
      </div>
      <div class="progress" style="height:6px;margin:0.5rem 0;">
        <div class="progress-bar" style="width:${c.probability || 0}%;"></div>
      </div>
      <p style="font-size:0.85rem;color:var(--muted);margin:0.4rem 0;">${c.reasoning || ''}</p>
      ${c.matching_symptoms ? `<div style="font-size:0.78rem;margin-top:0.4rem;"><strong>Matching:</strong> <span style="color:var(--primary);">${c.matching_symptoms}</span></div>` : ''}
      ${c.missing_symptoms ? `<div style="font-size:0.78rem;margin-top:0.2rem;"><strong>Missing:</strong> <span style="color:var(--muted);">${c.missing_symptoms}</span></div>` : ''}
      ${c.home_care ? `<div class="advice-box" style="margin-top:0.75rem;font-size:0.82rem;white-space:pre-wrap;">${c.home_care}</div>` : ''}
    </div>
  `).join('');
}

function renderQATimeline() {
  const container = document.getElementById('consult-qa-timeline');
  const qaItems = conversationLog.filter(m => m.role === 'assistant' || m.role === 'user');
  if (!qaItems.length) { container.innerHTML = '<p style="color:var(--muted);">No Q&A recorded.</p>'; return; }

  let html = '';
  for (let i = 0; i < qaItems.length; i += 2) {
    const q = qaItems[i];
    const a = qaItems[i + 1];
    if (!q) continue;
    html += `
      <div class="timeline-item">
        <div class="timeline-marker"></div>
        <div class="timeline-content">
          <p class="timeline-q">🩺 ${q.content}</p>
          ${a ? `<p class="timeline-a">👤 ${a.content}</p>` : ''}
        </div>
      </div>`;
  }
  container.innerHTML = html;
}

function renderEvidence(sources) {
  const grid = document.getElementById('consult-evidence-list');
  const validSources = (sources || []).filter(s => s && s.source !== 'System');
  if (!validSources.length) {
    grid.innerHTML = '<p style="color:var(--muted);font-size:0.85rem;">Limited external evidence retrieved. Assessment based on clinical reasoning.</p>';
    return;
  }
  grid.innerHTML = validSources.map(s => `
    <div class="evidence-card">
      <div class="evidence-card-header">
        <span class="evidence-source-badge">${s.source}</span>
        ${s.url ? `<a href="${s.url}" target="_blank" rel="noopener" class="evidence-link">View Source ↗</a>` : ''}
      </div>
      <p style="font-size:0.82rem;font-weight:600;margin:0.4rem 0 0.25rem;">${s.title}</p>
      <p style="font-size:0.78rem;color:var(--muted);margin:0;line-height:1.5;">${s.summary}</p>
    </div>
  `).join('');
}

// ── Chat helpers ──────────────────────────────────────────────────────────────
function appendMessage(role, content) {
  const div = document.createElement('div');
  div.className = `chat-msg ${role === 'user' ? 'user' : 'ai'}`;
  div.innerHTML = `
    <div class="chat-bubble">${escapeHtml(content)}</div>
    <div class="chat-meta"><span class="chat-time">${getTime()}</span></div>`;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTyping() {
  const id = 'typing-' + Date.now();
  const div = document.createElement('div');
  div.className = 'chat-msg ai';
  div.id = id;
  div.innerHTML = `<div class="chat-typing"><span></span><span></span><span></span></div>`;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function updateProgress(qNum) {
  const pct = Math.min(Math.round((qNum / 6) * 100), 95);
  progressBar.style.width = pct + '%';
  progressText.textContent = `Question ${qNum} of ~6`;
}

function showEmergency(msg) {
  emergencyBanner.classList.remove('hidden');
  emergencyText.textContent = msg || 'Your symptoms indicate a potential medical emergency. Please seek immediate care.';
  emergencyBanner.scrollIntoView({ behavior: 'smooth' });
}

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function getTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ── PDF Download ──────────────────────────────────────────────────────────────
document.getElementById('consult-download-btn').addEventListener('click', () => {
  if (consultationId) {
    const link = document.createElement('a');
    link.href = '/api/download-pdf/' + consultationId;
    link.target = '_blank';
    link.rel = 'noopener';
    link.click();
  }
});

// ── New Consultation ──────────────────────────────────────────────────────────
document.getElementById('consult-new-btn').addEventListener('click', () => {
  consultationId = null;
  questionNumber = 0;
  conversationLog = [];
  finalResult = null;
  chatWindow.innerHTML = '';
  answerInput.value = '';
  emergencyBanner.classList.add('hidden');
  resultSection.classList.add('hidden');
  chatSection.classList.add('hidden');
  inputArea.classList.remove('hidden');
  finalizingDiv.classList.add('hidden');
  formSection.classList.remove('hidden');
  progressBar.style.width = '16%';
  document.getElementById('consult-start-form').reset();
  painVal.textContent = '5';
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ── Voice Input (Start Form) ──────────────────────────────────────────────────
const voiceBtn = document.getElementById('consult-voice-btn');
const voiceStatus = document.getElementById('consult-voice-status');
let voiceRecognition = null;
let isListening = false;

if (voiceBtn) {
  voiceBtn.addEventListener('click', () => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      voiceStatus.textContent = 'Voice not supported in this browser.';
      return;
    }
    if (isListening) {
      voiceRecognition && voiceRecognition.stop();
      return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    voiceRecognition = new SR();
    voiceRecognition.lang = document.documentElement.lang === 'hi' ? 'hi-IN' : 'en-US';
    voiceRecognition.interimResults = false;
    voiceRecognition.maxAlternatives = 1;

    voiceRecognition.onstart = () => {
      isListening = true;
      voiceBtn.textContent = '🔴 Listening...';
      voiceStatus.textContent = 'Speak now...';
    };
    voiceRecognition.onresult = (e) => {
      document.getElementById('consult-symptoms').value = e.results[0][0].transcript;
      voiceStatus.textContent = 'Voice captured!';
    };
    voiceRecognition.onerror = (e) => {
      voiceStatus.textContent = 'Error: ' + e.error;
    };
    voiceRecognition.onend = () => {
      isListening = false;
      voiceBtn.textContent = '🎙️ Voice Input';
    };
    voiceRecognition.start();
  });
}

// ── Voice Answer (Chat) ───────────────────────────────────────────────────────
const voiceAnswerBtn = document.getElementById('consult-voice-answer-btn');
let isAnswerListening = false;
let answerRecognition = null;

if (voiceAnswerBtn) {
  voiceAnswerBtn.addEventListener('click', () => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert('Voice not supported in this browser.');
      return;
    }
    if (isAnswerListening) {
      answerRecognition && answerRecognition.stop();
      return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    answerRecognition = new SR();
    answerRecognition.lang = document.documentElement.lang === 'hi' ? 'hi-IN' : 'en-US';
    answerRecognition.interimResults = false;

    answerRecognition.onstart = () => {
      isAnswerListening = true;
      voiceAnswerBtn.textContent = '🔴';
    };
    answerRecognition.onresult = (e) => {
      answerInput.value = e.results[0][0].transcript;
    };
    answerRecognition.onerror = () => {};
    answerRecognition.onend = () => {
      isAnswerListening = false;
      voiceAnswerBtn.textContent = '🎙️';
    };
    answerRecognition.start();
  });
}
