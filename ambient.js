/* Muzha Food Link — generative background score.
   No audio files: every note is synthesised live, so the music never loops
   audibly and the page stays light. Opt-in only; nothing ever autoplays.

   One style: a fast, happy carnival march for the zoo end of the walk.
   132 BPM, 2/4 oom-pah, steam-organ lead, snare backbeat, glockenspiel
   sparkle, with an occasional slide whistle and a pair of bird chirps. */
window.MFL_AMBIENT = (function () {
  "use strict";

  var FADE_IN = 2.4, FADE_OUT = 1.6;

  function mtof(m) { return 440 * Math.pow(2, (m - 69) / 12); }
  function rnd(a, b) { return a + Math.random() * (b - a); }
  function pick(a) { return a[Math.floor(Math.random() * a.length)]; }

  /* ---------- procedural reverb impulse ---------- */
  function impulse(ctx, secs, decay) {
    var n = Math.floor(ctx.sampleRate * secs);
    var buf = ctx.createBuffer(2, n, ctx.sampleRate);
    for (var c = 0; c < 2; c++) {
      var d = buf.getChannelData(c), last = 0;
      for (var i = 0; i < n; i++) {
        var t = i / n;
        last = last * 0.72 + (Math.random() * 2 - 1) * 0.28;
        d[i] = last * Math.pow(1 - t, decay) * (i < 64 ? i / 64 : 1);
      }
    }
    return buf;
  }

  /* ---------- pink-ish noise, reused for air, picks and shakers ---------- */
  function noiseBuffer(ctx, secs) {
    var n = Math.floor(ctx.sampleRate * secs);
    var buf = ctx.createBuffer(2, n, ctx.sampleRate);
    for (var c = 0; c < 2; c++) {
      var d = buf.getChannelData(c), b0 = 0, b1 = 0, b2 = 0;
      for (var i = 0; i < n; i++) {
        var w = Math.random() * 2 - 1;
        b0 = 0.99765 * b0 + w * 0.0990460;
        b1 = 0.96300 * b1 + w * 0.2965164;
        b2 = 0.57000 * b2 + w * 1.0526913;
        d[i] = (b0 + b1 + b2 + w * 0.1848) * 0.16;
      }
      var f = Math.floor(ctx.sampleRate * 0.25);
      for (var k = 0; k < f; k++) { var g = k / f; d[k] *= g; d[n - 1 - k] *= g; }
    }
    return buf;
  }

  /* ---------- shared output chain ---------- */
  var CFG = { gain: 0.52, tone: 9200, ir: 1.0, irDecay: 1.9, wet: 0.13, dry: 0.97, air: 0.014 };

  function chain(ctx, dest, cfg) {
    var master = ctx.createGain(); master.gain.value = 0;
    var soften = ctx.createBiquadFilter();
    soften.type = "lowpass"; soften.frequency.value = cfg.tone; soften.Q.value = 0.4;
    var glue = ctx.createDynamicsCompressor();
    glue.threshold.value = -20; glue.knee.value = 24;
    glue.ratio.value = 3; glue.attack.value = 0.02; glue.release.value = 0.35;
    soften.connect(glue); glue.connect(master); master.connect(dest);

    var verb = ctx.createConvolver(); verb.buffer = impulse(ctx, cfg.ir, cfg.irDecay);
    var wet = ctx.createGain(); wet.gain.value = cfg.wet;
    var dry = ctx.createGain(); dry.gain.value = cfg.dry;
    var bus = ctx.createGain();
    bus.connect(dry); dry.connect(soften);
    bus.connect(verb); verb.connect(wet); wet.connect(soften);

    var noise = noiseBuffer(ctx, 6);
    var air = ctx.createBufferSource(); air.buffer = noise; air.loop = true;
    var aLp = ctx.createBiquadFilter(); aLp.type = "lowpass"; aLp.frequency.value = 620;
    var aHp = ctx.createBiquadFilter(); aHp.type = "highpass"; aHp.frequency.value = 110;
    var aG = ctx.createGain(); aG.gain.value = cfg.air;
    var lfo = ctx.createOscillator(); lfo.frequency.value = 0.045;
    var lfoG = ctx.createGain(); lfoG.gain.value = cfg.air * 0.4;
    lfo.connect(lfoG); lfoG.connect(aG.gain);
    air.connect(aHp); aHp.connect(aLp); aLp.connect(aG); aG.connect(bus);

    function panTo(node, p) {
      if (ctx.createStereoPanner) { var s = ctx.createStereoPanner(); s.pan.value = p; node.connect(s); s.connect(bus); }
      else node.connect(bus);
    }
    return { bus: bus, master: master, noise: noise, panTo: panTo,
             startSources: function (t) { air.start(t); lfo.start(t); },
             stopSources: function (t) { try { air.stop(t); lfo.stop(t); } catch (e) {} } };
  }

  /* =======================================================================
     THE SCORE — carnival march, 132 BPM, 2/4 oom-pah
     ======================================================================= */
  var BPM = 132, BEAT = 60 / BPM, BAR = 4 * BEAT;

  /* F major. root = oom (tuba), pah = off-beat chord stab. */
  var CH = [
    { root: 41, pah: [57, 60, 65] },        /* F  */
    { root: 46, pah: [58, 62, 65] },        /* Bb */
    { root: 48, pah: [55, 60, 64, 70] }     /* C7 */
  ];
  var PROG = [0, 1, 0, 2, 0, 1, 2, 0];      /* 8-bar loop */

  /* Tune as [beat, midi, dur] across the 32 beats of the loop. Fixed, not
     random, so it sounds composed; ornaments and octaves vary per pass. */
  var MEL = [
    [0, 72, .22], [.5, 77, .22], [1, 76, .22], [1.5, 74, .22], [2, 72, .40], [3, 69, .40],
    [4, 70, .22], [4.5, 74, .22], [5, 77, .22], [5.5, 74, .22], [6, 70, .40], [7, 72, .40],
    [8, 72, .22], [8.5, 77, .22], [9, 79, .22], [9.5, 77, .22], [10, 76, .40], [11, 74, .40],
    [12, 76, .22], [12.5, 74, .22], [13, 72, .22], [13.5, 71, .22], [14, 72, .60],
    [16, 81, .22], [16.5, 79, .22], [17, 77, .22], [17.5, 76, .22], [18, 77, .50], [19, 74, .30],
    [20, 82, .22], [20.5, 81, .22], [21, 79, .22], [21.5, 77, .22], [22, 74, .50], [23, 70, .30],
    [24, 72, .22], [24.5, 76, .22], [25, 79, .22], [25.5, 82, .22], [26, 81, .40], [27, 79, .40],
    [28, 77, .30], [28.5, 76, .30], [29, 77, .70], [31, 65, .40]
  ];

  function carnival(ctx, C) {
    var barAt = 0, barIdx = 0;

    /* steam-organ lead: two detuned squares, vibrato, bright but filtered */
    function calliope(t0, midi, dur, vel) {
      var f = mtof(midi), g = ctx.createGain();
      var lp = ctx.createBiquadFilter();
      lp.type = "lowpass"; lp.frequency.value = 2700; lp.Q.value = 1.1;
      g.connect(lp); C.panTo(lp, rnd(-0.16, 0.16));
      var vib = ctx.createOscillator(), vibG = ctx.createGain();
      vib.frequency.value = 5.6; vibG.gain.value = f * 0.0032;
      vib.connect(vibG); vib.start(t0); vib.stop(t0 + dur + 0.2);
      [[-7, 0.5], [7, 0.5], [1200, 0.13]].forEach(function (v) {
        var o = ctx.createOscillator();
        o.type = v[0] === 1200 ? "sine" : "square";
        o.frequency.value = f; o.detune.value = v[0] === 1200 ? 1200 : v[0];
        vibG.connect(o.frequency);
        var vg = ctx.createGain(); vg.gain.value = v[1];
        o.connect(vg); vg.connect(g); o.start(t0); o.stop(t0 + dur + 0.16);
      });
      g.gain.setValueAtTime(0, t0);
      g.gain.linearRampToValueAtTime(vel, t0 + 0.008);
      g.gain.setValueAtTime(vel, t0 + Math.max(0.02, dur - 0.05));
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur + 0.12);
    }

    /* oom: tuba downbeat */
    function oom(t0, midi, vel) {
      var f = mtof(midi), g = ctx.createGain();
      C.panTo(g, 0);
      [["sine", 1], ["triangle", 0.34]].forEach(function (v) {
        var o = ctx.createOscillator(); o.type = v[0]; o.frequency.value = f;
        var vg = ctx.createGain(); vg.gain.value = v[1];
        o.connect(vg); vg.connect(g); o.start(t0); o.stop(t0 + 0.34);
      });
      g.gain.setValueAtTime(0, t0);
      g.gain.linearRampToValueAtTime(vel, t0 + 0.012);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.30);
    }

    /* pah: clipped chord stab on the off beat */
    function pah(t0, notes, vel, pan) {
      var lp = ctx.createBiquadFilter();
      lp.type = "lowpass"; lp.frequency.value = 1900; lp.Q.value = 0.7;
      var g = ctx.createGain(); g.connect(lp); C.panTo(lp, pan);
      notes.forEach(function (m) {
        var o = ctx.createOscillator(); o.type = "square";
        o.frequency.value = mtof(m);
        var vg = ctx.createGain(); vg.gain.value = 0.3;
        o.connect(vg); vg.connect(g); o.start(t0); o.stop(t0 + 0.22);
      });
      g.gain.setValueAtTime(0, t0);
      g.gain.linearRampToValueAtTime(vel, t0 + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.18);
    }

    function noiseHit(t0, hz, dur, vel, pan, type) {
      var s = ctx.createBufferSource(); s.buffer = C.noise;
      s.playbackRate.value = 1.6;
      var f = ctx.createBiquadFilter();
      f.type = type || "highpass"; f.frequency.value = hz; f.Q.value = 0.8;
      var g = ctx.createGain();
      s.connect(f); f.connect(g); C.panTo(g, pan);
      g.gain.setValueAtTime(0, t0);
      g.gain.linearRampToValueAtTime(vel, t0 + 0.004);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
      s.start(t0, rnd(0, 4)); s.stop(t0 + dur + 0.05);
    }
    function snare(t0, vel) { noiseHit(t0, 950, 0.10, vel, 0, "highpass"); }
    function hat(t0, vel, pan) { noiseHit(t0, 6400, 0.035, vel, pan, "highpass"); }

    /* glockenspiel sparkle */
    function glock(t0, midi, vel) {
      var f = mtof(midi), g = ctx.createGain();
      C.panTo(g, rnd(-0.62, 0.62));
      [[1, 0.5, 1.2], [2.76, 0.16, 0.7], [5.4, 0.05, 0.4]].forEach(function (p) {
        var o = ctx.createOscillator(); o.type = "sine";
        o.frequency.value = f * p[0];
        var vg = ctx.createGain(); vg.gain.value = 0;
        vg.gain.setValueAtTime(0, t0);
        vg.gain.linearRampToValueAtTime(p[1] * vel, t0 + 0.004);
        vg.gain.exponentialRampToValueAtTime(0.0001, t0 + p[2]);
        o.connect(vg); vg.connect(g); o.start(t0); o.stop(t0 + p[2] + 0.05);
      });
      g.gain.value = 1;
    }

    /* slide whistle swoop */
    function whistle(t0) {
      var o = ctx.createOscillator(); o.type = "sine";
      var g = ctx.createGain(); o.connect(g); C.panTo(g, rnd(-0.5, 0.5));
      o.frequency.setValueAtTime(880, t0);
      o.frequency.exponentialRampToValueAtTime(2300, t0 + 0.26);
      o.frequency.exponentialRampToValueAtTime(1040, t0 + 0.55);
      g.gain.setValueAtTime(0, t0);
      g.gain.linearRampToValueAtTime(0.055, t0 + 0.05);
      g.gain.setValueAtTime(0.055, t0 + 0.4);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.6);
      o.start(t0); o.stop(t0 + 0.65);
    }

    /* two quick bird chirps, the zoo in the mix */
    function chirp(t0) {
      for (var k = 0; k < 2; k++) {
        var t = t0 + k * 0.12, o = ctx.createOscillator(), g = ctx.createGain();
        o.type = "sine"; o.connect(g); C.panTo(g, rnd(-0.7, 0.7));
        o.frequency.setValueAtTime(rnd(2100, 2500), t);
        o.frequency.exponentialRampToValueAtTime(rnd(3000, 3600), t + 0.05);
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(0.03, t + 0.008);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 0.09);
        o.start(t); o.stop(t + 0.12);
      }
    }

    function bar(t0, idx) {
      var b = idx % 8, loop = Math.floor(idx / 8);
      var ch = CH[PROG[b]];

      /* oom-pah engine */
      oom(t0, ch.root, 0.46);
      oom(t0 + 2 * BEAT, ch.root + (b % 2 ? 7 : 12), 0.36);
      pah(t0 + BEAT, ch.pah, 0.22, -0.46);
      pah(t0 + 3 * BEAT, ch.pah, 0.20, 0.46);

      /* backbeat snare, eighth-note hats */
      snare(t0 + BEAT, 0.16);
      snare(t0 + 3 * BEAT, 0.14);
      for (var e = 0; e < 8; e++) hat(t0 + e * BEAT * 0.5, e % 2 ? 0.036 : 0.062, e % 2 ? 0.52 : -0.38);

      /* melody for this bar */
      MEL.forEach(function (n) {
        if (n[0] < b * 4 || n[0] >= b * 4 + 4) return;
        var t = t0 + (n[0] - b * 4) * BEAT;
        var m = n[1] + (loop % 2 === 1 && b >= 4 ? 12 : 0);
        if (m > 93) m -= 12;
        calliope(t, m, n[2], 0.17);
        if (n[2] >= 0.4) glock(t, m + 12, 0.12);
        if (loop % 2 === 1 && Math.random() < 0.25) calliope(t - 0.055, m - 1, 0.05, 0.08);
      });

      /* bar 8: snare roll back into the top */
      if (b === 7) {
        for (var r = 0; r < 8; r++) snare(t0 + 2 * BEAT + r * BEAT * 0.25, 0.07 + r * 0.012);
      }
      if (b === 3 && Math.random() < 0.4) whistle(t0 + 2 * BEAT);
      if (b === 5 && Math.random() < 0.35) chirp(t0 + 3 * BEAT);
    }

    return {
      seed: function (t0) { barAt = t0; barIdx = 0; },
      schedule: function (until) {
        while (barAt < until) { bar(barAt, barIdx); barIdx++; barAt += BAR; }
      }
    };
  }

  function build(ctx, dest) {
    var C = chain(ctx, dest, CFG);
    var v = carnival(ctx, C);
    return { master: C.master, gain: CFG.gain, seed: v.seed, schedule: v.schedule,
             startSources: C.startSources, stopSources: C.stopSources };
  }

  /* ---------- live player ---------- */
  var ctx = null, eng = null, timer = null, playing = false, duck = 1;

  function tick() { if (eng && ctx) eng.schedule(ctx.currentTime + 4); }

  function ramp(to, secs) {
    if (!eng || !ctx) return;
    eng.master.gain.cancelScheduledValues(ctx.currentTime);
    eng.master.gain.setValueAtTime(eng.master.gain.value, ctx.currentTime);
    eng.master.gain.linearRampToValueAtTime(to, ctx.currentTime + secs);
  }

  function start() {
    if (playing) return true;
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return false;
    if (!ctx) ctx = new AC();
    if (ctx.state === "suspended") ctx.resume();
    if (!eng) {
      eng = build(ctx, ctx.destination);
      var t0 = ctx.currentTime + 0.08;
      eng.seed(t0); eng.startSources(t0);
    }
    playing = true;
    ramp(eng.gain * duck, FADE_IN);
    tick();
    timer = setInterval(tick, 1000);
    return true;
  }

  function teardown(fade) {
    clearInterval(timer); timer = null;
    if (!eng || !ctx) { eng = null; return; }
    var m = eng.master, e = eng;
    ramp(0, fade);
    e.stopSources(ctx.currentTime + fade + 0.1);
    setTimeout(function () { try { m.disconnect(); } catch (x) {} }, (fade + 0.3) * 1000);
    eng = null;
  }

  function stop() {
    if (!playing) return;
    playing = false;
    var c = ctx;
    teardown(FADE_OUT);
    setTimeout(function () { if (!playing && c && c.state === "running") c.suspend(); }, (FADE_OUT + 0.4) * 1000);
  }

  document.addEventListener("visibilitychange", function () {
    duck = document.hidden ? 0.25 : 1;
    if (playing && eng) ramp(eng.gain * duck, 1.2);
  });

  /* ---------- offline render, used to measure the mix ---------- */
  function render(seconds) {
    var OC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if (!OC) return Promise.reject(new Error("no OfflineAudioContext"));
    var oc = new OC(2, Math.ceil(44100 * seconds), 44100);
    var e = build(oc, oc.destination);
    e.seed(0); e.startSources(0);
    e.master.gain.setValueAtTime(0, 0);
    e.master.gain.linearRampToValueAtTime(e.gain, Math.min(FADE_IN, seconds * 0.4));
    e.schedule(seconds);
    return oc.startRendering();
  }

  return {
    start: start, stop: stop,
    toggle: function () { return playing ? (stop(), false) : (start(), true); },
    isPlaying: function () { return playing; },
    render: render
  };
})();
