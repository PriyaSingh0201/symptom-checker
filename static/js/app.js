// static/js/app.js – Phase 1+2+3 Main Application JS
'use strict';

// ── Token helper (supports both key names) ────────────────────────────────────
function getToken() {
  return localStorage.getItem('token') || localStorage.getItem('jwt_token') || '';
}

// ── i18n translations ─────────────────────────────────────────────────────────
const translations = {
  en: {
    dashboard: 'Dashboard', checker: 'Checker', history: 'History',
    profile: 'Profile', logout: 'Logout',
    footer: '© 2026 Symptom Checker • Secure, modern symptom guidance',
    welcomeBack: 'Welcome back',
    loginIntro: 'Sign in to continue your health journey with AI-guided insights.',
    login: 'Login', newHere: 'New here?', createAccount: 'Create an account',
    createAccountTitle: 'Create your account',
    registerIntro: 'Register to start tracking symptoms and receive smart guidance.',
    createAccountButton: 'Create account', haveAccount: 'Already have an account?',
    loginLink: 'Login',
    consultTitle: 'Smart Medical Consultation',
    consultIntro: 'Describe your symptoms and the AI will conduct a real consultation — asking one question at a time — before generating an evidence-based diagnosis.',
    consultStartButton: 'Start AI Consultation',
    consultVoiceButton: 'Voice Input', consultSendButton: 'Send',
    consultDownloadButton: 'Download PDF Report',
    consultNewButton: 'Start New Consultation',
    consultAnswerPlaceholder: 'Type your answer...',
    timelineTitle: 'Health Timeline', appointmentTitle: 'Book an Appointment',
  },
  hi: {
    dashboard: 'डैशबोर्ड', checker: 'जाँच', history: 'इतिहास',
    profile: 'प्रोफ़ाइल', logout: 'लॉगआउट',
    footer: '© 2026 एआई सिंप्टम चेकर • सुरक्षित, आधुनिक लक्षण मार्गदर्शन',
    welcomeBack: 'वापसी पर स्वागत है',
    loginIntro: 'एआई-निर्देशित अंतर्दृष्टि के साथ अपने स्वास्थ्य सफ़र को जारी रखने के लिए साइन इन करें।',
    login: 'लॉगिन', newHere: 'यहाँ नए हैं?', createAccount: 'खाता बनाएं',
    createAccountTitle: 'अपना खाता बनाएं',
    registerIntro: 'लक्षणों को ट्रैक करना और स्मार्ट मार्गदर्शन प्राप्त करना शुरू करने के लिए रजिस्टर करें।',
    createAccountButton: 'खाता बनाएं', haveAccount: 'पहले से खाता है?',
    loginLink: 'लॉगिन',
    consultTitle: 'स्मार्ट मेडिकल परामर्श',
    consultIntro: 'अपने लक्षणों का वर्णन करें और एआई एक वास्तविक परामर्श करेगा — एक-एक प्रश्न पूछकर — उसके बाद सबूत-आधारित निदान बनाएगा।',
    consultStartButton: 'एआई परामर्श शुरू करें',
    consultVoiceButton: 'वॉइस इनपुट', consultSendButton: 'भेजें',
    consultDownloadButton: 'PDF रिपोर्ट डाउनलोड करें',
    consultNewButton: 'नया परामर्श शुरू करें',
    consultAnswerPlaceholder: 'अपना उत्तर टाइप करें...',
    timelineTitle: 'स्वास्थ्य टाइमलाइन', appointmentTitle: 'अपॉइंटमेंट बुक करें',
  },
};

function applyTranslations(lang) {
  document.documentElement.setAttribute('lang', lang);
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    if (translations[lang] && translations[lang][key]) el.textContent = translations[lang][key];
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (translations[lang] && translations[lang][key]) el.setAttribute('placeholder', translations[lang][key]);
  });
}

// ── DOMContentLoaded ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('theme-toggle');
  const logoutBtn   = document.getElementById('logout-btn');
  const langToggle  = document.getElementById('lang-toggle');

  // Language toggle
  if (langToggle) {
    const savedLang = localStorage.getItem('lang') || 'en';
    langToggle.textContent = savedLang === 'en' ? 'हिंदी' : 'EN';
    applyTranslations(savedLang);
    langToggle.addEventListener('click', () => {
      const cur  = localStorage.getItem('lang') || 'en';
      const next = cur === 'en' ? 'hi' : 'en';
      localStorage.setItem('lang', next);
      langToggle.textContent = next === 'en' ? 'हिंदी' : 'EN';
      applyTranslations(next);
    });
  }

  // Theme toggle
  if (themeToggle) {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    themeToggle.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    themeToggle.addEventListener('click', () => {
      const cur  = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', cur);
      localStorage.setItem('theme', cur);
      themeToggle.textContent = cur === 'dark' ? '☀️' : '🌙';
    });
  }

  // Logout
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      const tok = getToken();
      if (tok) {
        try {
          await fetch('/api/logout', { method: 'POST', headers: { Authorization: `Bearer ${tok}` } });
        } catch (_) {}
      }
      localStorage.removeItem('token');
      localStorage.removeItem('jwt_token');
      document.cookie = 'token=; Max-Age=-1; path=/';
      window.location.href = '/login';
    });
  }

  // ── Symptom Checker Form (Phase 1 + 2) ─────────────────────────────────────
  const symptomForm = document.getElementById('symptom-form');
  if (!symptomForm) return;

  const message      = document.getElementById('analysis-message');
  const resultCard   = document.getElementById('result-card');
  const severityBadge = document.getElementById('severity-badge');
  const voiceBtn     = document.getElementById('voice-btn');
  const symptomsInput = document.querySelector('textarea[name="primary_symptom"]');
  const chatCard     = document.getElementById('chat-card');
  const chatAnswer   = document.getElementById('chat-answer');

  // Pain slider
  const painSlider = document.getElementById('pain-slider');
  const painVal    = document.getElementById('pain-val');
  if (painSlider && painVal) {
    painSlider.addEventListener('input', () => { painVal.textContent = painSlider.value; });
  }

  // Gender → pregnancy toggle
  const genderSelect    = document.getElementById('gender-select');
  const pregnancyGroup  = document.getElementById('pregnancy-group');
  if (genderSelect && pregnancyGroup) {
    genderSelect.addEventListener('change', () => {
      if (genderSelect.value === 'Female') {
        pregnancyGroup.classList.remove('hidden');
      } else {
        pregnancyGroup.classList.add('hidden');
        const sel = pregnancyGroup.querySelector('select');
        if (sel) sel.value = 'Not Pregnant';
      }
    });
  }

  // Reopen consultation from history
  const reopenId = localStorage.getItem('reopen_assessment_id');
  if (reopenId) {
    localStorage.removeItem('reopen_assessment_id');
    if (message) message.textContent = 'Loading previous consultation...';
    fetch(`/api/history/${reopenId}`, { headers: { Authorization: `Bearer ${getToken()}` } })
      .then(r => r.json())
      .then(data => {
        if (data && !data.error) {
          updateUI(data);
          if (message) message.textContent = 'Consultation resumed.';
        } else {
          if (message) message.textContent = 'Failed to load consultation.';
        }
      })
      .catch(() => { if (message) message.textContent = 'Error resuming consultation.'; });
  }

  // ── renderFollowups ─────────────────────────────────────────────────────────
  function renderFollowups(questions, assessmentId, responses = {}) {
    const followupContainer = document.getElementById('followup-container');
    const followupQuestions = document.getElementById('followup-questions');
    if (!followupContainer || !followupQuestions) return;

    if (questions && questions.length) {
      followupQuestions.innerHTML = questions.map(q => `
        <div class="followup-question-item">
          <p class="followup-question-text">${q}</p>
          <div class="followup-actions">
            <button class="primary-btn followup-yes" data-q="${q}" type="button">Yes</button>
            <button class="secondary-btn followup-no" data-q="${q}" type="button">No</button>
          </div>
        </div>`).join('');
      followupContainer.classList.remove('hidden');

      followupQuestions.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', async () => {
          const answer   = btn.classList.contains('followup-yes') ? 'Yes' : 'No';
          const question = btn.getAttribute('data-q');
          btn.disabled   = true;
          const res = await fetch('/api/followup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
            body: JSON.stringify({ answer, question, assessment_id: assessmentId })
          });
          const updateData = await res.json();
          if (res.ok) updateUI(updateData);
        });
      });
    } else {
      followupContainer.classList.add('hidden');
    }
    renderTimeline(responses);
  }

  // ── renderTimeline ──────────────────────────────────────────────────────────
  function renderTimeline(responses) {
    const timelineWrapper = document.getElementById('timeline-wrapper');
    const timeline        = document.getElementById('consultation-timeline');
    if (!timelineWrapper || !timeline) return;
    const keys = Object.keys(responses || {});
    if (keys.length) {
      timelineWrapper.classList.remove('hidden');
      timeline.innerHTML = keys.map(q => `
        <div class="timeline-item">
          <div class="timeline-marker"></div>
          <div class="timeline-content">
            <p class="timeline-q"><strong>Q:</strong> ${q}</p>
            <p class="timeline-a"><strong>A:</strong> ${responses[q]}</p>
          </div>
        </div>`).join('');
    } else {
      timelineWrapper.classList.add('hidden');
    }
  }

  // ── updateUI ────────────────────────────────────────────────────────────────
  function updateUI(data) {
    const assessmentId = data.assessment_id || data.id;

    document.getElementById('condition-name').textContent = data.possible_condition || '—';
    severityBadge.textContent  = data.severity || 'Moderate';
    severityBadge.className    = `severity-badge ${(data.severity || 'moderate').toLowerCase()}`;
    document.getElementById('explanation').textContent = data.explanation || '';
    document.getElementById('doctor').textContent      = data.recommended_doctor || '';
    document.getElementById('advice').textContent      = data.health_advice || '';

    // Confidence bar
    const confidenceBar  = document.getElementById('confidence-bar');
    const confidenceText = document.getElementById('confidence-text');
    if (confidenceBar && confidenceText) {
      const val = data.confidence_score || 0;
      confidenceBar.style.width  = `${val}%`;
      confidenceText.textContent = `${val}%`;
    }

    // Emergency banner
    const emergBanner = document.getElementById('emergency-banner');
    const emergText   = document.getElementById('emergency-text');
    if (emergBanner && emergText) {
      if (data.emergency_flag) {
        emergBanner.classList.remove('hidden');
        emergText.textContent = data.emergency_message || 'Life-threatening indications detected. Seek immediate emergency care.';
      } else {
        emergBanner.classList.add('hidden');
      }
    }

    // Top conditions list
    const topCondsList = document.getElementById('top-conditions-list');
    if (topCondsList && data.top_conditions && data.top_conditions.length) {
      topCondsList.innerHTML = data.top_conditions.map(c => `
        <div class="extra-condition-card">
          <div class="extra-condition-header">
            <strong>${c.condition} (${c.confidence}%)</strong>
            <span class="severity-badge ${(c.severity || 'moderate').toLowerCase()}">${c.severity}</span>
          </div>
          <p style="margin:0.4rem 0 0.25rem;font-size:0.9rem;">${c.explanation}</p>
          <p style="font-size:0.85rem;margin:0.2rem 0;"><strong>Specialist:</strong> ${c.recommended_department}</p>
          <p style="font-size:0.85rem;margin:0.2rem 0;color:var(--muted);"><strong>Supporting Symptoms:</strong> ${c.supporting_symptoms}</p>
          ${c.home_care_advice ? `
          <details style="margin-top:0.5rem;">
            <summary style="cursor:pointer;font-size:0.85rem;color:var(--primary);">View Home Care Advice</summary>
            <div class="advice-box" style="margin-top:0.5rem;white-space:pre-line;">${c.home_care_advice}</div>
          </details>` : ''}
        </div>`).join('');
    }

    // Evidence sources
    const evidenceList = document.getElementById('evidence-list');
    const evidenceBox  = document.getElementById('evidence-box');
    if (evidenceList && data.evidence_sources && data.evidence_sources.length) {
      evidenceList.innerHTML = data.evidence_sources.map(ev => `
        <div class="evidence-card">
          <div class="evidence-card-header">
            <span class="evidence-source-badge">${ev.source}</span>
            ${ev.url ? `<a href="${ev.url}" target="_blank" class="evidence-link">Reference ↗</a>` : ''}
          </div>
          <h4 style="margin:0.5rem 0 0.25rem;font-size:0.9rem;font-weight:600;">${ev.title}</h4>
          <p style="margin:0;font-size:0.75rem;color:var(--muted);line-height:1.4;">${ev.summary}</p>
        </div>`).join('');
      if (evidenceBox) evidenceBox.classList.remove('hidden');
    } else {
      if (evidenceBox) evidenceBox.classList.add('hidden');
    }

    renderFollowups(data.followup_questions, assessmentId, data.followup_responses || {});

    resultCard.classList.remove('hidden');
    if (chatCard)   chatCard.classList.add('hidden');
    if (chatAnswer) chatAnswer.innerHTML = '';

    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
      downloadBtn.onclick = () => {
        const link = document.createElement('a');
        link.href   = `/api/download-pdf/${assessmentId}`;
        link.target = '_blank';
        link.rel    = 'noopener';
        link.click();
      };
    }
  }

  // ── Form submit ─────────────────────────────────────────────────────────────
  symptomForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(symptomForm);
    const payload  = Object.fromEntries(formData.entries());

    // Multi-select secondary symptoms
    payload.secondary_symptoms = Array.from(
      symptomForm.querySelectorAll('input[name="secondary_symptoms"]:checked')
    ).map(el => el.value);

    if (message) message.textContent = 'Running clinical reasoning analysis...';

    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok) {
      if (message) message.textContent = data.error || 'Analysis failed';
      return;
    }

    updateUI(data);
    if (message) message.textContent = data.message || 'Analysis complete';
    const currentAssessmentId = data.assessment_id || data.id;

    const chatBtn = document.getElementById('chat-btn');
    if (chatBtn) chatBtn.onclick = () => chatCard && chatCard.classList.toggle('hidden');

    const chatSubmit = document.getElementById('chat-submit');
    if (chatSubmit) {
      chatSubmit.onclick = async () => {
        const question = document.getElementById('chat-question').value.trim();
        if (!question) return;
        const chatResponse = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
          body: JSON.stringify({ question, assessment_id: currentAssessmentId }),
        });
        const chatData = await chatResponse.json();
        if (chatData.updated) {
          if (chatAnswer) chatAnswer.innerHTML = `<p class="updated-notice">📝 ${chatData.answer}</p>`;
          updateUI(chatData.assessment);
        } else {
          if (chatAnswer) chatAnswer.innerHTML = `<p>${chatData.answer}</p>`;
        }
        document.getElementById('chat-question').value = '';
      };
    }
  });

  // ── Voice input ─────────────────────────────────────────────────────────────
  if (voiceBtn && symptomsInput) {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const isSecure = location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1';

    if (!SR || !isSecure) {
      voiceBtn.disabled    = true;
      voiceBtn.textContent = '🎙️ Voice unavailable';
    } else {
      let isListening = false;

      voiceBtn.addEventListener('click', () => {
        if (isListening) return;
        const recognition        = new SR();
        recognition.lang         = 'en-US';
        recognition.continuous   = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
          isListening          = true;
          voiceBtn.textContent = '🔴 Listening...';
          voiceBtn.disabled    = true;
          if (message) message.textContent = 'Describe your symptoms now.';
        };
        recognition.onresult = (e) => {
          const t = Array.from(e.results).map(r => r[0].transcript).join(' ');
          symptomsInput.value = symptomsInput.value ? `${symptomsInput.value}, ${t}` : t;
          if (message) message.textContent = 'Voice input added.';
        };
        recognition.onerror = (e) => {
          if (message) message.textContent = `Voice error: ${e.error}`;
        };
        recognition.onend = () => {
          isListening          = false;
          voiceBtn.textContent = '🎙️ Use voice input';
          voiceBtn.disabled    = false;
        };
        try { recognition.start(); } catch (e) {
          if (message) message.textContent = 'Could not start voice input: ' + e.message;
          isListening       = false;
          voiceBtn.disabled = false;
        }
      });
    }
  }
});
