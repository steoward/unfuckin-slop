/**
 * STRATA Model 01 - Interactive Product Engine
 * Built according to Unfuckin-Slop Craft Floor & Apple Fluid Interface guidelines.
 */

(function () {
  'use strict';

  // --- Multimodal Haptic Audio Synthesizer (Web Audio API) ---
  class HapticAudio {
    constructor() {
      this.ctx = null;
      this.enabled = true;
      this.droneOsc = null;
      this.droneGain = null;
      this.droneFilter = null;
      this.isDronePlaying = false;
    }

    ensureContext() {
      if (!this.ctx && typeof window !== 'undefined') {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) {
          this.ctx = new AudioContextClass();
        }
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    playDetentTick(frequency = 520) {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(frequency, now);
        osc.frequency.exponentialRampToValueAtTime(120, now + 0.018);

        gain.gain.setValueAtTime(0.045, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.018);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.018);
      } catch (err) {
        // Silently handle audio policy
      }
    }

    playSwitchClick() {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.exponentialRampToValueAtTime(90, now + 0.025);

        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.025);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.025);
      } catch (err) {
        // Silently handle audio policy
      }
    }

    playRelayClack() {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        // Two crisp impulses separated by 14ms
        [0, 0.014].forEach((offset, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          const t = now + offset;

          osc.type = 'square';
          osc.frequency.setValueAtTime(idx === 0 ? 440 : 280, t);
          osc.frequency.exponentialRampToValueAtTime(80, t + 0.015);

          gain.gain.setValueAtTime(0.035, t);
          gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.015);

          osc.connect(gain);
          gain.connect(this.ctx.destination);

          osc.start(t);
          osc.stop(t + 0.015);
        });
      } catch (err) {
        // Silently handle audio policy
      }
    }

    playSuccessChime() {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        const chord = [523.25, 659.25, 783.99, 1046.5]; // C Major
        chord.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          const startT = now + idx * 0.05;

          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, startT);

          gain.gain.setValueAtTime(0.04, startT);
          gain.gain.exponentialRampToValueAtTime(0.0001, startT + 0.35);

          osc.connect(gain);
          gain.connect(this.ctx.destination);

          osc.start(startT);
          osc.stop(startT + 0.35);
        });
      } catch (err) {
        // Silently handle audio policy
      }
    }

    startInteractiveTone(baseFreq = 220) {
      if (!this.enabled || this.isDronePlaying) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        this.droneOsc = this.ctx.createOscillator();
        this.droneFilter = this.ctx.createBiquadFilter();
        this.droneGain = this.ctx.createGain();

        this.droneOsc.type = 'sawtooth';
        this.droneOsc.frequency.setValueAtTime(baseFreq, this.ctx.currentTime);

        this.droneFilter.type = 'lowpass';
        this.droneFilter.frequency.setValueAtTime(800, this.ctx.currentTime);
        this.droneFilter.Q.setValueAtTime(3.0, this.ctx.currentTime);

        this.droneGain.gain.setValueAtTime(0.001, this.ctx.currentTime);
        this.droneGain.gain.exponentialRampToValueAtTime(0.035, this.ctx.currentTime + 0.08);

        this.droneOsc.connect(this.droneFilter);
        this.droneFilter.connect(this.droneGain);
        this.droneGain.connect(this.ctx.destination);

        this.droneOsc.start();
        this.isDronePlaying = true;
      } catch (err) {
        // Silently handle audio policy
      }
    }

    updateInteractiveTone(freq, cutoff) {
      if (!this.isDronePlaying || !this.ctx) return;
      try {
        const now = this.ctx.currentTime;
        if (this.droneOsc) {
          this.droneOsc.frequency.setTargetAtTime(freq, now, 0.03);
        }
        if (this.droneFilter) {
          this.droneFilter.frequency.setTargetAtTime(cutoff, now, 0.03);
        }
      } catch (err) {
        // Silently handle
      }
    }

    stopInteractiveTone() {
      if (!this.isDronePlaying || !this.ctx) return;
      try {
        const now = this.ctx.currentTime;
        if (this.droneGain) {
          this.droneGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);
        }
        setTimeout(() => {
          if (this.droneOsc) {
            this.droneOsc.stop();
            this.droneOsc.disconnect();
            this.droneOsc = null;
          }
          this.isDronePlaying = false;
        }, 70);
      } catch (err) {
        this.isDronePlaying = false;
      }
    }
  }

  const haptics = new HapticAudio();

  // --- State Variables ---
  let spatialAngle = 120; // 0 to 360 degrees
  let resonanceQ = 42;    // 0 to 100 (4.2 dB)
  let activeHarmonicMode = 'binaural';
  let isInteractingDial = false;

  // --- DOM Elements ---
  const dialSpatial = document.getElementById('dial-spatial');
  const knobSpatial = document.getElementById('knob-spatial');
  const valSpatial = document.getElementById('val-spatial');

  const dialResonance = document.getElementById('dial-resonance');
  const knobResonance = document.getElementById('knob-resonance');
  const valResonance = document.getElementById('val-resonance');

  const waveformCanvas = document.getElementById('waveform-canvas');
  const screenMode = document.getElementById('screen-mode');
  const screenFreq = document.getElementById('screen-freq');
  const powerStateText = document.getElementById('power-state-text');
  const interactionHint = document.getElementById('interaction-hint');

  const finishObsidianBtn = document.getElementById('finish-obsidian');
  const finishSilverBtn = document.getElementById('finish-silver');
  const hapticAudioToggle = document.getElementById('haptic-audio-toggle');
  const audioStatusGlyph = document.getElementById('audio-status-glyph');
  const modeButtons = document.querySelectorAll('.switch-toggle');

  const reserveForm = document.getElementById('reserve-form');
  const reserveFinishSelect = document.getElementById('reserve-finish');
  const formSuccessBanner = document.getElementById('form-success-banner');
  const nameError = document.getElementById('name-error');
  const emailError = document.getElementById('email-error');

  // --- Rotary Controller Class ---
  class RotaryController {
    constructor(element, knob, onUpdate, options = {}) {
      this.element = element;
      this.knob = knob;
      this.onUpdate = onUpdate;
      this.min = options.min ?? 0;
      this.max = options.max ?? 360;
      this.step = options.step ?? 1;
      this.currentVal = options.initial ?? 0;
      this.isDragging = false;
      this.lastTickVal = this.currentVal;

      this.init();
    }

    init() {
      this.renderAngle();

      this.element.addEventListener('pointerdown', this.onPointerDown.bind(this));
      window.addEventListener('pointermove', this.onPointerMove.bind(this));
      window.addEventListener('pointerup', this.onPointerUp.bind(this));
      window.addEventListener('pointercancel', this.onPointerUp.bind(this));

      this.element.addEventListener('wheel', this.onWheel.bind(this), { passive: false });
      this.element.addEventListener('keydown', this.onKeyDown.bind(this));
    }

    getCenter() {
      const rect = this.element.getBoundingClientRect();
      return {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2
      };
    }

    calculateAngle(clientX, clientY) {
      const center = this.getCenter();
      const dx = clientX - center.x;
      const dy = clientY - center.y;
      let deg = Math.atan2(dy, dx) * (180 / Math.PI);
      deg = (deg + 90 + 360) % 360;
      return deg;
    }

    onPointerDown(e) {
      if (e.button !== 0 && e.pointerType === 'mouse') return;
      this.isDragging = true;
      isInteractingDial = true;
      this.element.setPointerCapture(e.pointerId);

      const deg = this.calculateAngle(e.clientX, e.clientY);
      this.setValueFromAngle(deg);

      haptics.startInteractiveTone(220 + (this.currentVal / this.max) * 220);
      haptics.playDetentTick(600);
      interactionHint.textContent = 'OPTICAL TRACKING ACTIVE';
    }

    onPointerMove(e) {
      if (!this.isDragging) return;
      const deg = this.calculateAngle(e.clientX, e.clientY);
      this.setValueFromAngle(deg);
    }

    onPointerUp(e) {
      if (!this.isDragging) return;
      this.isDragging = false;
      isInteractingDial = false;
      try {
        this.element.releasePointerCapture(e.pointerId);
      } catch (err) {
        // Ignored
      }
      haptics.stopInteractiveTone();
      interactionHint.textContent = 'READY';
    }

    onWheel(e) {
      e.preventDefault();
      const delta = e.deltaY < 0 ? this.step * 2 : -this.step * 2;
      this.setClampedValue(this.currentVal + delta);
    }

    onKeyDown(e) {
      let handled = false;
      if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
        this.setClampedValue(this.currentVal + this.step * 3);
        handled = true;
      } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
        this.setClampedValue(this.currentVal - this.step * 3);
        handled = true;
      }
      if (handled) {
        e.preventDefault();
      }
    }

    setValueFromAngle(deg) {
      const ratio = deg / 360;
      const targetVal = this.min + ratio * (this.max - this.min);
      this.setClampedValue(targetVal);
    }

    setClampedValue(val) {
      const clamped = Math.max(this.min, Math.min(this.max, val));
      const stepped = Math.round(clamped / this.step) * this.step;

      if (stepped !== this.currentVal) {
        this.currentVal = stepped;
        this.renderAngle();
        this.element.setAttribute('aria-valuenow', this.currentVal);

        // Magnetic Detent Tick check
        if (Math.abs(this.currentVal - this.lastTickVal) >= this.step) {
          haptics.playDetentTick(480 + (this.currentVal / this.max) * 260);
          this.lastTickVal = this.currentVal;
        }

        haptics.updateInteractiveTone(
          200 + (this.currentVal / this.max) * 300,
          600 + (resonanceQ / 100) * 2400
        );

        this.onUpdate(this.currentVal);
      }
    }

    renderAngle() {
      const ratio = (this.currentVal - this.min) / (this.max - this.min);
      const deg = ratio * 360;
      this.knob.style.transform = `rotate(${deg}deg)`;
    }
  }

  // --- Initialize Rotary Controls ---
  new RotaryController(dialSpatial, knobSpatial, val => {
    spatialAngle = val;
    valSpatial.textContent = `${Math.round(val)}°`;
    screenFreq.textContent = `${(300 + (val / 360) * 300).toFixed(1)} Hz`;
  }, { min: 0, max: 360, step: 2, initial: 120 });

  new RotaryController(dialResonance, knobResonance, val => {
    resonanceQ = val;
    valResonance.textContent = `${(val / 10).toFixed(1)} dB`;
  }, { min: 0, max: 100, step: 1, initial: 42 });

  // --- Waveform Canvas Vector Rendering ---
  let canvasCtx = null;
  let wavePhase = 0;

  function initWaveformCanvas() {
    if (!waveformCanvas) return;
    canvasCtx = waveformCanvas.getContext('2d');
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    requestAnimationFrame(renderWaveform);
  }

  function resizeCanvas() {
    if (!waveformCanvas) return;
    const rect = waveformCanvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    waveformCanvas.width = rect.width * dpr;
    waveformCanvas.height = rect.height * dpr;
    if (canvasCtx) {
      canvasCtx.scale(dpr, dpr);
    }
  }

  function renderWaveform() {
    if (!canvasCtx || !waveformCanvas) return;
    const rect = waveformCanvas.getBoundingClientRect();
    const w = rect.width;
    const h = rect.height;

    // Clear background
    canvasCtx.fillStyle = 'rgba(10, 11, 15, 0.4)';
    canvasCtx.fillRect(0, 0, w, h);

    // Draw Subtle Grid
    canvasCtx.strokeStyle = 'rgba(56, 189, 248, 0.08)';
    canvasCtx.lineWidth = 1;
    const gridCols = 8;
    const gridRows = 4;
    for (let c = 1; c < gridCols; c++) {
      const gx = (w / gridCols) * c;
      canvasCtx.beginPath();
      canvasCtx.moveTo(gx, 0);
      canvasCtx.lineTo(gx, h);
      canvasCtx.stroke();
    }
    for (let r = 1; r < gridRows; r++) {
      const gy = (h / gridRows) * r;
      canvasCtx.beginPath();
      canvasCtx.moveTo(0, gy);
      canvasCtx.lineTo(w, gy);
      canvasCtx.stroke();
    }

    // Dynamic Waveform Calculation
    const midY = h / 2;
    const speed = isInteractingDial ? 0.09 : 0.035;
    wavePhase += speed;

    const baseFrequency = 0.025 + (spatialAngle / 360) * 0.035;
    const amplitude = (h * 0.28) * (0.6 + (resonanceQ / 100) * 0.6);

    // Primary Channel (Cyan)
    canvasCtx.beginPath();
    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = '#38bdf8';

    for (let x = 0; x < w; x++) {
      let y = midY;
      if (activeHarmonicMode === 'binaural') {
        const p1 = Math.sin(x * baseFrequency + wavePhase);
        const p2 = Math.sin(x * baseFrequency * 2.01 + wavePhase * 1.5) * 0.35;
        y = midY + (p1 + p2) * amplitude;
      } else if (activeHarmonicMode === 'harmonic') {
        const fundamental = Math.sin(x * baseFrequency + wavePhase);
        const secondHarmonic = Math.sin(x * baseFrequency * 2 + wavePhase) * 0.5;
        const thirdHarmonic = Math.sin(x * baseFrequency * 3 + wavePhase) * 0.25;
        y = midY + (fundamental + secondHarmonic + thirdHarmonic) * (amplitude * 0.85);
      } else if (activeHarmonicMode === 'transient') {
        const decay = Math.exp(-((x % (w / 3)) / (w * 0.12)));
        const ring = Math.sin(x * baseFrequency * 4 + wavePhase) * decay;
        y = midY + ring * (amplitude * 1.3);
      }

      if (x === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }
    }
    canvasCtx.stroke();

    // Secondary Spatial Channel (Amber / Phase-offset)
    if (activeHarmonicMode === 'binaural') {
      canvasCtx.beginPath();
      canvasCtx.lineWidth = 1.5;
      canvasCtx.strokeStyle = 'rgba(245, 158, 11, 0.7)';
      const phaseOffset = (spatialAngle / 360) * Math.PI;

      for (let x = 0; x < w; x++) {
        const p1 = Math.sin(x * baseFrequency + wavePhase + phaseOffset);
        const p2 = Math.sin(x * baseFrequency * 1.99 + wavePhase * 1.5 + phaseOffset) * 0.35;
        const y = midY + (p1 + p2) * (amplitude * 0.9);

        if (x === 0) {
          canvasCtx.moveTo(x, y);
        } else {
          canvasCtx.lineTo(x, y);
        }
      }
      canvasCtx.stroke();
    }

    requestAnimationFrame(renderWaveform);
  }

  // --- Finish Switcher Handlers ---
  function setChassisFinish(finish) {
    document.body.setAttribute('data-finish', finish);

    const isObsidian = finish === 'obsidian';
    finishObsidianBtn.classList.toggle('active', isObsidian);
    finishObsidianBtn.setAttribute('aria-pressed', isObsidian ? 'true' : 'false');

    finishSilverBtn.classList.toggle('active', !isObsidian);
    finishSilverBtn.setAttribute('aria-pressed', !isObsidian ? 'true' : 'false');

    if (reserveFinishSelect) {
      reserveFinishSelect.value = finish;
    }

    haptics.playRelayClack();
  }

  finishObsidianBtn.addEventListener('click', () => setChassisFinish('obsidian'));
  finishSilverBtn.addEventListener('click', () => setChassisFinish('silver'));

  if (reserveFinishSelect) {
    reserveFinishSelect.addEventListener('change', e => {
      setChassisFinish(e.target.value);
    });
  }

  // --- Mode Switches Handlers ---
  modeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const mode = btn.dataset.mode;
      activeHarmonicMode = mode;

      modeButtons.forEach(b => {
        const isSelected = b === btn;
        b.classList.toggle('active', isSelected);
        b.setAttribute('aria-checked', isSelected ? 'true' : 'false');
      });

      screenMode.textContent = mode.toUpperCase() + (mode === 'binaural' ? ' SPATIAL' : ' SPECTRUM');
      haptics.playSwitchClick();
    });
  });

  // --- Haptic Sound Master Toggle ---
  hapticAudioToggle.addEventListener('click', () => {
    haptics.enabled = !haptics.enabled;
    if (haptics.enabled) {
      audioStatusGlyph.textContent = '🔊';
      hapticAudioToggle.setAttribute('title', 'Audio feedback enabled');
      haptics.playSwitchClick();
      powerStateText.textContent = 'ACTIVE 96k';
    } else {
      audioStatusGlyph.textContent = '🔇';
      hapticAudioToggle.setAttribute('title', 'Audio feedback muted');
      powerStateText.textContent = 'MUTED 96k';
    }
  });

  // --- Pre-order Form Submission ---
  if (reserveForm) {
    reserveForm.addEventListener('submit', e => {
      e.preventDefault();

      let valid = true;
      nameError.textContent = '';
      emailError.textContent = '';

      const nameInput = document.getElementById('reserve-name');
      const emailInput = document.getElementById('reserve-email');

      if (!nameInput.value.trim()) {
        nameError.textContent = 'Please provide your full name for the allocation registry.';
        nameInput.focus();
        valid = false;
      }

      const emailVal = emailInput.value.trim();
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailVal || !emailRegex.test(emailVal)) {
        emailError.textContent = 'Please enter a valid email address for delivery confirmation.';
        if (valid) emailInput.focus();
        valid = false;
      }

      if (valid) {
        haptics.playSuccessChime();
        formSuccessBanner.classList.add('visible');
        formSuccessBanner.setAttribute('aria-hidden', 'false');

        const submitBtn = document.getElementById('submit-reserve-btn');
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = 'Allocation Secured';
        }

        const successBody = document.getElementById('success-message-body');
        if (successBody) {
          const randomSerial = Math.floor(1000 + Math.random() * 9000);
          successBody.textContent = `Batch 01 allocation #${randomSerial} confirmed for ${nameInput.value.trim()}. We have transmitted the reservation key to ${emailVal}.`;
        }
      }
    });
  }

  // --- Startup Initialization ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWaveformCanvas);
  } else {
    initWaveformCanvas();
  }
})();
