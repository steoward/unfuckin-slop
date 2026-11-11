/**
 * AURA KINETICS - Apple Fluid Physics & Kinetic Surface Engine
 * Calibrated according to WWDC Fluid Interface principles and Unfuckin-Slop guidelines.
 */

(function () {
  'use strict';

  // --- Physical Audio Synthesizer (Web Audio API) ---
  class HapticAudio {
    constructor() {
      this.ctx = null;
      this.enabled = true;
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

    playGrab() {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(280, now);
        osc.frequency.exponentialRampToValueAtTime(70, now + 0.035);

        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.035);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.035);
      } catch (err) {
        // Audio policy ignore
      }
    }

    playSnap() {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(587.33, now); // D5
        osc1.frequency.exponentialRampToValueAtTime(880, now + 0.09); // A5

        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(293.66, now); // D4

        gain.gain.setValueAtTime(0.05, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.12);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(this.ctx.destination);

        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 0.12);
        osc2.stop(now + 0.12);
      } catch (err) {
        // Audio policy ignore
      }
    }

    playBoundary() {
      if (!this.enabled) return;
      this.ensureContext();
      if (!this.ctx) return;

      try {
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const filter = this.ctx.createBiquadFilter();
        const gain = this.ctx.createGain();

        osc.type = 'square';
        osc.frequency.setValueAtTime(120, now);
        osc.frequency.exponentialRampToValueAtTime(40, now + 0.05);

        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(260, now);

        gain.gain.setValueAtTime(0.04, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

        osc.connect(filter);
        filter.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.05);
      } catch (err) {
        // Audio policy ignore
      }
    }
  }

  // --- Momentum Projection & Spring Math ---
  // Apple WWDC Momentum Projection: project(velocity, decelerationRate = 0.998)
  function projectMomentum(velocity, decelerationRate = 0.998) {
    return (velocity / 1000) * (decelerationRate / (1 - decelerationRate));
  }

  function rubberBandClamp(val, min, max, factor = 0.3) {
    if (val < min) {
      return min - Math.pow(min - val, 0.85) * factor;
    }
    if (val > max) {
      return max + Math.pow(val - max, 0.85) * factor;
    }
    return val;
  }

  // --- DOM References ---
  const viewport = document.getElementById('viewport');
  const card = document.getElementById('card');
  const indicator = document.getElementById('indicator');
  const statusTag = document.getElementById('status-tag');
  const coordReadout = document.getElementById('coord-readout');
  const velReadout = document.getElementById('vel-readout');

  const telVelocity = document.getElementById('tel-velocity');
  const telProjection = document.getElementById('tel-projection');
  const telPhase = document.getElementById('tel-phase');
  const telFps = document.getElementById('tel-fps');

  const dampingSlider = document.getElementById('damping-slider');
  const dampingVal = document.getElementById('damping-val');
  const responseSlider = document.getElementById('response-slider');
  const responseVal = document.getElementById('response-val');

  const themeToggle = document.getElementById('theme-toggle');
  const themeIcon = document.getElementById('theme-icon');
  const themeText = document.getElementById('theme-text');
  const resetPosBtn = document.getElementById('reset-pos-btn');
  const audioToggle = document.getElementById('audio-toggle');
  const soundIcon = document.getElementById('sound-icon');
  const soundText = document.getElementById('sound-text');

  const presetButtons = document.querySelectorAll('.preset-btn');
  const anchorElements = document.querySelectorAll('.viewport-anchor');

  const haptics = new HapticAudio();

  // --- Physics Simulation State ---
  let dampingRatio = 1.0;
  let responseDuration = 0.4;

  let posX = 40;
  let posY = 40;
  let targetX = 40;
  let targetY = 40;
  let velX = 0;
  let velY = 0;

  let isDragging = false;
  let dragStartPointerX = 0;
  let dragStartPointerY = 0;
  let dragStartPosX = 0;
  let dragStartPosY = 0;
  let pointerHistory = [];

  let lastFrameTime = performance.now();
  let smoothFps = 60;
  let activePhase = 'Equilibrium';
  let hasSnappedAtRest = true;

  // --- Anchors Resolution ---
  function getAnchorPositions() {
    const vRect = viewport.getBoundingClientRect();
    const cardW = 200;
    const cardH = 140;

    return [
      { name: 'Anchor 1', x: vRect.width * 0.25 - cardW / 2, y: vRect.height * 0.25 - cardH / 2 },
      { name: 'Anchor 2', x: vRect.width * 0.75 - cardW / 2, y: vRect.height * 0.25 - cardH / 2 },
      { name: 'Anchor 3', x: vRect.width * 0.25 - cardW / 75 - cardW / 2, y: vRect.height * 0.75 - cardH / 2 },
      { name: 'Anchor 4', x: vRect.width * 0.75 - cardW / 2, y: vRect.height * 0.75 - cardH / 2 }
    ].map((a, i) => {
      // Precise positions based on anchor style
      const fx = (i % 2 === 0) ? 0.25 : 0.75;
      const fy = (i < 2) ? 0.25 : 0.75;
      return {
        name: `Anchor ${i + 1}`,
        x: Math.round(vRect.width * fx - cardW / 2),
        y: Math.round(vRect.height * fy - cardH / 2)
      };
    });
  }

  function getViewportBounds() {
    const vRect = viewport.getBoundingClientRect();
    const cardW = 200;
    const cardH = 140;
    const padding = 16;
    return {
      minX: padding,
      maxX: Math.max(padding, vRect.width - cardW - padding),
      minY: padding,
      maxY: Math.max(padding, vRect.height - cardH - padding)
    };
  }

  function findNearestAnchor(px, py) {
    const anchors = getAnchorPositions();
    let bestDist = Infinity;
    let bestAnchor = anchors[0];

    anchors.forEach(a => {
      const dx = a.x - px;
      const dy = a.y - py;
      const dist = dx * dx + dy * dy;
      if (dist < bestDist) {
        bestDist = dist;
        bestAnchor = a;
      }
    });

    return bestAnchor;
  }

  // --- Initial Position Set ---
  function initPosition() {
    const anchors = getAnchorPositions();
    const initial = anchors[0] || { x: 40, y: 40 };
    posX = initial.x;
    posY = initial.y;
    targetX = initial.x;
    targetY = initial.y;
    velX = 0;
    velY = 0;
    card.style.transform = `translate3d(${posX}px, ${posY}px, 0)`;
  }

  // --- Pointer Interaction Handlers ---
  function onPointerDown(e) {
    if (e.button !== 0 && e.pointerType === 'mouse') return;

    haptics.playGrab();
    isDragging = true;
    hasSnappedAtRest = false;
    card.setPointerCapture(e.pointerId);

    dragStartPointerX = e.clientX;
    dragStartPointerY = e.clientY;
    dragStartPosX = posX;
    dragStartPosY = posY;

    pointerHistory = [{ t: performance.now(), x: posX, y: posY }];
    velX = 0;
    velY = 0;

    activePhase = 'Direct Tracking';
    updateVisualStatus('DRAGGING', '#ffb830');
  }

  function onPointerMove(e) {
    if (!isDragging) return;

    const deltaX = e.clientX - dragStartPointerX;
    const deltaY = e.clientY - dragStartPointerY;

    const bounds = getViewportBounds();
    const rawX = dragStartPosX + deltaX;
    const rawY = dragStartPosY + deltaY;

    posX = rubberBandClamp(rawX, bounds.minX, bounds.maxX);
    posY = rubberBandClamp(rawY, bounds.minY, bounds.maxY);

    const now = performance.now();
    pointerHistory.push({ t: now, x: posX, y: posY });
    pointerHistory = pointerHistory.filter(pt => now - pt.t <= 100);

    card.style.transform = `translate3d(${posX}px, ${posY}px, 0)`;

    // Calculate live velocity from pointer buffer
    if (pointerHistory.length >= 2) {
      const oldest = pointerHistory[0];
      const newest = pointerHistory[pointerHistory.length - 1];
      const dt = (newest.t - oldest.t) / 1000;
      if (dt > 0.005) {
        velX = (newest.x - oldest.x) / dt;
        velY = (newest.y - oldest.y) / dt;
      }
    }

    const currentSpeed = Math.round(Math.sqrt(velX * velX + velY * velY));
    coordReadout.textContent = `X: ${Math.round(posX)} Y: ${Math.round(posY)}`;
    velReadout.textContent = `${currentSpeed} px/s`;
    telVelocity.textContent = `${currentSpeed} px/s`;

    // Live projection estimation
    const projX = posX + projectMomentum(velX);
    const projY = posY + projectMomentum(velY);
    const projectedAnchor = findNearestAnchor(projX, projY);
    telProjection.textContent = projectedAnchor.name;
  }

  function onPointerUp(e) {
    if (!isDragging) return;
    isDragging = false;

    try {
      card.releasePointerCapture(e.pointerId);
    } catch (err) {
      // Ignored if capture already lost
    }

    // Velocity computation at release
    const now = performance.now();
    pointerHistory = pointerHistory.filter(pt => now - pt.t <= 120);

    if (pointerHistory.length >= 2) {
      const oldest = pointerHistory[0];
      const newest = pointerHistory[pointerHistory.length - 1];
      const dt = (newest.t - oldest.t) / 1000;
      if (dt > 0.005) {
        velX = (newest.x - oldest.x) / dt;
        velY = (newest.y - oldest.y) / dt;
      }
    }

    // Velocity clamp to avoid runaway physics
    const maxSpeed = 3500;
    const speed = Math.sqrt(velX * velX + velY * velY);
    if (speed > maxSpeed) {
      const scale = maxSpeed / speed;
      velX *= scale;
      velY *= scale;
    }

    // Momentum projection
    const projectedX = posX + projectMomentum(velX);
    const projectedY = posY + projectMomentum(velY);

    const nearestAnchor = findNearestAnchor(projectedX, projectedY);
    targetX = nearestAnchor.x;
    targetY = nearestAnchor.y;

    if (speed > 180) {
      activePhase = 'Momentum Coasting';
      updateVisualStatus('COASTING', '#4e75ff');
    } else {
      activePhase = 'Spring Settling';
      updateVisualStatus('SETTLING', '#4e75ff');
    }

    telProjection.textContent = nearestAnchor.name;
  }

  // --- Status & Readout Helpers ---
  function updateVisualStatus(label, color) {
    statusTag.textContent = label;
    indicator.style.backgroundColor = color;
  }

  // --- Keyboard Interaction ---
  function onKeyDown(e) {
    const anchors = getAnchorPositions();
    const currentNearest = findNearestAnchor(posX, posY);
    let currentIndex = anchors.findIndex(a => a.name === currentNearest.name);
    if (currentIndex === -1) currentIndex = 0;

    let targetIndex = currentIndex;
    let handled = false;

    switch (e.key) {
      case 'ArrowRight':
        targetIndex = (currentIndex % 2 === 0) ? currentIndex + 1 : currentIndex;
        handled = true;
        break;
      case 'ArrowLeft':
        targetIndex = (currentIndex % 2 !== 0) ? currentIndex - 1 : currentIndex;
        handled = true;
        break;
      case 'ArrowDown':
        targetIndex = (currentIndex < 2) ? currentIndex + 2 : currentIndex;
        handled = true;
        break;
      case 'ArrowUp':
        targetIndex = (currentIndex >= 2) ? currentIndex - 2 : currentIndex;
        handled = true;
        break;
      case 'Enter':
      case ' ':
        // Cycle clockwise 0 -> 1 -> 3 -> 2 -> 0
        const order = [0, 1, 3, 2];
        const ordPos = order.indexOf(currentIndex);
        targetIndex = order[(ordPos + 1) % order.length];
        handled = true;
        break;
      default:
        break;
    }

    if (handled) {
      e.preventDefault();
      const chosen = anchors[targetIndex];
      targetX = chosen.x;
      targetY = chosen.y;
      
      // Inject directional velocity for kinetic punch
      const dirX = targetX - posX;
      const dirY = targetY - posY;
      const dist = Math.sqrt(dirX * dirX + dirY * dirY);
      if (dist > 0) {
        velX += (dirX / dist) * 450;
        velY += (dirY / dist) * 450;
      }

      hasSnappedAtRest = false;
      activePhase = 'Spring Settling';
      updateVisualStatus('SETTLING', '#4e75ff');
      telProjection.textContent = chosen.name;
    }
  }

  // --- Main Animation Frame (Spring Integrator) ---
  function stepPhysics(currentTime) {
    const rawDelta = (currentTime - lastFrameTime) / 1000;
    lastFrameTime = currentTime;

    // Framerate smoothing
    if (rawDelta > 0) {
      const currentFps = 1 / rawDelta;
      smoothFps = smoothFps * 0.9 + currentFps * 0.1;
      telFps.textContent = `${Math.round(smoothFps)} fps`;
    }

    if (!isDragging) {
      // Apple Spring Equations:
      // omega0 = 2 * PI / responseDuration
      // acc = -omega0^2 * (x - targetX) - 2 * dampingRatio * omega0 * vel
      const omega0 = (2 * Math.PI) / Math.max(responseDuration, 0.05);
      const omega0Sq = omega0 * omega0;
      const dampingFactor = 2 * dampingRatio * omega0;

      // Sub-stepping for numerical stability
      let dtRemaining = Math.min(rawDelta, 0.064);
      const subStep = 0.008;

      while (dtRemaining > 0) {
        const dt = Math.min(dtRemaining, subStep);

        const accX = -omega0Sq * (posX - targetX) - dampingFactor * velX;
        const accY = -omega0Sq * (posY - targetY) - dampingFactor * velY;

        velX += accX * dt;
        velY += accY * dt;

        posX += velX * dt;
        posY += velY * dt;

        dtRemaining -= dt;
      }

      // Check resting equilibrium
      const distTarget = Math.sqrt(Math.pow(posX - targetX, 2) + Math.pow(posY - targetY, 2));
      const currentSpeed = Math.sqrt(velX * velX + velY * velY);

      if (distTarget < 0.35 && currentSpeed < 1.2) {
        posX = targetX;
        posY = targetY;
        velX = 0;
        velY = 0;

        if (!hasSnappedAtRest) {
          hasSnappedAtRest = true;
          haptics.playSnap();
        }

        activePhase = 'Equilibrium';
        updateVisualStatus('RESTING', 'var(--accent-energy)');
      } else {
        hasSnappedAtRest = false;
      }

      card.style.transform = `translate3d(${posX}px, ${posY}px, 0)`;

      const roundedSpeed = Math.round(currentSpeed);
      coordReadout.textContent = `X: ${Math.round(posX)} Y: ${Math.round(posY)}`;
      velReadout.textContent = `${roundedSpeed} px/s`;
      telVelocity.textContent = `${roundedSpeed} px/s`;
      telPhase.textContent = activePhase;
    } else {
      telPhase.textContent = activePhase;
    }

    requestAnimationFrame(stepPhysics);
  }

  // --- Preset Switcher ---
  const PRESETS = {
    pip: { damping: 1.0, response: 0.4 },
    sheet: { damping: 0.8, response: 0.3 },
    rotation: { damping: 0.7, response: 0.45 }
  };

  function applyPreset(key) {
    const config = PRESETS[key];
    if (!config) return;

    dampingRatio = config.damping;
    responseDuration = config.response;

    dampingSlider.value = dampingRatio.toFixed(2);
    dampingVal.textContent = dampingRatio.toFixed(2);

    responseSlider.value = responseDuration.toFixed(2);
    responseVal.textContent = `${responseDuration.toFixed(2)}s`;

    presetButtons.forEach(btn => {
      const isActive = btn.dataset.preset === key;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-checked', isActive ? 'true' : 'false');
    });
  }

  // --- Slider Event Listeners ---
  dampingSlider.addEventListener('input', e => {
    dampingRatio = parseFloat(e.target.value);
    dampingVal.textContent = dampingRatio.toFixed(2);
    presetButtons.forEach(btn => {
      btn.classList.remove('active');
      btn.setAttribute('aria-checked', 'false');
    });
  });

  responseSlider.addEventListener('input', e => {
    responseDuration = parseFloat(e.target.value);
    responseVal.textContent = `${responseDuration.toFixed(2)}s`;
    presetButtons.forEach(btn => {
      btn.classList.remove('active');
      btn.setAttribute('aria-checked', 'false');
    });
  });

  presetButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      applyPreset(btn.dataset.preset);
      haptics.playGrab();
    });
  });

  // --- Theme Toggle ---
  themeToggle.addEventListener('click', () => {
    const root = document.documentElement;
    const isLight = root.getAttribute('data-theme') === 'light';

    if (isLight) {
      root.removeAttribute('data-theme');
      themeIcon.textContent = '🌙';
      themeText.textContent = 'Dark';
    } else {
      root.setAttribute('data-theme', 'light');
      themeIcon.textContent = '☀️';
      themeText.textContent = 'Light';
    }
    haptics.playGrab();
  });

  // --- Audio Haptics Toggle ---
  audioToggle.addEventListener('click', () => {
    haptics.enabled = !haptics.enabled;
    if (haptics.enabled) {
      soundIcon.textContent = '🔊';
      soundText.textContent = 'Haptic Sound: Enabled';
      haptics.playGrab();
    } else {
      soundIcon.textContent = '🔇';
      soundText.textContent = 'Haptic Sound: Disabled';
    }
  });

  // --- Recenter Button ---
  resetPosBtn.addEventListener('click', () => {
    const vRect = viewport.getBoundingClientRect();
    const cardW = 200;
    const cardH = 140;

    targetX = Math.round(vRect.width / 2 - cardW / 2);
    targetY = Math.round(vRect.height / 2 - cardH / 2);
    velX = 0;
    velY = 0;
    hasSnappedAtRest = false;

    activePhase = 'Spring Settling';
    updateVisualStatus('SETTLING', '#4e75ff');
    telProjection.textContent = 'Center';
    haptics.playGrab();
  });

  // --- Window Resize & Orientation ---
  window.addEventListener('resize', () => {
    const bounds = getViewportBounds();
    posX = Math.max(bounds.minX, Math.min(bounds.maxX, posX));
    posY = Math.max(bounds.minY, Math.min(bounds.maxY, posY));
    targetX = Math.max(bounds.minX, Math.min(bounds.maxX, targetX));
    targetY = Math.max(bounds.minY, Math.min(bounds.maxY, targetY));
    card.style.transform = `translate3d(${posX}px, ${posY}px, 0)`;
  });

  // --- Bind Event Listeners ---
  card.addEventListener('pointerdown', onPointerDown);
  window.addEventListener('pointermove', onPointerMove);
  window.addEventListener('pointerup', onPointerUp);
  window.addEventListener('pointercancel', onPointerUp);
  card.addEventListener('keydown', onKeyDown);

  // Initialize
  window.addEventListener('DOMContentLoaded', () => {
    initPosition();
    requestAnimationFrame(stepPhysics);
  });

  if (document.readyState !== 'loading') {
    initPosition();
    requestAnimationFrame(stepPhysics);
  }
})();
