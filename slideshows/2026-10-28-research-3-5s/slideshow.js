"use strict";

(() => {
  // Change timing here. Keep photo filenames and sequence in photos.js.
  const INTERVAL_MS = 3500;
  const FADE_MS = 100;
  const CONTROLS_HIDE_MS = 3000;
  const PRELOAD_AHEAD = 8;
  const photos = window.SLIDESHOW_PHOTOS || [];
  const body = document.body;
  const layers = [...document.querySelectorAll(".slide")];
  const controls = document.querySelector("#controls");
  const playButton = document.querySelector("#play");
  const fullButton = document.querySelector("#fullscreen");
  const status = document.querySelector("#status");
  const cache = new Map();
  let current = -1;
  let requested = -1;
  let front = 0;
  let playing = true;
  let timer;
  let hideTimer;
  let statusTimer;
  let remaining = INTERVAL_MS;
  let dueAt = 0;
  let requestId = 0;
  let transitionUntil = 0;
  let hovering = false;
  let suspended = document.hidden;

  document.documentElement.style.setProperty("--fade-duration", `${FADE_MS}ms`);
  const wrap = (index) => (index % photos.length + photos.length) % photos.length;

  function notify(message) {
    clearTimeout(statusTimer);
    status.textContent = message;
    status.hidden = false;
    statusTimer = setTimeout(() => { status.hidden = true; }, 6000);
  }

  function loadPhoto(index) {
    if (cache.has(index)) return cache.get(index);
    const image = new Image();
    image.decoding = "async";
    if (index === 0) image.fetchPriority = "high";
    const promise = new Promise((resolve, reject) => {
      image.onload = async () => {
        try {
          if (image.decode) await image.decode();
          resolve(image);
        } catch (error) { reject(error); }
      };
      image.onerror = () => reject(new Error(`Cannot load photograph ${index + 1}`));
      image.src = `photos/${encodeURIComponent(photos[index])}`;
    });
    cache.set(index, promise);
    // Preloads are allowed to fail; navigation handles the failure without a blank slide.
    promise.catch(() => { if (cache.get(index) === promise) cache.delete(index); });
    return promise;
  }

  function preload() {
    const keep = new Set([current, wrap(current - 1)]);
    for (let step = 1; step <= Math.min(PRELOAD_AHEAD, photos.length - 1); step++) {
      keep.add(wrap(current + step));
    }
    for (const index of cache.keys()) if (!keep.has(index)) cache.delete(index);
    for (const index of keep) loadPhoto(index).catch(() => {});
  }

  function schedule(delay = INTERVAL_MS) {
    clearTimeout(timer);
    remaining = delay;
    if (!playing || suspended || current < 0 || photos.length < 2) return;
    dueAt = performance.now() + delay;
    timer = setTimeout(() => show(current + 1), delay);
  }

  function revealControls() {
    body.classList.add("controls-visible");
    clearTimeout(hideTimer);
    if (playing && !hovering && !controls.contains(document.activeElement)) {
      hideTimer = setTimeout(() => body.classList.remove("controls-visible"), CONTROLS_HIDE_MS);
    }
  }

  async function show(target, direction = 1) {
    if (!photos.length) return;
    clearTimeout(timer);
    const id = ++requestId;
    requested = wrap(target);
    let decoded;
    let next = requested;
    for (let attempt = 0; attempt < photos.length; attempt++) {
      try { decoded = await loadPhoto(next); break; }
      catch (error) {
        if (id !== requestId) return;
        console.warn(error.message);
        next = wrap(next + direction);
      }
    }
    if (id !== requestId) return;
    if (!decoded) {
      playing = false;
      updatePlayButton();
      revealControls();
      notify("The photographs could not load. Check your connection and refresh.");
      return;
    }
    requested = next;
    if (next !== current) {
      const now = performance.now();
      // A rapid sequence of arrow presses should show the final requested photo
      // immediately, without reusing an image layer halfway through a fade.
      if (current < 0 || now < transitionUntil) {
        for (const layer of layers) {
          layer.classList.add("instant");
          layer.classList.remove("is-active");
        }
        layers[front].src = decoded.src;
        layers[front].classList.add("is-active");
        void layers[front].offsetWidth;
        for (const layer of layers) layer.classList.remove("instant");
        transitionUntil = now;
      } else {
        const back = 1 - front;
        layers[back].src = decoded.src;
        layers[back].classList.add("is-active");
        layers[front].classList.remove("is-active");
        front = back;
        transitionUntil = now + FADE_MS;
      }
      current = next;
      // Non-visible state makes ordering and playback straightforward to verify.
      document.querySelector("#slideshow").dataset.photo = String(current + 1);
      document.querySelector("#slideshow").setAttribute("aria-label",
        `MIT 2.009 photo slideshow, photograph ${current + 1} of ${photos.length}`);
    }
    schedule();
    preload();
  }

  function updatePlayButton() {
    body.classList.toggle("paused", !playing);
    const label = playing ? "Pause slideshow" : "Play slideshow";
    playButton.setAttribute("aria-label", label);
    playButton.title = `${label} (Space)`;
  }

  function togglePlay() {
    playing = !playing;
    if (playing) {
      if (current < 0) show(0);
      else schedule(remaining);
    } else {
      remaining = dueAt ? Math.max(0, dueAt - performance.now()) : INTERVAL_MS;
      clearTimeout(timer);
      // Cancel an automatic advance that is still waiting for Wi-Fi.
      requestId++;
      requested = current;
    }
    updatePlayButton();
    revealControls();
  }

  function step(direction) {
    revealControls();
    show((requested < 0 ? 0 : requested) + direction, direction);
  }

  function fullElement() {
    return document.fullscreenElement || document.webkitFullscreenElement;
  }

  function updateFullscreen() {
    const active = Boolean(fullElement());
    body.classList.toggle("fullscreen", active);
    const label = active ? "Exit full screen" : "Enter full screen";
    fullButton.setAttribute("aria-label", label);
    fullButton.title = `${label} (F${active ? " or Escape" : ""})`;
    revealControls();
  }

  async function toggleFullscreen() {
    revealControls();
    try {
      if (fullElement()) {
        const exit = document.exitFullscreen || document.webkitExitFullscreen;
        await exit.call(document);
      } else {
        const root = document.documentElement;
        const enter = root.requestFullscreen || root.webkitRequestFullscreen;
        if (!enter) throw new Error("Fullscreen unavailable");
        await enter.call(root);
      }
    } catch {
      notify("Full screen is unavailable here. Open this slideshow in your laptop browser.");
    }
  }

  document.querySelector("#previous").addEventListener("click", () => step(-1));
  document.querySelector("#next").addEventListener("click", () => step(1));
  playButton.addEventListener("click", togglePlay);
  fullButton.addEventListener("click", toggleFullscreen);
  document.addEventListener("fullscreenchange", updateFullscreen);
  document.addEventListener("webkitfullscreenchange", updateFullscreen);
  document.addEventListener("pointermove", revealControls, { passive: true });
  document.addEventListener("pointerdown", revealControls, { passive: true });
  controls.addEventListener("pointerenter", (event) => {
    if (event.pointerType === "mouse") { hovering = true; revealControls(); }
  });
  controls.addEventListener("pointerleave", () => { hovering = false; revealControls(); });
  controls.addEventListener("pointerdown", (event) => {
    // Mouse clicks must not leave hidden keyboard focus holding the bar open.
    if (event.pointerType === "mouse") {
      event.preventDefault();
      if (controls.contains(document.activeElement)) document.activeElement.blur();
    }
  });
  controls.addEventListener("focusin", revealControls);
  controls.addEventListener("focusout", () => setTimeout(revealControls, 0));
  document.addEventListener("keydown", (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.target.isContentEditable) return;
    if (event.key === "Tab") { revealControls(); return; }
    if (event.repeat) return;
    if (event.code === "Space" && event.target.tagName !== "BUTTON") {
      event.preventDefault(); togglePlay();
    } else if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault(); step(event.key === "ArrowLeft" ? -1 : 1);
    } else if (event.key.toLowerCase() === "f") {
      event.preventDefault(); toggleFullscreen();
    }
  });

  document.addEventListener("visibilitychange", () => {
    suspended = document.hidden;
    if (suspended) {
      if (playing) remaining = dueAt ? Math.max(0, dueAt - performance.now()) : INTERVAL_MS;
      clearTimeout(timer);
      requestId++;
      requested = current;
    } else if (current < 0) {
      show(0);
    } else schedule(remaining);
  });

  if (photos.length) show(0);
  else {
    playing = false;
    updatePlayButton();
    revealControls();
    notify("No photographs are listed. Check photos.js and refresh.");
  }
})();
