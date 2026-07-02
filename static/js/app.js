const translations = {
  en: {
    dashboard: 'Dashboard',
    checker: 'Checker',
    history: 'History',
    profile: 'Profile',
    logout: 'Logout',
    footer: '© 2026 Symptom Checker • Secure, modern symptom guidance',
    welcomeBack: 'Welcome back',
    loginIntro: 'Sign in to continue your health journey with AI-guided insights.',
    login: 'Login',
    newHere: 'New here?',
    createAccount: 'Create an account',
    createAccountTitle: 'Create your account',
    registerIntro: 'Register to start tracking symptoms and receive smart guidance.',
    createAccountButton: 'Create account',
    haveAccount: 'Already have an account?',
    loginLink: 'Login',
  },
  hi: {
    dashboard: 'डैशबोर्ड',
    checker: 'जाँच',
    history: 'इतिहास',
    profile: 'प्रोफ़ाइल',
    logout: 'लॉगआउट',
    footer: '© 2026 एआई सिंप्टम चेकर • सुरक्षित, आधुनिक लक्षण मार्गदर्शन',
    welcomeBack: 'वापसी पर स्वागत है',
    loginIntro: 'एआई-निर्देशित अंतर्दृष्टि के साथ अपने स्वास्थ्य सफ़र को जारी रखने के लिए साइन इन करें।',
    login: 'लॉगिन',
    newHere: 'यहाँ नए हैं?',
    createAccount: 'खाता बनाएं',
    createAccountTitle: 'अपना खाता बनाएं',
    registerIntro: 'लक्षणों को ट्रैक करना और स्मार्ट मार्गदर्शन प्राप्त करना शुरू करने के लिए रजिस्टर करें।',
    createAccountButton: 'खाता बनाएं',
    haveAccount: 'पहले से खाता है?',
    loginLink: 'लॉगिन',
  },
};

function applyTranslations(lang) {
  document.documentElement.setAttribute('lang', lang);
  document.querySelectorAll('[data-i18n]').forEach((element) => {
    const key = element.getAttribute('data-i18n');
    if (translations[lang][key]) {
      element.textContent = translations[lang][key];
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('theme-toggle');
  const logoutBtn = document.getElementById('logout-btn');
  const langToggle = document.getElementById('lang-toggle');

  if (langToggle) {
    const savedLang = localStorage.getItem('lang') || 'en';
    langToggle.textContent = savedLang === 'en' ? 'हिंदी' : 'EN';
    applyTranslations(savedLang);
    langToggle.addEventListener('click', () => {
      const nextLang = savedLang === 'en' ? 'hi' : 'en';
      localStorage.setItem('lang', nextLang);
      langToggle.textContent = nextLang === 'en' ? 'हिंदी' : 'EN';
      applyTranslations(nextLang);
    });
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', current);
      localStorage.setItem('theme', current);
      themeToggle.textContent = current === 'dark' ? '☀️' : '🌙';
    });
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    themeToggle.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      const token = localStorage.getItem('token');
      if (token) {
        await fetch('/api/logout', { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
      }
      localStorage.removeItem('token');
      document.cookie = 'token=; Max-Age=-1; path=/';
      window.location.href = '/login';
    });
  }

  const symptomForm = document.getElementById('symptom-form');
  if (symptomForm) {
    const message = document.getElementById('analysis-message');
    const resultCard = document.getElementById('result-card');
    const severityBadge = document.getElementById('severity-badge');
    const voiceBtn = document.getElementById('voice-btn');
    const symptomsInput = document.querySelector('textarea[name="symptoms"]');
    const chatCard = document.getElementById('chat-card');
    const chatAnswer = document.getElementById('chat-answer');

    symptomForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const formData = new FormData(symptomForm);
      const payload = Object.fromEntries(formData.entries());
      const token = localStorage.getItem('token');

      message.textContent = 'Analyzing your symptoms...';
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (!response.ok) {
        message.textContent = data.error || 'Analysis failed';
        return;
      }

      document.getElementById('condition-name').textContent = data.possible_condition;
      severityBadge.textContent = data.severity;
      severityBadge.className = `severity-badge ${data.severity.toLowerCase()}`;
      document.getElementById('explanation').textContent = data.explanation;
      document.getElementById('doctor').textContent = data.recommended_doctor;
      document.getElementById('advice').textContent = data.health_advice;

      // Show matched keywords
      const keywordsRow = document.getElementById('keywords-row');
      const keywordsList = document.getElementById('keywords-list');
      if (data.matched_keywords && data.matched_keywords.length) {
        keywordsList.innerHTML = data.matched_keywords
          .map(k => `<span class="keyword-tag">${k}</span>`).join(' ');
        keywordsRow.classList.remove('hidden');
      } else {
        keywordsRow.classList.add('hidden');
      }

      // Show additional conditions
      const additionalSection = document.getElementById('additional-conditions');
      const conditionsList = document.getElementById('conditions-list');
      if (data.all_conditions && data.all_conditions.length) {
        conditionsList.innerHTML = data.all_conditions.map(c => `
          <div class="extra-condition-card">
            <div class="extra-condition-header">
              <strong>${c.condition}</strong>
              <span class="severity-badge ${c.severity.toLowerCase()}">${c.severity}</span>
            </div>
            <p style="margin:0.4rem 0 0.25rem;font-size:0.9rem;">${c.explanation}</p>
            <p style="font-size:0.85rem;"><strong>Doctor:</strong> ${c.doctor}</p>
            <p style="font-size:0.8rem;color:var(--text-muted);"><strong>Matched:</strong> ${c.matched_keywords.join(', ')}</p>
            <details style="margin-top:0.5rem;">
              <summary style="cursor:pointer;font-size:0.85rem;">View advice</summary>
              <div class="advice-box" style="margin-top:0.5rem;white-space:pre-line;">${c.advice}</div>
            </details>
          </div>`).join('');
        additionalSection.classList.remove('hidden');
      } else {
        additionalSection.classList.add('hidden');
      }

      resultCard.classList.remove('hidden');
      chatCard.classList.add('hidden');
      chatAnswer.innerHTML = '';
      message.textContent = data.message || 'Analysis complete';

      document.getElementById('download-btn').onclick = () => {
        window.open(`/api/download-pdf/${data.assessment_id}`, '_blank');
      };

      document.getElementById('chat-btn').onclick = () => {
        chatCard.classList.toggle('hidden');
      };

      document.getElementById('chat-submit').onclick = async () => {
        const question = document.getElementById('chat-question').value;
        const chatResponse = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({ question, assessment_id: data.assessment_id }),
        });
        const chatData = await chatResponse.json();
        chatAnswer.innerHTML = `<p>${chatData.answer}</p>`;
      };
    });

    if (voiceBtn && symptomsInput) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      // Web Speech API requires HTTPS or localhost
      const isSecureContext = location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1';

      if (!SpeechRecognition || !isSecureContext) {
        voiceBtn.disabled = true;
        voiceBtn.textContent = '🎙️ Voice unavailable';
        voiceBtn.title = !SpeechRecognition
          ? 'Your browser does not support voice input. Use Chrome or Edge.'
          : 'Voice input requires HTTPS or localhost.';
      } else {
        let isListening = false;
        let hadError = false;

        voiceBtn.addEventListener('click', () => {
          if (isListening) return;
          hadError = false;

          const recognition = new SpeechRecognition();
          recognition.lang = 'en-US';
          recognition.continuous = false;
          recognition.interimResults = false;
          recognition.maxAlternatives = 1;

          recognition.onstart = () => {
            isListening = true;
            voiceBtn.textContent = '🔴 Listening...';
            voiceBtn.disabled = true;
            message.textContent = 'Listening... speak your symptoms now.';
          };

          recognition.onresult = (event) => {
            const transcription = Array.from(event.results)
              .map((r) => r[0].transcript).join(' ');
            symptomsInput.value = symptomsInput.value
              ? `${symptomsInput.value}, ${transcription}`
              : transcription;
            message.textContent = 'Voice input added.';
          };

          recognition.onerror = (event) => {
            hadError = true;
            const errors = {
              'not-allowed': 'Mic permission denied — click the lock icon in your browser address bar and allow microphone.',
              'no-speech': 'No speech detected. Please try again.',
              'network': 'Network error. Make sure you are online.',
              'audio-capture': 'No microphone found. Please connect a mic and try again.',
              'service-not-allowed': 'Speech service blocked. Try opening the app on localhost.',
            };
            message.textContent = errors[event.error] || `Voice error: ${event.error}`;
          };

          recognition.onend = () => {
            isListening = false;
            voiceBtn.textContent = '🎙️ Use voice input';
            voiceBtn.disabled = false;
            // Don't overwrite error message
            if (!hadError && message.textContent === 'Listening... speak your symptoms now.') {
              message.textContent = 'No speech detected. Please try again.';
            }
          };

          try {
            recognition.start();
          } catch (e) {
            message.textContent = 'Could not start voice input: ' + e.message;
            isListening = false;
            voiceBtn.disabled = false;
          }
        });
      }
    }
  }
});
