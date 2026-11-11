/**
 * AETHER OS - Spatial Neural Computing Workstation Engine
 * Engineered under Unfuckin-Slop discipline and CollectUI / Pixlpin inspirations.
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

    playDetentTick(freq = 560) {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, now);
        osc.frequency.exponentialRampToValueAtTime(140, now + 0.016);

        gain.gain.setValueAtTime(0.045, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.016);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.016);
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
        osc.frequency.setValueAtTime(380, now);
        osc.frequency.exponentialRampToValueAtTime(95, now + 0.022);

        gain.gain.setValueAtTime(0.055, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.022);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.022);
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
          osc.frequency.setValueAtTime(idx === 0 ? 480 : 280, t);
          osc.frequency.exponentialRampToValueAtTime(75, t + 0.015);

          gain.gain.setValueAtTime(0.035, t);
          gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.015);

          osc.connect(gain);
          gain.connect(this.ctx.destination);

          osc.start(t);
          osc.stop(t + 0.015);
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
        const chord = [523.25, 659.25, 783.99, 1046.5, 1318.5]; // C Major 9
        chord.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          const startT = now + idx * 0.045;

          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, startT);

          gain.gain.setValueAtTime(0.04, startT);
          gain.gain.exponentialRampToValueAtTime(0.0001, startT + 0.45);

          osc.connect(gain);
          gain.connect(this.ctx.destination);

          osc.start(startT);
          osc.stop(startT + 0.45);
        });
      } catch (err) {
        // Silently catch audio policy blocks
      }
    }

    startAcousticTone(freq = 260) {
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
        this.droneFilter.frequency.setValueAtTime(900, this.ctx.currentTime);
        this.droneFilter.Q.setValueAtTime(3.8, this.ctx.currentTime);

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

  // --- Workstation State Variables ---
  let orbitalAngle = 140; // 0 to 360 deg
  let resonanceQ = 48;    // 0 to 100 (4.8 dB)
  let activeAlgorithm = 'neural';
  let isManipulatingDial = false;

  // --- 3D Spatial Vector Matrix Math ---
  let rotX = 0.25;
  let rotY = 0.45;
  let targetRotX = 0.25;
  let targetRotY = 0.45;
  let velRotX = 0;
  let velRotY = 0;
  let isDraggingCanvas = false;
  let lastMouseX = 0;
  let lastMouseY = 0;

  // --- DOM Elements ---
  const cosmicCanvas = document.getElementById('cosmic-canvas');
  const spatialCanvas = document.getElementById('spatial-canvas');
  const hudModeReadout = document.getElementById('hud-mode-readout');
  const hudTensorFrequency = document.getElementById('hud-tensor-frequency');
  const hudCoordinates = document.getElementById('hud-coordinates');
  const hudFpsCounter = document.getElementById('hud-fps-counter');
  const busMeter = document.getElementById('bus-meter');

  const dialOrbital = document.getElementById('dial-orbital');
  const rotorOrbital = document.getElementById('rotor-orbital');
  const metricOrbitalAngle = document.getElementById('metric-orbital-angle');

  const dialResonance = document.getElementById('dial-resonance');
  const rotorResonance = document.getElementById('rotor-resonance');
  const metricResonanceQ = document.getElementById('metric-resonance-q');

  const finishTitaniumBtn = document.getElementById('finish-titanium');
  const finishObsidianBtn = document.getElementById('finish-obsidian');
  const chassisFinishChoice = document.getElementById('chassis-finish-choice');
  const hapticAudioSwitch = document.getElementById('haptic-audio-switch');
  const audioStateGlyph = document.getElementById('audio-state-glyph');

  const modeSwitchButtons = document.querySelectorAll('.mode-switch-btn');
  const explorerTabs = document.querySelectorAll('.explorer-tab');

  const reservationForm = document.getElementById('reservation-form');
  const clientNameInput = document.getElementById('client-name');
  const clientEmailInput = document.getElementById('client-email');
  const nameErrorDisplay = document.getElementById('name-error-display');
  const emailErrorDisplay = document.getElementById('email-error-display');
  const allocationSuccessModal = document.getElementById('allocation-success-modal');
  const successDynamicMessage = document.getElementById('success-dynamic-message');
  const btnConfirmReservation = document.getElementById('btn-confirm-reservation');

  // --- Rotary Knob Controller ---
  class RotaryKnob {
    constructor(element, rotor, onChange, options = {}) {
      this.element = element;
      this.rotor = rotor;
      this.onChange = onChange;
      this.min = options.min ?? 0;
      this.max = options.max ?? 360;
      this.step = options.step ?? 1;
      this.value = options.initial ?? 0;
      this.lastTickVal = this.value;
      this.isDragging = false;

      this.init();
    }

    init() {
      this.render();
      this.element.addEventListener('pointerdown', this.onDown.bind(this));
      window.addEventListener('pointermove', this.onMove.bind(this));
      window.addEventListener('pointerup', this.onUp.bind(this));
      window.addEventListener('pointercancel', this.onUp.bind(this));
      this.element.addEventListener('wheel', this.onWheel.bind(this), { passive: false });
      this.element.addEventListener('keydown', this.onKey.bind(this));
    }

    getCenter() {
      const rect = this.element.getBoundingClientRect();
      return {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2
      };
    }

    getAngle(clientX, clientY) {
      const c = this.getCenter();
      const dx = clientX - c.x;
      const dy = clientY - c.y;
      let deg = Math.atan2(dy, dx) * (180 / Math.PI);
      deg = (deg + 90 + 360) % 360;
      return deg;
    }

    onDown(e) {
      if (e.button !== 0 && e.pointerType === 'mouse') return;
      this.isDragging = true;
      isManipulatingDial = true;
      this.element.setPointerCapture(e.pointerId);

      const deg = this.getAngle(e.clientX, e.clientY);
      this.updateAngle(deg);

      haptics.startAcousticTone(240 + (this.value / this.max) * 240);
      haptics.playDetentTick(620);
    }

    onMove(e) {
      if (!this.isDragging) return;
      const deg = this.getAngle(e.clientX, e.clientY);
      this.updateAngle(deg);
    }

    onUp(e) {
      if (!this.isDragging) return;
      this.isDragging = false;
      isManipulatingDial = false;
      try {
        this.element.releasePointerCapture(e.pointerId);
      } catch (err) {
        // Ignored
      }
      haptics.stopAcousticTone();
    }

    onWheel(e) {
      e.preventDefault();
      const delta = e.deltaY < 0 ? this.step * 2 : -this.step * 2;
      this.setClamped(this.value + delta);
    }

    onKey(e) {
      let handled = false;
      if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
        this.setClamped(this.value + this.step * 3);
        handled = true;
      } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
        this.setClamped(this.value - this.step * 3);
        handled = true;
      }
      if (handled) {
        e.preventDefault();
      }
    }

    updateAngle(deg) {
      const ratio = deg / 360;
      const target = this.min + ratio * (this.max - this.min);
      this.setClamped(target);
    }

    setClamped(target) {
      const clamped = Math.max(this.min, Math.min(this.max, target));
      const stepped = Math.round(clamped / this.step) * this.step;

      if (stepped !== this.value) {
        this.value = stepped;
        this.render();
        this.element.setAttribute('aria-valuenow', this.value);

        if (Math.abs(this.value - this.lastTickVal) >= this.step) {
          haptics.playDetentTick(500 + (this.value / this.max) * 280);
          this.lastTickVal = this.value;
        }

        haptics.updateAcousticTone(
          220 + (this.value / this.max) * 360,
          700 + (resonanceQ / 100) * 2600
        );

        this.onChange(this.value);
      }
    }

    render() {
      const ratio = (this.value - this.min) / (this.max - this.min);
      const deg = ratio * 360;
      this.rotor.style.transform = `rotate(${deg}deg)`;
    }
  }

  // --- Initialize Rotary Dials ---
  new RotaryKnob(dialOrbital, rotorOrbital, val => {
    orbitalAngle = val;
    metricOrbitalAngle.textContent = `${Math.round(val)}°`;
    hudTensorFrequency.textContent = `RESONANCE: ${(320 + (val / 360) * 340).toFixed(1)} Hz`;
    targetRotY = (val / 360) * Math.PI * 2;
  }, { min: 0, max: 360, step: 2, initial: 140 });

  new RotaryKnob(dialResonance, rotorResonance, val => {
    resonanceQ = val;
    metricResonanceQ.textContent = `${(val / 10).toFixed(1)} dB`;
  }, { min: 0, max: 100, step: 1, initial: 48 });

  // --- Background Cosmic Coordinate Matrix ---
  let cosmicCtx = null;
  const cosmicNodes = [];

  function initCosmicBackdrop() {
    if (!cosmicCanvas) return;
    cosmicCtx = cosmicCanvas.getContext('2d');
    resizeCosmicCanvas();
    window.addEventListener('resize', resizeCosmicCanvas);

    for (let i = 0; i < 48; i++) {
      cosmicNodes.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        radius: Math.random() * 1.5 + 0.5
      });
    }

    renderCosmic();
  }

  function resizeCosmicCanvas() {
    if (!cosmicCanvas) return;
    cosmicCanvas.width = window.innerWidth;
    cosmicCanvas.height = window.innerHeight;
  }

  function renderCosmic() {
    if (!cosmicCtx || !cosmicCanvas) return;
    const w = cosmicCanvas.width;
    const h = cosmicCanvas.height;

    cosmicCtx.clearRect(0, 0, w, h);
    cosmicCtx.fillStyle = 'rgba(167, 139, 250, 0.4)';
    cosmicCtx.strokeStyle = 'rgba(45, 212, 191, 0.04)';
    cosmicCtx.lineWidth = 1;

    for (let i = 0; i < cosmicNodes.length; i++) {
      const n = cosmicNodes[i];
      n.x += n.vx;
      n.y += n.vy;

      if (n.x < 0) n.x = w;
      if (n.x > w) n.x = 0;
      if (n.y < 0) n.y = h;
      if (n.y > h) n.y = 0;

      cosmicCtx.beginPath();
      cosmicCtx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
      cosmicCtx.fill();

      for (let j = i + 1; j < cosmicNodes.length; j++) {
        const n2 = cosmicNodes[j];
        const dx = n.x - n2.x;
        const dy = n.y - n2.y;
        const dist = dx * dx + dy * dy;
        if (dist < 14000) {
          cosmicCtx.beginPath();
          cosmicCtx.moveTo(n.x, n.y);
          cosmicCtx.lineTo(n2.x, n2.y);
          cosmicCtx.stroke();
        }
      }
    }

    requestAnimationFrame(renderCosmic);
  }

  // --- 3D Interactive Spatial Orbital Vector Canvas ---
  let spatialCtx = null;
  let lastFrameTime = performance.now();
  let smoothFps = 120;

  // Generate 3D Orbital Points
  const SPATIAL_POINTS = [];
  const TOTAL_POINTS = 160;
  for (let i = 0; i < TOTAL_POINTS; i++) {
    const theta = Math.acos(1 - 2 * (i / TOTAL_POINTS));
    const phi = Math.PI * (1 + Math.sqrt(5)) * i;
    const r = 95;
    SPATIAL_POINTS.push({
      ox: r * Math.sin(theta) * Math.cos(phi),
      oy: r * Math.sin(theta) * Math.sin(phi),
      oz: r * Math.cos(theta),
      phase: Math.random() * Math.PI * 2
    });
  }

  function initSpatialCanvas() {
    if (!spatialCanvas) return;
    spatialCtx = spatialCanvas.getContext('2d');
    resizeSpatialCanvas();
    window.addEventListener('resize', resizeSpatialCanvas);

    // Mouse drag rotation on 3D canvas
    spatialCanvas.addEventListener('pointerdown', e => {
      isDraggingCanvas = true;
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
      spatialCanvas.setPointerCapture(e.pointerId);
      haptics.playSwitchClick();
    });

    window.addEventListener('pointermove', e => {
      if (!isDraggingCanvas) return;
      const dx = e.clientX - lastMouseX;
      const dy = e.clientY - lastMouseY;
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;

      velRotY = dx * 0.008;
      velRotX = dy * 0.008;
      targetRotY += velRotY;
      targetRotX += velRotX;
    });

    const stopDrag = e => {
      if (isDraggingCanvas) {
        isDraggingCanvas = false;
        try {
          spatialCanvas.releasePointerCapture(e.pointerId);
        } catch (err) {}
      }
    };
    window.addEventListener('pointerup', stopDrag);
    window.addEventListener('pointercancel', stopDrag);

    requestAnimationFrame(renderSpatial);
  }

  function resizeSpatialCanvas() {
    if (!spatialCanvas) return;
    const rect = spatialCanvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    spatialCanvas.width = rect.width * dpr;
    spatialCanvas.height = rect.height * dpr;
    if (spatialCtx) {
      spatialCtx.scale(dpr, dpr);
    }
  }

  function renderSpatial(now) {
    if (!spatialCtx || !spatialCanvas) return;

    // Delta time & FPS calculation
    const delta = (now - lastFrameTime) / 1000;
    lastFrameTime = now;
    if (delta > 0) {
      const instantFps = 1 / delta;
      smoothFps = smoothFps * 0.92 + instantFps * 0.08;
      if (hudFpsCounter) {
        hudFpsCounter.textContent = `${Math.round(smoothFps)} FPS NATIVE`;
      }
    }

    const rect = spatialCanvas.getBoundingClientRect();
    const w = rect.width;
    const h = rect.height;
    const cx = w / 2;
    const cy = h / 2;

    // Clear frame
    spatialCtx.fillStyle = 'rgba(5, 6, 8, 0.4)';
    spatialCtx.fillRect(0, 0, w, h);

    // Draw Graticule Grid
    spatialCtx.strokeStyle = 'rgba(167, 139, 250, 0.06)';
    spatialCtx.lineWidth = 1;
    const gridDivs = 8;
    for (let c = 1; c < gridDivs; c++) {
      const gx = (w / gridDivs) * c;
      spatialCtx.beginPath();
      spatialCtx.moveTo(gx, 0);
      spatialCtx.lineTo(gx, h);
      spatialCtx.stroke();
    }
    for (let r = 1; r < 4; r++) {
      const gy = (h / 4) * r;
      spatialCtx.beginPath();
      spatialCtx.moveTo(0, gy);
      spatialCtx.lineTo(w, gy);
      spatialCtx.stroke();
    }

    // Auto-spin velocity & damping
    if (!isDraggingCanvas) {
      targetRotY += 0.005 + (orbitalAngle / 360) * 0.008;
    }

    // Spring damping interpolation toward target rotation
    rotX += (targetRotX - rotX) * 0.12;
    rotY += (targetRotY - rotY) * 0.12;

    if (hudCoordinates) {
      hudCoordinates.textContent = `VECTOR [X: ${rotX.toFixed(2)}, Y: ${rotY.toFixed(2)}, Z: 1.00]`;
    }

    // 3D Rotation Matrix Calculation
    const cosY = Math.cos(rotY);
    const sinY = Math.sin(rotY);
    const cosX = Math.cos(rotX);
    const sinX = Math.sin(rotX);

    const projected = [];
    const focalLength = 320;
    const pulseRate = now * 0.003;
    const qFactor = 0.8 + (resonanceQ / 100) * 0.6;

    for (let i = 0; i < SPATIAL_POINTS.length; i++) {
      const p = SPATIAL_POINTS[i];
      let { ox, oy, oz } = p;

      // Mode-specific deformation
      if (activeAlgorithm === 'neural') {
        const wave = Math.sin(p.phase + pulseRate) * 6 * qFactor;
        ox += wave;
        oy += wave;
      } else if (activeAlgorithm === 'tensor') {
        const torusWave = Math.sin(ox * 0.05 + pulseRate * 2) * 12;
        oy += torusWave;
      } else if (activeAlgorithm === 'kinetic') {
        const spinWave = Math.cos(pulseRate * 3 + p.phase) * 16 * qFactor;
        oz += spinWave;
      }

      // Rotate Y
      const x1 = ox * cosY - oz * sinY;
      const z1 = ox * sinY + oz * cosY;

      // Rotate X
      const y2 = oy * cosX - z1 * sinX;
      const z2 = oy * sinX + z1 * cosX;

      // Perspective Projection
      const depth = z2 + 280;
      if (depth > 10) {
        const scale = focalLength / depth;
        const px = cx + x1 * scale;
        const py = cy + y2 * scale;
        projected.push({
          x: px,
          y: py,
          z: z2,
          scale: scale,
          rawZ: depth
        });
      }
    }

    // Sort by depth (painter's algorithm)
    projected.sort((a, b) => b.z - a.z);

    // Connect Neighboring Lines
    spatialCtx.lineWidth = 1;
    for (let i = 0; i < projected.length; i++) {
      const p1 = projected[i];
      for (let j = i + 1; j < projected.length; j++) {
        const p2 = projected[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < 1200) {
          const alpha = (1 - d2 / 1200) * 0.28 * (p1.scale / 1.5);
          spatialCtx.strokeStyle = activeAlgorithm === 'kinetic'
            ? `rgba(45, 212, 191, ${alpha})`
            : `rgba(167, 139, 250, ${alpha})`;
          spatialCtx.beginPath();
          spatialCtx.moveTo(p1.x, p1.y);
          spatialCtx.lineTo(p2.x, p2.y);
          spatialCtx.stroke();
        }
      }
    }

    // Draw Projected Nodes
    for (let i = 0; i < projected.length; i++) {
      const p = projected[i];
      const radius = Math.max(1, p.scale * 2.5);
      const alpha = Math.min(1, Math.max(0.2, (p.z + 100) / 200));

      spatialCtx.fillStyle = activeAlgorithm === 'neural'
        ? `rgba(167, 139, 250, ${alpha})`
        : activeAlgorithm === 'tensor'
        ? `rgba(243, 232, 203, ${alpha})`
        : `rgba(45, 212, 191, ${alpha})`;

      spatialCtx.beginPath();
      spatialCtx.arc(p.x, p.y, radius, 0, Math.PI * 2);
      spatialCtx.fill();
    }

    requestAnimationFrame(renderSpatial);
  }

  // --- Segmented Neural VU Meter Pulse ---
  function updateNeuralBusMeter() {
    if (!busMeter) return;
    const cells = busMeter.querySelectorAll('.meter-cell');
    const energy = 0.45 + (resonanceQ / 100) * 0.45;
    const activeCount = Math.min(7, Math.floor(energy * 6 + Math.random() * 2));

    cells.forEach((cell, idx) => {
      cell.classList.toggle('active', idx < activeCount);
    });
  }
  setInterval(updateNeuralBusMeter, 110);

  // --- Algorithm Mode Switcher ---
  modeSwitchButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const mode = btn.dataset.mode;
      activeAlgorithm = mode;

      modeSwitchButtons.forEach(b => {
        const isSelected = b === btn;
        b.classList.toggle('active', isSelected);
        b.setAttribute('aria-checked', isSelected ? 'true' : 'false');
      });

      if (hudModeReadout) {
        hudModeReadout.textContent = `ALGORITHM: ${
          mode === 'neural' ? 'NEURAL TENSOR MESH' : mode === 'tensor' ? 'HARMONIC TENSOR TORUS' : 'KINETIC QUANTUM VOID'
        }`;
      }

      haptics.playSwitchClick();
    });
  });

  // --- Material Finish Switcher ---
  function setWorkstationFinish(finish) {
    document.body.setAttribute('data-finish', finish);

    const isTitanium = finish === 'titanium';
    finishTitaniumBtn.classList.toggle('active', isTitanium);
    finishTitaniumBtn.setAttribute('aria-pressed', isTitanium ? 'true' : 'false');

    finishObsidianBtn.classList.toggle('active', !isTitanium);
    finishObsidianBtn.setAttribute('aria-pressed', !isTitanium ? 'true' : 'false');

    if (chassisFinishChoice) {
      chassisFinishChoice.value = finish;
    }

    haptics.playRelayClack();
  }

  finishTitaniumBtn.addEventListener('click', () => setWorkstationFinish('titanium'));
  finishObsidianBtn.addEventListener('click', () => setWorkstationFinish('obsidian'));

  if (chassisFinishChoice) {
    chassisFinishChoice.addEventListener('change', e => {
      setWorkstationFinish(e.target.value);
    });
  }

  // --- Architecture Explorer Tabs ---
  const ARCHITECTURE_DATA = {
    monocoque: {
      id: 'STRUCTURAL ARCHITECTURE // LAYER 01',
      spec: 'MACHINING TOLERANCE ±0.010 mm',
      title: 'Solid Monobloc Grade 5 Titanium Monocoque',
      desc: 'Titanium Grade 5 provides twice the tensile strength of 6061 aluminum with superior vibrational damping characteristics. Eliminates microphonic distortion, resonance ringing, and electromagnetic interference across high-frequency acoustic bands.',
      stats: [
        { val: '940 g', label: 'Chassis Structural Mass' },
        { val: '280 × 175 × 28 mm', label: 'Exterior Monolith Footprint' },
        { val: '0.00008%', label: 'Residual Harmonic Distortion' }
      ]
    },
    vault: {
      id: 'FARADAY ISOLATION // LAYER 02',
      spec: 'SHIELDING REJECTION > 125 dB',
      title: 'Hermetically Sealed Oxygen-Free Copper Vault',
      desc: 'Differential Burr-Brown floating converters rest in an isolated pure copper sub-chassis. Gasket-sealed with gold-plated conductive mesh to completely isolate high-speed digital clock jitter from delicate analog preamplifiers.',
      stats: [
        { val: '142.4 dB', label: 'Signal to Noise Ratio' },
        { val: '< 32 fs', label: 'Master Clock Jitter Floor' },
        { val: '> 134.0 dB', label: 'Inter-channel Separation' }
      ]
    },
    rotors: {
      id: 'TACTILE ACTUATION // LAYER 03',
      spec: 'OPTICAL CPR: 8,192 PULSES',
      title: 'Neodymium Electromagnetic Rotor Assembly',
      desc: 'Precision diamond-knurled dials with programmable magnetic detent coils. Non-contact optical sensors read micro-rotations at 8,192 counts per revolution with zero mechanical friction or potentiometer scratch.',
      stats: [
        { val: '0 to 140 mN·m', label: 'Variable Magnetic Resistance' },
        { val: '< 0.08 ms', label: 'Encoder Latency' },
        { val: 'Infinite', label: 'Contactless Lifespan' }
      ]
    },
    thermal: {
      id: 'CRYOGENIC CONDUCTION // LAYER 04',
      spec: 'HEAT PIPING 24 W / m·K',
      title: 'Passive Cryogenic Siphon Heatpipe',
      desc: 'Sintered copper powder heatpipes disperse class-A amplifier thermal loads directly through the titanium chassis. 100% silent solid-state dissipation with zero fans or pump vibration.',
      stats: [
        { val: '0.0 dBA', label: 'Acoustic Sound Floor' },
        { val: '36° C', label: 'Nominal Operating Temperature' },
        { val: '20 W', label: 'Thunderbolt 4 Bus Power' }
      ]
    }
  };

  explorerTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const layer = tab.dataset.layer;
      const data = ARCHITECTURE_DATA[layer];
      if (!data) return;

      explorerTabs.forEach(t => {
        const isSelected = t === tab;
        t.classList.toggle('active', isSelected);
        t.setAttribute('aria-selected', isSelected ? 'true' : 'false');
      });

      document.getElementById('layer-badge-id').textContent = data.id;
      document.getElementById('layer-badge-spec').textContent = data.spec;
      document.getElementById('layer-heading').textContent = data.title;
      document.getElementById('layer-body-copy').textContent = data.desc;

      const cluster = document.getElementById('layer-metrics-cluster');
      cluster.innerHTML = '';
      data.stats.forEach(s => {
        const div = document.createElement('div');
        div.className = 'metric-unit';
        div.innerHTML = `<span class="unit-val">${s.val}</span><span class="unit-label">${s.label}</span>`;
        cluster.appendChild(div);
      });

      haptics.playSwitchClick();
    });
  });

  // --- Haptic Audio Switch ---
  hapticAudioSwitch.addEventListener('click', () => {
    haptics.enabled = !haptics.enabled;
    if (haptics.enabled) {
      audioStateGlyph.textContent = '🔊';
      hapticAudioSwitch.setAttribute('title', 'Audio feedback enabled');
      haptics.playSwitchClick();
    } else {
      audioStateGlyph.textContent = '🔇';
      hapticAudioSwitch.setAttribute('title', 'Audio feedback muted');
    }
  });

  // --- Pre-Order Reservation Form ---
  if (reservationForm) {
    reservationForm.addEventListener('submit', e => {
      e.preventDefault();

      let valid = true;
      nameErrorDisplay.textContent = '';
      emailErrorDisplay.textContent = '';

      if (!clientNameInput.value.trim()) {
        nameErrorDisplay.textContent = 'Please enter your name or studio designation.';
        clientNameInput.focus();
        valid = false;
      }

      const emailVal = clientEmailInput.value.trim();
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailVal || !emailRegex.test(emailVal)) {
        emailErrorDisplay.textContent = 'Please provide a valid professional email address for delivery confirmation.';
        if (valid) clientEmailInput.focus();
        valid = false;
      }

      if (valid) {
        haptics.playAllocationChime();
        allocationSuccessModal.classList.add('visible');
        allocationSuccessModal.setAttribute('aria-hidden', 'false');

        if (btnConfirmReservation) {
          btnConfirmReservation.disabled = true;
          btnConfirmReservation.textContent = 'Allocation Secured';
        }

        if (successDynamicMessage) {
          const randomSerial = Math.floor(100 + Math.random() * 900);
          successDynamicMessage.textContent = `Batch 01 production serial #00${randomSerial} registered for ${clientNameInput.value.trim()}. Verification transmitted to ${emailVal}.`;
        }
      }
    });
  }

  // --- Boot Sequence ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initCosmicBackdrop();
      initSpatialCanvas();
    });
  } else {
    initCosmicBackdrop();
    initSpatialCanvas();
  }
})();
