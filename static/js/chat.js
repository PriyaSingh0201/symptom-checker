// static/js/chat.js – Dooper Bot Widget
// Standalone – does NOT modify any existing app.js functionality

(function () {
  'use strict';

  // ── DOM refs (resolved after DOMContentLoaded) ──────────────────────────
  let toggle, chatWindow, closeBtn, clearBtn, messages, input, sendBtn,
      statusEl, contextBanner, contextText, unreadBadge, suggestions;

  // ── State ────────────────────────────────────────────────────────────────
  let isOpen = false;
  let isLoading = false;
  let sessionHistory = [];   // { role, text, time }
  let currentAssessmentId = null;

  // ── Init ─────────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    toggle        = document.getElementById('chat-widget-toggle');
    chatWindow    = document.getElementById('chat-widget-window');
    closeBtn      = document.getElementById('chat-widget-close');
    clearBtn      = document.getElementById('chat-clear-btn');
    messages      = document.getElementById('chat-messages');
    input         = document.getElementById('chat-widget-input');
    sendBtn       = document.getElementById('chat-widget-send');
    statusEl      = document.getElementById('chat-status');
    contextBanner = document.getElementById('chat-context-banner');
    contextText   = document.getElementById('chat-context-text');
    unreadBadge   = document.getElementById('chat-unread');
    suggestions   = document.getElementById('chat-suggestions');

    if (!toggle) return; // widget not present on this page

    // Attach event listeners
    toggle.addEventListener('click', toggleChat);
    
    // Close button - make sure it's properly attached
    if (closeBtn) {
      closeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('Close button clicked');
        closeChat();
      });
      console.log('Close button listener attached successfully');
    } else {
      console.error('Chat: close button element not found!');
    }
    
    if (clearBtn) {
      clearBtn.addEventListener('click', clearChat);
    }
    
    sendBtn.addEventListener('click', handleSend);
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } });

    // Suggestion chips
    document.querySelectorAll('.chat-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        input.value = chip.textContent.trim();
        handleSend();
      });
    });
    
    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && isOpen) {
        closeChat();
      }
    });
    
    // Close when clicking outside the chat window (but not on toggle button)
    document.addEventListener('click', (e) => {
      if (isOpen && !chatWindow.contains(e.target) && !toggle.contains(e.target)) {
        closeChat();
      }
    });

    // Load latest assessment context on init
    loadLatestContext();

    // Show welcome message
    showEmpty();
  });

  // ── Toggle / Open / Close ────────────────────────────────────────────────
  function toggleChat() {
    isOpen ? closeChat() : openChat();
  }

  function openChat() {
    isOpen = true;
    chatWindow.classList.remove('hidden');
    toggle.setAttribute('aria-expanded', 'true');
    if (unreadBadge) unreadBadge.classList.add('hidden');
    if (input) input.focus();
    scrollToBottom();
  }

  function closeChat() {
    isOpen = false;
    if (chatWindow) {
      chatWindow.classList.add('hidden');
    }
    if (toggle) {
      toggle.setAttribute('aria-expanded', 'false');
    }
    console.log('Chat closed');
  }

  // ── Context ──────────────────────────────────────────────────────────────
  async function loadLatestContext() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      // Ping /api/assistant with empty-ish call to get context info
      // We just fetch the latest assessment via the profile/history API
      const res = await fetch('/api/history?per_page=1&sort=newest', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = await res.json();
      const latest = (data.assessments || data)[0];
      if (latest) {
        currentAssessmentId = latest.id;
        const severity = latest.severity || 'Moderate';
        contextText.textContent =
          `Context: ${latest.possible_condition} (${severity}) — ${latest.created_date}`;
        contextBanner.classList.remove('hidden');
        
        // Update suggestions based on condition and severity
        updateSuggestions(latest.possible_condition, severity);
        
        setStatus('Context loaded');
      }
    } catch (_) {
      // silently ignore — chat still works without context
    }
  }

  function updateSuggestions(condition, severity) {
    if (!suggestions) return;
    
    // Determine suggestions based on severity and condition keywords
    let conditionSuggestions = [
      "What precautions should I take?",
      "What foods should I eat?",
      "When should I see a doctor?",
      "What medicines can help?",
    ];
    
    // Add severity-specific suggestions
    if (severity === 'Severe' || severity === 'severe') {
      conditionSuggestions.unshift("🚨 Is this an emergency?");
    }
    
    // Add common follow-ups
    conditionSuggestions.push(
      "How long will recovery take?",
      "Can I exercise?",
      "Is this contagious?"
    );
    
    // Update the suggestion chips
    suggestions.innerHTML = '';
    conditionSuggestions.forEach(text => {
      const chip = document.createElement('button');
      chip.className = 'chat-chip';
      chip.type = 'button';
      chip.textContent = text;
      chip.addEventListener('click', () => {
        input.value = text;
        handleSend();
      });
      suggestions.appendChild(chip);
    });
  }

  // ── Send ─────────────────────────────────────────────────────────────────
  async function handleSend() {
    const text = input.value.trim();
    if (!text || isLoading) return;

    const token = localStorage.getItem('token');
    if (!token) {
      appendMessage('ai', 'Please log in to use Dooper Bot.');
      return;
    }

    input.value = '';
    hideSuggestions();
    appendMessage('user', text);
    showTyping();
    setLoading(true);
    setStatus('Thinking...');

    try {
      const res = await fetch('/api/assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: text,
          assessment_id: currentAssessmentId || undefined,
        }),
      });

      removeTyping();

      if (res.status === 429) {
        appendMessage('ai', 'Too many requests. Please wait a moment and try again.');
        setStatus('Rate limited');
        return;
      }

      const data = await res.json();

      if (!res.ok) {
        appendMessage('ai', data.error || 'Something went wrong. Please try again.');
        setStatus('Error');
        return;
      }

      appendMessage('ai', data.answer);

      // Update context banner if condition returned
      if (data.condition && !contextBanner.classList.contains('hidden') === false) {
        contextText.textContent = `Context: ${data.condition}`;
        contextBanner.classList.remove('hidden');
      }

      // Highlight emergency situation
      if (data.is_emergency) {
        const lastMsg = messages.querySelector('.chat-msg.ai:last-child');
        if (lastMsg) {
          lastMsg.style.backgroundColor = '#ffebee';
          const bubble = lastMsg.querySelector('.chat-bubble');
          if (bubble) {
            bubble.style.borderLeft = '4px solid #d32f2f';
            bubble.style.borderRadius = '4px';
          }
        }
        setStatus('🚨 Emergency - Seek immediate help');
      } else {
        setStatus('Ready to help');
      }

      // Show unread badge if chat is closed
      if (!isOpen) {
        unreadBadge.classList.remove('hidden');
      }

    } catch (err) {
      removeTyping();
      appendMessage('ai', 'Network error. Please check your connection and try again.');
      setStatus('Offline');
    } finally {
      setLoading(false);
    }
  }

  // ── Message rendering ────────────────────────────────────────────────────
  function appendMessage(role, text) {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    sessionHistory.push({ role, text, time });

    const wrapper = document.createElement('div');
    wrapper.className = `chat-msg ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    
    // Add special styling for emergency messages
    if (text.includes('🚨') || text.includes('emergency') || text.includes('IMMEDIATE')) {
      bubble.style.borderLeft = '4px solid #d32f2f';
      bubble.style.backgroundColor = role === 'ai' ? '#ffebee' : undefined;
    }
    
    bubble.innerHTML = formatText(text);

    const meta = document.createElement('div');
    meta.className = 'chat-meta';

    const timeEl = document.createElement('span');
    timeEl.className = 'chat-time';
    timeEl.textContent = time;

    meta.appendChild(timeEl);

    // Copy button for AI messages
    if (role === 'ai') {
      const copyBtn = document.createElement('button');
      copyBtn.className = 'chat-copy-btn';
      copyBtn.textContent = 'Copy';
      copyBtn.title = 'Copy message';
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(text).then(() => {
          copyBtn.textContent = 'Copied!';
          setTimeout(() => { copyBtn.textContent = 'Copy'; }, 1500);
        });
      });
      meta.appendChild(copyBtn);
    }

    wrapper.appendChild(bubble);
    wrapper.appendChild(meta);

    // Remove empty state if present
    const empty = messages.querySelector('.chat-empty');
    if (empty) empty.remove();

    messages.appendChild(wrapper);
    scrollToBottom();
  }

  function formatText(text) {
    // Convert bullet points and newlines to HTML, with better formatting
    let formatted = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br>')
      .replace(/•\s/g, '<span style="color:var(--primary)">•</span> ');
    
    // Highlight emergency warnings
    formatted = formatted.replace(
      /🚨(.*?)(?=<br>|$)/g,
      '<span style="color: #d32f2f; font-weight: 600;">🚨$1</span>'
    );
    
    // Highlight important keywords
    const keywords = ['immediately', 'urgent', 'emergency', 'critical', 'severe', 'ALWAYS', 'WARNING'];
    keywords.forEach(kw => {
      const regex = new RegExp(`\\b(${kw})\\b`, 'gi');
      formatted = formatted.replace(regex, '<strong style="color: #d32f2f;">$1</strong>');
    });
    
    // Highlight doctor recommendations
    formatted = formatted.replace(
      /consult (a )?([a-zA-Z\s]+?)(?:\.|,|<br>)/g,
      'consult <strong style="color: var(--primary);">$2</strong>.'
    );
    
    return formatted;
  }

  // ── Typing indicator ─────────────────────────────────────────────────────
  function showTyping() {
    const typing = document.createElement('div');
    typing.className = 'chat-msg ai';
    typing.id = 'chat-typing-indicator';
    typing.innerHTML = '<div class="chat-typing"><span></span><span></span><span></span></div>';
    messages.appendChild(typing);
    scrollToBottom();
  }

  function removeTyping() {
    const el = document.getElementById('chat-typing-indicator');
    if (el) el.remove();
  }

  // ── Helpers ──────────────────────────────────────────────────────────────
  function scrollToBottom() {
    setTimeout(() => { messages.scrollTop = messages.scrollHeight; }, 50);
  }

  function setLoading(val) {
    isLoading = val;
    sendBtn.disabled = val;
    input.disabled = val;
  }

  function setStatus(text) {
    if (statusEl) statusEl.textContent = text;
  }

  function hideSuggestions() {
    if (suggestions) suggestions.style.display = 'none';
  }

  function showEmpty() {
    if (sessionHistory.length === 0) {
      messages.innerHTML = `
        <div class="chat-empty">
          <div class="chat-empty-icon">🩺</div>
          <p>Ask Dooper Bot anything about your symptoms, recovery, or next steps.</p>
        </div>`;
    }
  }

  function clearChat() {
    sessionHistory = [];
    messages.innerHTML = '';
    showEmpty();
    if (suggestions) suggestions.style.display = '';
    setStatus('Ready to help');
  }

})();
