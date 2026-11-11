/**
 * flunds · Interactive Studio, Phone Simulator, and Agent MCP Engine
 * Craft Floor: Apple Design & Impeccable Philosophy (Unfuckin-Slop)
 */

(function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // 1. Audio Engine (Tactile Web Audio API)
  // ---------------------------------------------------------------------------
  class AudioEngine {
    constructor() {
      this.ctx = null;
      this.enabled = false;
    }

    init() {
      if (!this.ctx && typeof window.AudioContext !== 'undefined') {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioCtx();
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    toggle() {
      this.init();
      this.enabled = !this.enabled;
      return this.enabled;
    }

    playTap() {
      if (!this.enabled || !this.ctx) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      const now = this.ctx.currentTime;

      osc.type = 'sine';
      osc.frequency.setValueAtTime(320, now);
      osc.frequency.exponentialRampToValueAtTime(140, now + 0.04);

      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.04);
    }

    playKey() {
      if (!this.enabled || !this.ctx) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      const now = this.ctx.currentTime;

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(800 + Math.random() * 300, now);

      gain.gain.setValueAtTime(0.03, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.025);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.025);
    }

    playSuccessChime() {
      if (!this.enabled || !this.ctx) return;
      const now = this.ctx.currentTime;
      const notes = [523.25, 659.25, 783.99, 1046.5]; // C5, E5, G5, C6

      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const noteStart = now + idx * 0.07;

        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, noteStart);

        gain.gain.setValueAtTime(0.06, noteStart);
        gain.gain.exponentialRampToValueAtTime(0.001, noteStart + 0.35);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(noteStart);
        osc.stop(noteStart + 0.35);
      });
    }
  }

  const audio = new AudioEngine();

  // ---------------------------------------------------------------------------
  // 2. Application Presets & Mock Data
  // ---------------------------------------------------------------------------
  const PRESETS = {
    habits: {
      name: 'Orbit Habit PWA',
      shortName: 'Orbit',
      category: 'Productivity',
      url: 'flunds.dev/@steoward/orbit',
      iconSvg: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>',
      iconBg: 'linear-gradient(135deg, #10b981, #059669)',
      prompt: 'Build an offline habit tracker with daily streaks, haptics, and instant PWA manifest.',
      terminalLogs: [
        { time: '00:01', agent: 'Agent', tool: 'flunds_create_app', text: 'Initializing PWA "Orbit" with standalone display and orientation portrait.' },
        { time: '00:03', agent: 'Agent', tool: 'flunds_generate_icons', text: 'Rendered adaptive maskable 192x192 & 512x512 icons in emerald-green.' },
        { time: '00:06', agent: 'Agent', tool: 'flunds_configure_sw', text: 'Configured offline CacheStorage strategy: StaleWhileRevalidate for local habits.' },
        { time: '00:09', agent: 'Agent', tool: 'flunds_deploy_pwa', text: 'Deployed PWA to edge! Install link: flunds.dev/@steoward/orbit (Size: 420 KB)' }
      ],
      renderScreen: function () {
        return `
          <div class="sim-pwa-view">
            <div class="sim-app-header">
              <span class="sim-app-title">Today's Orbit</span>
              <span class="sim-pwa-badge">PWA Active</span>
            </div>
            <div class="habit-list">
              <div class="habit-row" role="button" tabindex="0" data-habit="1">
                <div class="habit-info">
                  <span class="habit-title">Morning Deep Work</span>
                  <span class="habit-streak">18-day streak</span>
                </div>
                <div class="habit-checkbox checked">✓</div>
              </div>
              <div class="habit-row" role="button" tabindex="0" data-habit="2">
                <div class="habit-info">
                  <span class="habit-title">Hydration 2.5L</span>
                  <span class="habit-streak">12-day streak</span>
                </div>
                <div class="habit-checkbox checked">✓</div>
              </div>
              <div class="habit-row" role="button" tabindex="0" data-habit="3">
                <div class="habit-info">
                  <span class="habit-title">Cold Plunge / Cardio</span>
                  <span class="habit-streak">4-day streak</span>
                </div>
                <div class="habit-checkbox"></div>
              </div>
              <div class="habit-row" role="button" tabindex="0" data-habit="4">
                <div class="habit-info">
                  <span class="habit-title">Review Code Pull Requests</span>
                  <span class="habit-streak">29-day streak</span>
                </div>
                <div class="habit-checkbox"></div>
              </div>
            </div>
          </div>
        `;
      }
    },
    wallet: {
      name: 'Krypton Pay PWA',
      shortName: 'Krypton',
      category: 'Fintech',
      url: 'flunds.dev/@steoward/krypton',
      iconSvg: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="14" x="2" y="5" rx="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line></svg>',
      iconBg: 'linear-gradient(135deg, #38bdf8, #0284c7)',
      prompt: 'Construct a non-custodial crypto wallet PWA with biometric WebAuthn authorization.',
      terminalLogs: [
        { time: '00:01', agent: 'Agent', tool: 'flunds_create_app', text: 'Initializing PWA "Krypton" with secure hardware key storage and WebAuthn API.' },
        { time: '00:04', agent: 'Agent', tool: 'flunds_generate_manifest', text: 'Set secure origin requirements, theme_color #0c0e14, and standalone window.' },
        { time: '00:07', agent: 'Agent', tool: 'flunds_configure_sw', text: 'Isolated encrypted local state into IndexedDB with zero cloud credentials leak.' },
        { time: '00:10', agent: 'Agent', tool: 'flunds_deploy_pwa', text: 'Bundle published! Ready for iPhone & Android home screen installation. (Size: 890 KB)' }
      ],
      renderScreen: function () {
        return `
          <div class="sim-pwa-view">
            <div class="sim-app-header">
              <span class="sim-app-title">Krypton Vault</span>
              <span class="sim-pwa-badge">Biometric</span>
            </div>
            <div class="wallet-balance-card">
              <span style="font-size: 0.75rem; color: #94a3b8;">Total Available Balance</span>
              <div class="wallet-balance-num">$14,892.40</div>
              <span style="font-size: 0.75rem; color: #10b981;">+ 4.82% today</span>
            </div>
            <div class="wallet-quick-actions">
              <button type="button" class="wallet-btn" id="wallet-send">Send</button>
              <button type="button" class="wallet-btn" id="wallet-receive">Receive</button>
              <button type="button" class="wallet-btn" id="wallet-swap">Swap</button>
            </div>
          </div>
        `;
      }
    },
    ambient: {
      name: 'Solara Audio PWA',
      shortName: 'Solara',
      category: 'Soundscapes',
      url: 'flunds.dev/@steoward/solara',
      iconSvg: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>',
      iconBg: 'linear-gradient(135deg, #a855f7, #7c3aed)',
      prompt: 'Develop an ambient generative audio soundscape PWA running completely offline via Web Audio.',
      terminalLogs: [
        { time: '00:01', agent: 'Agent', tool: 'flunds_create_app', text: 'Initializing PWA "Solara" with background audio session policy.' },
        { time: '00:04', agent: 'Agent', tool: 'flunds_generate_manifest', text: 'Registered mediaSession playback controls for iOS Dynamic Island and Android lockscreen.' },
        { time: '00:07', agent: 'Agent', tool: 'flunds_configure_sw', text: 'Cached generative audio synthesis oscillators and sound models into Service Worker.' },
        { time: '00:10', agent: 'Agent', tool: 'flunds_deploy_pwa', text: 'Edge deploy complete! Installable directly from Safari/Chrome. (Size: 380 KB)' }
      ],
      renderScreen: function () {
        return `
          <div class="sim-pwa-view">
            <div class="sim-app-header">
              <span class="sim-app-title">Solara Sound</span>
              <span class="sim-pwa-badge">Offline Audio</span>
            </div>
            <div class="audio-player-card">
              <span style="font-size: 0.8rem; font-weight: 600;">Active Frequency</span>
              <div style="font-size: 1.1rem; font-family: monospace; color: #a855f7;">432 Hz Harmonic Rain</div>
              <div class="soundscape-selector">
                <div class="sound-chip active" role="button" tabindex="0">
                  <span>Deep Forest Rain</span>
                  <span>Active</span>
                </div>
                <div class="sound-chip" role="button" tabindex="0">
                  <span>Night Cosmic Wind</span>
                  <span>Ready</span>
                </div>
                <div class="sound-chip" role="button" tabindex="0">
                  <span>Binaural Focus Alpha</span>
                  <span>Ready</span>
                </div>
              </div>
            </div>
          </div>
        `;
      }
    },
    notes: {
      name: 'Quill Markdown PWA',
      shortName: 'Quill',
      category: 'Notes',
      url: 'flunds.dev/@steoward/quill',
      iconSvg: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>',
      iconBg: 'linear-gradient(135deg, #f59e0b, #d97706)',
      prompt: 'Build a distraction-free mobile markdown notebook with instant local export and offline cache.',
      terminalLogs: [
        { time: '00:01', agent: 'Agent', tool: 'flunds_create_app', text: 'Initializing PWA "Quill" with text-editor view and hardware keyboard support.' },
        { time: '00:03', agent: 'Agent', tool: 'flunds_generate_manifest', text: 'Registered file_handlers for .md and .txt files directly from native OS share sheet.' },
        { time: '00:06', agent: 'Agent', tool: 'flunds_configure_sw', text: 'Configured local snapshot sync and offline IndexedDB persistence.' },
        { time: '00:09', agent: 'Agent', tool: 'flunds_deploy_pwa', text: 'Edge deployment live! Installable on home screen in 1 click. (Size: 510 KB)' }
      ],
      renderScreen: function () {
        return `
          <div class="sim-pwa-view">
            <div class="sim-app-header">
              <span class="sim-app-title">Quill Notes</span>
              <span class="sim-pwa-badge">Local Sync</span>
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <div style="padding: 10px; background: rgba(255,255,255,0.04); border-radius: 8px; font-size: 0.85rem;">
                <strong>Architecture notes</strong>
                <p style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">Service workers allow full offline capability on phone screens...</p>
              </div>
              <div style="padding: 10px; background: rgba(255,255,255,0.04); border-radius: 8px; font-size: 0.85rem;">
                <strong>Next Sprint Milestones</strong>
                <p style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">Connect flunds MCP to autonomous Claude Code agent...</p>
              </div>
            </div>
          </div>
        `;
      }
    }
  };

  // State
  let currentPresetKey = 'habits';
  let isHomeScreenView = false;
  let installedApps = new Set();

  // Elements
  const audioToggle = document.getElementById('audio-toggle');
  const terminalStream = document.getElementById('terminal-stream');
  const promptInput = document.getElementById('prompt-input');
  const promptRunBtn = document.getElementById('prompt-run-btn');
  const phoneScreen = document.getElementById('phone-screen');
  const phoneHomeBtn = document.getElementById('phone-home-btn');
  const installPwaBtn = document.getElementById('install-pwa-btn');
  const simulatorUrlDisplay = document.getElementById('simulator-url-display');
  const phoneClock = document.getElementById('phone-clock');
  const toastNotify = document.getElementById('toast-notify');

  // ---------------------------------------------------------------------------
  // 3. Audio Toggle Setup
  // ---------------------------------------------------------------------------
  if (audioToggle) {
    audioToggle.addEventListener('click', () => {
      const active = audio.toggle();
      audioToggle.setAttribute('aria-pressed', String(active));
      const label = audioToggle.querySelector('.audio-btn-label');
      if (label) {
        label.textContent = active ? 'Sound On' : 'Sound Off';
      }
      showToast(active ? 'Tactile Interface Audio Enabled' : 'Tactile Audio Muted');
      if (active) audio.playTap();
    });
  }

  // ---------------------------------------------------------------------------
  // 4. Phone Clock Updater
  // ---------------------------------------------------------------------------
  function updatePhoneClock() {
    if (!phoneClock) return;
    const now = new Date();
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    hours = hours % 12 || 12;
    phoneClock.textContent = `${hours}:${minutes}`;
  }
  setInterval(updatePhoneClock, 30000);
  updatePhoneClock();

  // ---------------------------------------------------------------------------
  // 5. Toast Notification System
  // ---------------------------------------------------------------------------
  let toastTimer = null;
  function showToast(message) {
    if (!toastNotify) return;
    toastNotify.textContent = message;
    toastNotify.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toastNotify.classList.remove('visible');
    }, 2800);
  }

  // ---------------------------------------------------------------------------
  // 6. Terminal Code Stream Simulation
  // ---------------------------------------------------------------------------
  function streamTerminalLogs(logs) {
    if (!terminalStream) return;
    terminalStream.innerHTML = '';
    let delay = 0;

    logs.forEach((log) => {
      setTimeout(() => {
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = `
          <span class="log-time">[${log.time}]</span>
          <span class="log-agent">${log.agent}</span>
          <span class="log-tool">&gt; ${log.tool}:</span>
          <span class="log-content">${log.text}</span>
        `;
        terminalStream.appendChild(entry);
        terminalStream.scrollTop = terminalStream.scrollHeight;
        audio.playKey();
      }, delay);
      delay += 350;
    });
  }

  // ---------------------------------------------------------------------------
  // 7. Phone Screen & App Rendering
  // ---------------------------------------------------------------------------
  function renderPhoneContent() {
    if (!phoneScreen) return;

    if (isHomeScreenView) {
      // Render Simulated SpringBoard / Home Screen
      let appIconsHtml = `
        <div class="sim-springboard-view">
          <div class="springboard-grid">
      `;

      // Render default phone apps
      const defaultApps = [
        { name: 'Safari', bg: '#0284c7', icon: '🌐' },
        { name: 'Messages', bg: '#10b981', icon: '💬' },
        { name: 'Settings', bg: '#64748b', icon: '⚙️' },
        { name: 'Camera', bg: '#334155', icon: '📷' }
      ];

      defaultApps.forEach((app) => {
        appIconsHtml += `
          <div class="app-icon-slot" tabindex="0" role="button" aria-label="Open ${app.name}">
            <div class="app-icon-box" style="background: ${app.bg}; color: #fff; font-size: 1.4rem;">
              ${app.icon}
            </div>
            <span class="app-icon-name">${app.name}</span>
          </div>
        `;
      });

      // Render installed PWAs
      Object.keys(PRESETS).forEach((key) => {
        const preset = PRESETS[key];
        const isInstalled = installedApps.has(key);
        if (isInstalled) {
          appIconsHtml += `
            <div class="app-icon-slot" tabindex="0" role="button" data-launch="${key}" aria-label="Launch installed PWA ${preset.shortName}">
              <div class="app-icon-box new-installed" style="background: ${preset.iconBg};">
                ${preset.iconSvg}
                <span class="pwa-indicator-badge">PWA</span>
              </div>
              <span class="app-icon-name">${preset.shortName}</span>
            </div>
          `;
        }
      });

      appIconsHtml += `
          </div>
        </div>
      `;

      phoneScreen.innerHTML = appIconsHtml;

      // Attach launch click handlers for installed PWAs
      phoneScreen.querySelectorAll('[data-launch]').forEach((btn) => {
        btn.addEventListener('click', () => {
          const targetKey = btn.getAttribute('data-launch');
          launchPwa(targetKey);
        });
      });
    } else {
      // Render the current PWA
      const preset = PRESETS[currentPresetKey];
      phoneScreen.innerHTML = preset.renderScreen();
      attachAppInteractions();
    }
  }

  function launchPwa(key) {
    audio.playTap();
    currentPresetKey = key;
    isHomeScreenView = false;
    updateSimulatorMeta();
    renderPhoneContent();
  }

  function attachAppInteractions() {
    // Habit checkbox toggle
    phoneScreen.querySelectorAll('.habit-row').forEach((row) => {
      row.addEventListener('click', () => {
        audio.playTap();
        const box = row.querySelector('.habit-checkbox');
        if (box) {
          const isChecked = box.classList.contains('checked');
          box.classList.toggle('checked');
          box.textContent = isChecked ? '' : '✓';
        }
      });
    });

    // Sound chips toggle
    phoneScreen.querySelectorAll('.sound-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        audio.playTap();
        phoneScreen.querySelectorAll('.sound-chip').forEach((c) => c.classList.remove('active'));
        chip.classList.add('active');
        const textSpan = chip.querySelectorAll('span')[1];
        if (textSpan) textSpan.textContent = 'Active';
      });
    });

    // Wallet buttons
    const sendBtn = phoneScreen.querySelector('#wallet-send');
    if (sendBtn) {
      sendBtn.addEventListener('click', () => {
        audio.playTap();
        showToast('Krypton PWA: Biometric confirmation approved!');
      });
    }
  }

  function updateSimulatorMeta() {
    const preset = PRESETS[currentPresetKey];
    if (simulatorUrlDisplay) {
      simulatorUrlDisplay.textContent = preset.url;
    }
    if (promptInput) {
      promptInput.value = preset.prompt;
    }
    // Update active preset buttons
    document.querySelectorAll('.preset-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.getAttribute('data-preset') === currentPresetKey);
    });
  }

  // ---------------------------------------------------------------------------
  // 8. Preset Switcher Logic
  // ---------------------------------------------------------------------------
  function loadPreset(key) {
    if (!PRESETS[key]) return;
    audio.playTap();
    currentPresetKey = key;
    isHomeScreenView = false;
    updateSimulatorMeta();
    renderPhoneContent();
    streamTerminalLogs(PRESETS[key].terminalLogs);
  }

  document.querySelectorAll('.preset-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const key = btn.getAttribute('data-preset');
      loadPreset(key);
    });
  });

  document.querySelectorAll('.gallery-item-card button, .gallery-item-card').forEach((el) => {
    el.addEventListener('click', (e) => {
      const presetKey = el.getAttribute('data-preset');
      if (presetKey) {
        loadPreset(presetKey);
        const studioEl = document.getElementById('studio');
        if (studioEl) {
          studioEl.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });
  });

  // ---------------------------------------------------------------------------
  // 9. Phone Home Button & PWA Install Simulation
  // ---------------------------------------------------------------------------
  if (phoneHomeBtn) {
    phoneHomeBtn.addEventListener('click', () => {
      audio.playTap();
      isHomeScreenView = !isHomeScreenView;
      renderPhoneContent();
    });
  }

  if (installPwaBtn) {
    installPwaBtn.addEventListener('click', () => {
      audio.playSuccessChime();
      installedApps.add(currentPresetKey);
      const preset = PRESETS[currentPresetKey];
      showToast(`Installed "${preset.shortName}" to Phone Home Screen!`);
      // Animate to home screen to reveal the installed PWA
      isHomeScreenView = true;
      renderPhoneContent();
    });
  }

  // ---------------------------------------------------------------------------
  // 10. Agent Tab Switcher & Prompt Dispatcher
  // ---------------------------------------------------------------------------
  const agentStatusText = document.getElementById('agent-status-text');
  document.querySelectorAll('.agent-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      audio.playTap();
      document.querySelectorAll('.agent-tab').forEach((t) => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      const agentName = tab.textContent;
      if (agentStatusText) {
        agentStatusText.textContent = `${agentName} connected to flunds MCP`;
      }
      showToast(`${agentName} agent active`);
    });
  });

  if (promptRunBtn && promptInput) {
    promptRunBtn.addEventListener('click', () => {
      audio.playTap();
      const val = promptInput.value.trim();
      if (!val) return;
      const customLogs = [
        { time: '00:01', agent: 'Agent', tool: 'flunds_create_app', text: `Analyzing prompt: "${val.slice(0, 48)}..."` },
        { time: '00:04', agent: 'Agent', tool: 'flunds_generate_manifest', text: 'Compiling responsive touch viewport, webmanifest, and splash screens.' },
        { time: '00:07', agent: 'Agent', tool: 'flunds_configure_sw', text: 'Building offline Service Worker with dynamic background sync.' },
        { time: '00:10', agent: 'Agent', tool: 'flunds_deploy_pwa', text: 'Deployment published! Ready for one-tap home screen install.' }
      ];
      streamTerminalLogs(customLogs);
      showToast('Agent building & deploying PWA...');
    });
  }

  // ---------------------------------------------------------------------------
  // 11. MCP Config Tabs & Copy Buttons
  // ---------------------------------------------------------------------------
  document.querySelectorAll('.config-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      audio.playTap();
      document.querySelectorAll('.config-tab').forEach((t) => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      const targetId = tab.getAttribute('data-target');
      document.querySelectorAll('.config-content').forEach((content) => {
        content.classList.toggle('active', content.id === targetId);
      });
    });
  });

  const copyHeroBtn = document.getElementById('copy-mcp-hero-btn');
  const copyActiveBtn = document.getElementById('copy-active-snippet-btn');

  function copyMcpSnippet() {
    const activeContent = document.querySelector('.config-content.active pre code');
    const textToCopy = activeContent ? activeContent.textContent : '{\n  "mcpServers": {\n    "flunds": {\n      "command": "flunds-mcp"\n    }\n  }\n}';

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(textToCopy).then(() => {
        audio.playTap();
        showToast('flunds MCP Configuration copied to clipboard!');
      }).catch(() => {
        showToast('MCP Configuration copied!');
      });
    } else {
      showToast('MCP Configuration ready to paste!');
    }
  }

  if (copyHeroBtn) copyHeroBtn.addEventListener('click', copyMcpSnippet);
  if (copyActiveBtn) copyActiveBtn.addEventListener('click', copyMcpSnippet);

  // ---------------------------------------------------------------------------
  // 12. Developer Handle Reservation Form
  // ---------------------------------------------------------------------------
  const claimForm = document.getElementById('claim-handle-form');
  const handleInput = document.getElementById('handle-input');
  const claimReceipt = document.getElementById('claim-receipt');
  const receiptNamespace = document.getElementById('receipt-namespace');
  const receiptToken = document.getElementById('receipt-token');

  if (claimForm && handleInput && claimReceipt) {
    claimForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const rawHandle = handleInput.value.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '');
      if (!rawHandle) return;

      audio.playSuccessChime();
      const randomHex = Math.random().toString(16).substring(2, 10) + Math.random().toString(16).substring(2, 10);
      if (receiptNamespace) receiptNamespace.textContent = `flunds.dev/@${rawHandle}`;
      if (receiptToken) receiptToken.textContent = `flunds_live_sec_${randomHex}`;

      claimReceipt.classList.remove('hidden');
      showToast(`Handle @${rawHandle} secured!`);
    });
  }

  // ---------------------------------------------------------------------------
  // Initial Boot
  // ---------------------------------------------------------------------------
  loadPreset('habits');
})();
