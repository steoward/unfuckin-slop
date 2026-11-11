/**
 * STRATA Model 01 - State-of-the-Art Physical Acoustic Console Engine
 * Built under Unfuckin-Slop discipline and synthesized from CollectUI & Pixlpin inspirations.
 */

(function () {
  'use strict';

  // --- Multimodal Haptic Audio Synthesizer (Web Audio API) ---
  class HapticAudioEngine {
    constructor() {
      this.ctx = null;
      this.enabled = true;
      this.droneOsc = null;
      this.droneFilter = null;
      this.droneGain = null;
      this.isDroneActive = false;
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

    playDetentTick(freq = 540) {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, now);
        osc.frequency.exponentialRampToValueAtTime(140, now + 0.018);

        gain.gain.setValueAtTime(0.045, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.018);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.018);
      } catch (err) {
        // Silently catch audio policy blocks
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
        osc.frequency.setValueAtTime(360, now);
        osc.frequency.exponentialRampToValueAtTime(90, now + 0.024);

        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.024);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.024);
      } catch (err) {
        // Silently catch audio policy blocks
      }
    }

    playRelayClack() {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        [0, 0.012].forEach((offset, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          const t = now + offset;

          osc.type = 'square';
          osc.frequency.setValueAtTime(idx === 0 ? 460 : 260, t);
          osc.frequency.exponentialRampToValueAtTime(70, t + 0.016);

          gain.gain.setValueAtTime(0.035, t);
          gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.016);

          osc.connect(gain);
          gain.connect(this.ctx.destination);

          osc.start(t);
          osc.stop(t + 0.016);
        });
      } catch (err) {
        // Silently catch audio policy blocks
      }
    }

    playAllocationChime() {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        const chord = [523.25, 659.25, 783.99, 1046.5]; // C Major Chord
        chord.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          const startT = now + idx * 0.045;

          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, startT);

          gain.gain.setValueAtTime(0.04, startT);
          gain.gain.exponentialRampToValueAtTime(0.0001, startT + 0.38);

          osc.connect(gain);
          gain.connect(this.ctx.destination);

          osc.start(startT);
          osc.stop(startT + 0.38);
        });
      } catch (err) {
        // Silently catch audio policy blocks
      }
    }

    startAcousticTone(freq = 220) {
      if (!this.enabled || this.isDroneActive) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        this.droneOsc = this.ctx.createOscillator();
        this.droneFilter = this.ctx.createBiquadFilter();
        this.droneGain = this.ctx.createGain();

        this.droneOsc.type = 'sawtooth';
        this.droneOsc.frequency.setValueAtTime(freq, this.ctx.currentTime);

        this.droneFilter.type = 'lowpass';
        this.droneFilter.frequency.setValueAtTime(800, this.ctx.currentTime);
        this.droneFilter.Q.setValueAtTime(3.5, this.ctx.currentTime);

        this.droneGain.gain.setValueAtTime(0.001, this.ctx.currentTime);
        this.droneGain.gain.exponentialRampToValueAtTime(0.03, this.ctx.currentTime + 0.06);

        this.droneOsc.connect(this.droneFilter);
        this.droneFilter.connect(this.droneGain);
        this.droneGain.connect(this.ctx.destination);

        this.droneOsc.start();
        this.isDroneActive = true;
      } catch (err) {
        // Silently catch
      }
    }

    updateAcousticTone(freq, cutoff) {
      if (!this.isDroneActive || !this.ctx) return;
      try {
        const now = this.ctx.currentTime;
        if (this.droneOsc) {
          this.droneOsc.frequency.setTargetAtTime(freq, now, 0.03);
        }
        if (this.droneFilter) {
          this.droneFilter.frequency.setTargetAtTime(cutoff, now, 0.03);
        }
      } catch (err) {
        // Silently catch
      }
    }

    stopAcousticTone() {
      if (!this.isDroneActive || !this.ctx) return;
      try {
        const now = this.ctx.currentTime;
        if (this.droneGain) {
          this.droneGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.05);
        }
        setTimeout(() => {
          if (this.droneOsc) {
            this.droneOsc.stop();
            this.droneOsc.disconnect();
            this.droneOsc = null;
          }
          this.isDroneActive = false;
        }, 60);
      } catch (err) {
        this.isDroneActive = false;
      }
    }
  }

  const haptics = new HapticAudioEngine();

  // --- Instrument State ---
  let spatialAngle = 120; // 0 to 360 deg
  let resonanceQ = 42;    // 0 to 100 (4.2 dB)
  let activeHarmonicMode = 'binaural';
  let isManipulatingDial = false;

  // --- DOM Elements ---
  const radarContainer = document.getElementById('radar-container');
  const knobSpatial = document.getElementById('knob-spatial');
  const spatialRadarCanvas = document.getElementById('spatial-radar-canvas');
  const readoutSpatialAngle = document.getElementById('readout-spatial-angle');

  const dialResonance = document.getElementById('dial-resonance');
  const knobResonance = document.getElementById('knob-resonance');
  const readoutResonanceQ = document.getElementById('readout-resonance-q');

  const vectorOscilloscopeCanvas = document.getElementById('vector-oscilloscope-canvas');
  const hudModeDisplay = document.getElementById('hud-mode-display');
  const hudHarmonicFreq = document.getElementById('hud-harmonic-freq');
  const hudImpedance = document.getElementById('hud-impedance');
  const deckTelemetryStatus = document.getElementById('deck-telemetry-status');

  const meterLeft = document.getElementById('meter-left');
  const meterRight = document.getElementById('meter-right');

  const btnFinishObsidian = document.getElementById('btn-finish-obsidian');
  const btnFinishSilver = document.getElementById('btn-finish-silver');
  const selectFinishChoice = document.getElementById('select-finish-choice');
  const audioFeedbackBtn = document.getElementById('audio-feedback-btn');
  const audioIconDisplay = document.getElementById('audio-icon-display');

  const modeSwitches = document.querySelectorAll('.tactile-switch');
  const architectureTabs = document.querySelectorAll('.terminal-tab');

  const allocationForm = document.getElementById('allocation-form');
  const inputClientName = document.getElementById('input-client-name');
  const inputClientEmail = document.getElementById('input-client-email');
  const feedbackName = document.getElementById('feedback-name');
  const feedbackEmail = document.getElementById('feedback-email');
  const allocationSuccessReceipt = document.getElementById('allocation-success-receipt');
  const receiptMessageText = document.getElementById('receipt-message-text');
  const btnSubmitAllocation = document.getElementById('btn-submit-allocation');

  // --- Rotary Knob Controller ---
  class DialController {
    constructor(element, knob, onValueChange, options = {}) {
      this.element = element;
      this.knob = knob;
      this.onValueChange = onValueChange;
      this.min = options.min ?? 0;
      this.max = options.max ?? 360;
      this.step = options.step ?? 1;
      this.val = options.initial ?? 0;
      this.isDragging = false;
      this.lastTickVal = this.val;

      this.init();
    }

    init() {
      this.render();
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

    getAngle(clientX, clientY) {
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
      isManipulatingDial = true;
      this.element.setPointerCapture(e.pointerId);

      const deg = this.getAngle(e.clientX, e.clientY);
      this.updateFromAngle(deg);

      haptics.startAcousticTone(220 + (this.val / this.max) * 220);
      haptics.playDetentTick(580);
      if (deckTelemetryStatus) {
        deckTelemetryStatus.textContent = 'OPTICAL DETENT: ROTATING';
      }
    }

    onPointerMove(e) {
      if (!this.isDragging) return;
      const deg = this.getAngle(e.clientX, e.clientY);
      this.updateFromAngle(deg);
    }

    onPointerUp(e) {
      if (!this.isDragging) return;
      this.isDragging = false;
      isManipulatingDial = false;
      try {
        this.element.releasePointerCapture(e.pointerId);
      } catch (err) {
        // Ignored
      }
      haptics.stopAcousticTone();
      if (deckTelemetryStatus) {
        deckTelemetryStatus.textContent = 'MAGNETIC BRAKE: ENGAGED';
      }
    }

    onWheel(e) {
      e.preventDefault();
      const delta = e.deltaY < 0 ? this.step * 2 : -this.step * 2;
      this.setClamped(this.val + delta);
    }

    onKeyDown(e) {
      let handled = false;
      if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
        this.setClamped(this.val + this.step * 3);
        handled = true;
      } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
        this.setClamped(this.val - this.step * 3);
        handled = true;
      }
      if (handled) {
        e.preventDefault();
      }
    }

    updateFromAngle(deg) {
      const ratio = deg / 360;
      const target = this.min + ratio * (this.max - this.min);
      this.setClamped(target);
    }

    setClamped(target) {
      const clamped = Math.max(this.min, Math.min(this.max, target));
      const stepped = Math.round(clamped / this.step) * this.step;

      if (stepped !== this.val) {
        this.val = stepped;
        this.render();
        this.element.setAttribute('aria-valuenow', this.val);

        if (Math.abs(this.val - this.lastTickVal) >= this.step) {
          haptics.playDetentTick(480 + (this.val / this.max) * 280);
          this.lastTickVal = this.val;
        }

        haptics.updateAcousticTone(
          200 + (this.val / this.max) * 320,
          600 + (resonanceQ / 100) * 2400
        );

        this.onValueChange(this.val);
      }
    }

    render() {
      const ratio = (this.val - this.min) / (this.max - this.min);
      const deg = ratio * 360;
      this.knob.style.transform = `rotate(${deg}deg)`;
    }
  }

  // --- Initialize Dials ---
  new DialController(radarContainer, knobSpatial, val => {
    spatialAngle = val;
    readoutSpatialAngle.textContent = `${Math.round(val)}°`;
    hudHarmonicFreq.textContent = `${(320 + (val / 360) * 280).toFixed(1)} Hz`;
  }, { min: 0, max: 360, step: 2, initial: 120 });

  new DialController(dialResonance, knobResonance, val => {
    resonanceQ = val;
    readoutResonanceQ.textContent = `${(val / 10).toFixed(1)} dB`;
    hudImpedance.textContent = `${Math.round(200 + (val / 100) * 600)} Ω`;
  }, { min: 0, max: 100, step: 1, initial: 42 });

  // --- Circular Spatial Radar Canvas ---
  let radarCtx = null;

  function initRadarCanvas() {
    if (!spatialRadarCanvas) return;
    radarCtx = spatialRadarCanvas.getContext('2d');
    renderRadar();
  }

  function renderRadar() {
    if (!radarCtx || !spatialRadarCanvas) return;
    const w = spatialRadarCanvas.width;
    const h = spatialRadarCanvas.height;
    const cx = w / 2;
    const cy = h / 2;

    radarCtx.clearRect(0, 0, w, h);

    // Concentric Reticle Rings
    radarCtx.strokeStyle = 'rgba(56, 189, 248, 0.15)';
    radarCtx.lineWidth = 1;
    [30, 52, 74].forEach(r => {
      radarCtx.beginPath();
      radarCtx.arc(cx, cy, r, 0, Math.PI * 2);
      radarCtx.stroke();
    });

    // Crosshairs
    radarCtx.beginPath();
    radarCtx.moveTo(cx, 4);
    radarCtx.lineTo(cx, h - 4);
    radarCtx.moveTo(4, cy);
    radarCtx.lineTo(w - 4, cy);
    radarCtx.stroke();

    // Sweeping Spatial Beam
    const rad = (spatialAngle - 90) * (Math.PI / 180);
    const beamLength = 72;
    const bx = cx + Math.cos(rad) * beamLength;
    const by = cy + Math.sin(rad) * beamLength;

    radarCtx.strokeStyle = '#ff5722';
    radarCtx.lineWidth = 2;
    radarCtx.beginPath();
    radarCtx.moveTo(cx, cy);
    radarCtx.lineTo(bx, by);
    radarCtx.stroke();

    // Beam Target Dot
    radarCtx.fillStyle = '#ff5722';
    radarCtx.beginPath();
    radarCtx.arc(bx, by, 3.5, 0, Math.PI * 2);
    radarCtx.fill();

    requestAnimationFrame(renderRadar);
  }

  // --- Real-Time Vector Oscilloscope Canvas ---
  let oscCtx = null;
  let wavePhase = 0;

  function initOscilloscope() {
    if (!vectorOscilloscopeCanvas) return;
    oscCtx = vectorOscilloscopeCanvas.getContext('2d');
    resizeOscilloscope();
    window.addEventListener('resize', resizeOscilloscope);
    requestAnimationFrame(renderOscilloscope);
  }

  function resizeOscilloscope() {
    if (!vectorOscilloscopeCanvas) return;
    const rect = vectorOscilloscopeCanvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    vectorOscilloscopeCanvas.width = rect.width * dpr;
    vectorOscilloscopeCanvas.height = rect.height * dpr;
    if (oscCtx) {
      oscCtx.scale(dpr, dpr);
    }
  }

  function renderOscilloscope() {
    if (!oscCtx || !vectorOscilloscopeCanvas) return;
    const rect = vectorOscilloscopeCanvas.getBoundingClientRect();
    const w = rect.width;
    const h = rect.height;

    // Canvas Background
    oscCtx.fillStyle = 'rgba(10, 12, 16, 0.45)';
    oscCtx.fillRect(0, 0, w, h);

    // Coordinate Grid Lines
    oscCtx.strokeStyle = 'rgba(56, 189, 248, 0.08)';
    oscCtx.lineWidth = 1;
    const cols = 8;
    const rows = 4;
    for (let c = 1; c < cols; c++) {
      const gx = (w / cols) * c;
      oscCtx.beginPath();
      oscCtx.moveTo(gx, 0);
      oscCtx.lineTo(gx, h);
      oscCtx.stroke();
    }
    for (let r = 1; r < rows; r++) {
      const gy = (h / rows) * r;
      oscCtx.beginPath();
      oscCtx.moveTo(0, gy);
      oscCtx.lineTo(w, gy);
      oscCtx.stroke();
    }

    const midY = h / 2;
    const speed = isManipulatingDial ? 0.08 : 0.032;
    wavePhase += speed;

    const baseFrequency = 0.024 + (spatialAngle / 360) * 0.038;
    const amplitude = (h * 0.28) * (0.6 + (resonanceQ / 100) * 0.55);

    // Primary Channel (Cyan)
    oscCtx.beginPath();
    oscCtx.lineWidth = 2;
    oscCtx.strokeStyle = '#38bdf8';

    for (let x = 0; x < w; x++) {
      let y = midY;
      if (activeHarmonicMode === 'binaural') {
        const p1 = Math.sin(x * baseFrequency + wavePhase);
        const p2 = Math.sin(x * baseFrequency * 2.01 + wavePhase * 1.5) * 0.35;
        y = midY + (p1 + p2) * amplitude;
      } else if (activeHarmonicMode === 'harmonic') {
        const f1 = Math.sin(x * baseFrequency + wavePhase);
        const f2 = Math.sin(x * baseFrequency * 2 + wavePhase) * 0.5;
        const f3 = Math.sin(x * baseFrequency * 3 + wavePhase) * 0.25;
        y = midY + (f1 + f2 + f3) * (amplitude * 0.85);
      } else if (activeHarmonicMode === 'transient') {
        const decay = Math.exp(-((x % (w / 3)) / (w * 0.12)));
        const ring = Math.sin(x * baseFrequency * 4 + wavePhase) * decay;
        y = midY + ring * (amplitude * 1.3);
      }

      if (x === 0) {
        oscCtx.moveTo(x, y);
      } else {
        oscCtx.lineTo(x, y);
      }
    }
    oscCtx.stroke();

    // Secondary Phase Channel (Amber) for Binaural Mode
    if (activeHarmonicMode === 'binaural') {
      oscCtx.beginPath();
      oscCtx.lineWidth = 1.5;
      oscCtx.strokeStyle = 'rgba(245, 158, 11, 0.75)';
      const phaseOffset = (spatialAngle / 360) * Math.PI;

      for (let x = 0; x < w; x++) {
        const p1 = Math.sin(x * baseFrequency + wavePhase + phaseOffset);
        const p2 = Math.sin(x * baseFrequency * 1.99 + wavePhase * 1.5 + phaseOffset) * 0.35;
        const y = midY + (p1 + p2) * (amplitude * 0.88);

        if (x === 0) {
          oscCtx.moveTo(x, y);
        } else {
          oscCtx.lineTo(x, y);
        }
      }
      oscCtx.stroke();
    }

    requestAnimationFrame(renderOscilloscope);
  }

  // --- Segmented LED VU Meter Pulse ---
  function updateVUMeters() {
    if (!meterLeft || !meterRight) return;

    const leftSegments = meterLeft.querySelectorAll('.meter-segment');
    const rightSegments = meterRight.querySelectorAll('.meter-segment');

    // Modulate based on resonance and random transient burst
    const baseEnergy = 0.5 + (resonanceQ / 100) * 0.4;
    const lLevel = Math.min(8, Math.floor(baseEnergy * 7 + Math.random() * 2));
    const rLevel = Math.min(8, Math.floor(baseEnergy * 7 + Math.random() * 2));

    leftSegments.forEach((seg, idx) => {
      seg.classList.toggle('active', idx < lLevel);
    });

    rightSegments.forEach((seg, idx) => {
      seg.classList.toggle('active', idx < rLevel);
    });
  }
  setInterval(updateVUMeters, 120);

  // --- Architecture Exploded Layer Switcher ---
  const ARCH_LAYERS = {
    monobloc: {
      coord: 'STRUCTURAL LAYER 01 // CNC BILLET',
      spec: 'TOLERANCE ±0.015 mm',
      title: 'Seamless Aerospace Magnesium Monobloc',
      desc: 'High-pressure magnesium alloy AZ91D offers 33% lower density than aluminum with exceptional damping characteristics, suppressing electromagnetic interference and mechanical microphonics across all audio bandwidths.',
      stats: [
        { val: '680 g', label: 'Net Chassis Mass' },
        { val: '242 × 158 × 32 mm', label: 'Exterior Dimensions' },
        { val: '0.00012%', label: 'Residual Harmonic Distortion' }
      ]
    },
    faraday: {
      coord: 'ISOLATION LAYER 02 // FARADAY VAULT',
      spec: 'SHIELDING > 115 dB',
      title: 'Hermetically Sealed Analog Faraday Chambers',
      desc: 'Input transformers and Lundahl step-up stages are isolated in machined chambers with pure oxygen-free copper gaskets, preventing digital processor clock ripple from entering the analog domain.',
      stats: [
        { val: '132.4 dB', label: 'Signal to Noise Ratio' },
        { val: '< 42 fs', label: 'Master Clock Jitter' },
        { val: '> 126.5 dB', label: 'Crosstalk Rejection' }
      ]
    },
    rotary: {
      coord: 'CONTROL LAYER 03 // NON-CONTACT ROTORS',
      spec: 'RESOLUTION 4,096 CPR',
      title: 'Optical Brushless Rotor Assembly',
      desc: 'Infrared optical encoders with micro-perforated code discs track rotary angles with sub-millisecond precision. Integrated neodymium electromagnets dynamically simulate variable mechanical drag and tactile detents.',
      stats: [
        { val: '0 to 120 mN·m', label: 'Variable Magnetic Drag' },
        { val: '0.12 ms', label: 'Encoder Response Time' },
        { val: 'Infinite', label: 'Contactless Lifespan' }
      ]
    },
    thermal: {
      coord: 'THERMAL LAYER 04 // PASSIVE SIPHON',
      spec: 'HEAT FLUX 18 W / m·K',
      title: 'Passive Magnesium Thermal Siphon Deck',
      desc: 'The monobloc chassis acts as a unified heat sink, silently drawing heat away from the class-A discrete operational amplifiers without fans or mechanical air circulation.',
      stats: [
        { val: '0.0 dBA', label: 'Acoustic Noise Floor' },
        { val: '38° C', label: 'Nominal Operating Temp' },
        { val: '15 W', label: 'Thunderbolt 4 Bus Power' }
      ]
    }
  };

  architectureTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const layerKey = tab.dataset.layer;
      const data = ARCH_LAYERS[layerKey];
      if (!data) return;

      architectureTabs.forEach(t => {
        const isSelected = t === tab;
        t.classList.toggle('active', isSelected);
        t.setAttribute('aria-selected', isSelected ? 'true' : 'false');
      });

      document.getElementById('layer-chip-id').textContent = data.coord;
      document.getElementById('layer-chip-spec').textContent = data.spec;
      document.getElementById('layer-title').textContent = data.title;
      document.getElementById('layer-desc').textContent = data.desc;

      const specsContainer = document.getElementById('layer-specs-row');
      specsContainer.innerHTML = '';
      data.stats.forEach(s => {
        const div = document.createElement('div');
        div.className = 'layer-stat';
        div.innerHTML = `<span class="stat-value">${s.val}</span><span class="stat-label">${s.label}</span>`;
        specsContainer.appendChild(div);
      });

      haptics.playSwitchClick();
    });
  });

  // --- Finish Switcher Handlers ---
  function applyChassisFinish(finish) {
    document.body.setAttribute('data-finish', finish);

    const isObsidian = finish === 'obsidian';
    btnFinishObsidian.classList.toggle('active', isObsidian);
    btnFinishObsidian.setAttribute('aria-pressed', isObsidian ? 'true' : 'false');

    btnFinishSilver.classList.toggle('active', !isObsidian);
    btnFinishSilver.setAttribute('aria-pressed', !isObsidian ? 'true' : 'false');

    if (selectFinishChoice) {
      selectFinishChoice.value = finish;
    }

    haptics.playRelayClack();
  }

  btnFinishObsidian.addEventListener('click', () => applyChassisFinish('obsidian'));
  btnFinishSilver.addEventListener('click', () => applyChassisFinish('silver'));

  if (selectFinishChoice) {
    selectFinishChoice.addEventListener('change', e => {
      applyChassisFinish(e.target.value);
    });
  }

  // --- Mode Switches Handlers ---
  modeSwitches.forEach(btn => {
    btn.addEventListener('click', () => {
      const mode = btn.dataset.mode;
      activeHarmonicMode = mode;

      modeSwitches.forEach(b => {
        const isSelected = b === btn;
        b.classList.toggle('active', isSelected);
        b.setAttribute('aria-checked', isSelected ? 'true' : 'false');
      });

      hudModeDisplay.textContent = (mode === 'binaural' ? 'BINAURAL VECTOR' : mode === 'harmonic' ? 'HARMONIC SPECTRUM' : 'TRANSIENT SCOPE');
      haptics.playSwitchClick();
    });
  });

  // --- Haptic Sound Toggle ---
  audioFeedbackBtn.addEventListener('click', () => {
    haptics.enabled = !haptics.enabled;
    if (haptics.enabled) {
      audioIconDisplay.textContent = '🔊';
      audioFeedbackBtn.setAttribute('title', 'Audio feedback enabled');
      haptics.playSwitchClick();
    } else {
      audioIconDisplay.textContent = '🔇';
      audioFeedbackBtn.setAttribute('title', 'Audio feedback muted');
    }
  });

  // --- Allocation Form Handling ---
  if (allocationForm) {
    allocationForm.addEventListener('submit', e => {
      e.preventDefault();

      let valid = true;
      feedbackName.textContent = '';
      feedbackEmail.textContent = '';

      if (!inputClientName.value.trim()) {
        feedbackName.textContent = 'Please enter your client or studio name.';
        inputClientName.focus();
        valid = false;
      }

      const emailVal = inputClientEmail.value.trim();
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailVal || !emailRegex.test(emailVal)) {
        feedbackEmail.textContent = 'Please enter a valid studio email address for the hardware allocation key.';
        if (valid) inputClientEmail.focus();
        valid = false;
      }

      if (valid) {
        haptics.playAllocationChime();
        allocationSuccessReceipt.classList.add('visible');
        allocationSuccessReceipt.setAttribute('aria-hidden', 'false');

        if (btnSubmitAllocation) {
          btnSubmitAllocation.disabled = true;
          btnSubmitAllocation.textContent = 'Production Slot Secured';
        }

        if (receiptMessageText) {
          const serial = Math.floor(1000 + Math.random() * 9000);
          receiptMessageText.textContent = `Batch 01 allocation #${serial} reserved for ${inputClientName.value.trim()}. Hardware key dispatched to ${emailVal}.`;
        }
      }
    });
  }

  // --- Boot Sequence ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initRadarCanvas();
      initOscilloscope();
    });
  } else {
    initRadarCanvas();
    initOscilloscope();
  }
})();
