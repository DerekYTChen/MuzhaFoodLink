/* Muzha Food Link — generative background score.
   No audio files: every note is synthesised live, so the music never loops
   audibly and the page stays light. Opt-in only; nothing ever autoplays.

   One style: a slow, warm room. 72 BPM, 4/4, a four-bar loop of
   Am9 - Fmaj7 - C - G. Felt piano, a breathing pad, upright-bass plucks,
   a brushed shaker kept almost under the floor, and the odd vibraphone
   bell. Long reverb, few onsets: it should read as quiet thinking, not
   as a campaign. */
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
  var CFG = { gain: 0.56, tone: 6400, ir: 2.8, irDecay: 2.3, wet: 0.30, dry: 0.92, air: 0.018 };

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
     THE SCORE — 72 BPM, 4/4, four-bar loop in A minor
     ======================================================================= */
  var BPM = 72, BEAT = 60 / BPM, BAR = 4 * BEAT;

  /* root = bass, fifth = second bass note, pad/voicing = sustained chord,
     arp = the notes the felt piano walks through. */
  var CH = [
    { root: 45, fifth: 52, pad: [57, 60, 64, 67, 71], arp: [57, 64, 67, 71] },  /* Am9   */
    { root: 41, fifth: 48, pad: [53, 57, 60, 64],     arp: [53, 60, 64, 69] },  /* Fmaj7 */
    { root: 48, fifth: 55, pad: [55, 60, 64, 67],     arp: [55, 64, 67, 72] },  /* C     */
    { root: 43, fifth: 50, pad: [55, 59, 62, 67],     arp: [50, 59, 62, 67] }   /* G     */
  ];

  /* Tune as [beat, midi, dur] across the 16 beats of the loop. Fixed, so it
     sounds composed; register and ornament vary per pass. Long notes, gaps
     left open on purpose. */
  var MEL = [
    [0, 76, 2.4], [2.75, 72, 1.0],
    [4, 74, 2.6], [6.75, 69, 1.1],
    [8, 72, 1.9], [10.5, 76, 1.3],
    [12, 79, 2.2], [14.5, 74, 1.3]
  ];

  function room(ctx, C) {
    var barAt = 0, barIdx = 0;

    /* felt piano: soft attack, sine body plus a quiet detuned triangle,
       lowpass that closes as the note decays so it darkens like felt. */
    function felt(t0, midi, dur, vel, pan) {
      var f = mtof(midi), g = ctx.createGain();
      var lp = ctx.createBiquadFilter();
      lp.type = "lowpass"; lp.Q.value = 0.6;
      lp.frequency.setValueAtTime(Math.min(5200, f * 7), t0);
      lp.frequency.exponentialRampToValueAtTime(Math.max(420, f * 2.2), t0 + dur);
      g.connect(lp); C.panTo(lp, pan);
      [["sine", 0, 1], ["triangle", 6, 0.20], ["sine", -5, 0.34]].forEach(function (v) {
        var o = ctx.createOscillator(); o.type = v[0];
        o.frequency.value = f; o.detune.value = v[1];
        var vg = ctx.createGain(); vg.gain.value = v[2];
        o.connect(vg); vg.connect(g); o.start(t0); o.stop(t0 + dur + 0.4);
      });
      /* a breath of key noise, the felt hitting the string */
      var s = ctx.createBufferSource(); s.buffer = C.noise;
      s.playbackRate.value = 0.9;
      var hp = ctx.createBiquadFilter(); hp.type = "bandpass";
      hp.frequency.value = f * 3; hp.Q.value = 0.9;
      var sg = ctx.createGain();
      s.connect(hp); hp.connect(sg); C.panTo(sg, pan);
      sg.gain.setValueAtTime(0, t0);
      sg.gain.linearRampToValueAtTime(vel * 0.16, t0 + 0.012);
      sg.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.14);
      s.start(t0, rnd(0, 4)); s.stop(t0 + 0.2);

      g.gain.setValueAtTime(0, t0);
      g.gain.linearRampToValueAtTime(vel, t0 + 0.035);
      g.gain.exponentialRampToValueAtTime(vel * 0.28, t0 + dur * 0.55);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur + 0.35);
    }

    /* pad: two slightly detuned saws per note through a filter that opens
       and closes across the bar, so the chord breathes rather than sits. */
    function pad(t0, notes, dur, vel) {
      var lp = ctx.createBiquadFilter();
      lp.type = "lowpass"; lp.Q.value = 0.7;
      lp.frequency.setValueAtTime(560, t0);
      lp.frequency.linearRampToValueAtTime(1150, t0 + dur * 0.45);
      lp.frequency.linearRampToValueAtTime(600, t0 + dur);
      var g = ctx.createGain(); g.connect(lp); C.panTo(lp, rnd(-0.1, 0.1));
      notes.forEach(function (m) {
        var f = mtof(m);
        [-6, 6].forEach(function (dt) {
          var o = ctx.createOscillator(); o.type = "sawtooth";
          o.frequency.value = f; o.detune.value = dt;
          var vg = ctx.createGain(); vg.gain.value = 0.5 / notes.length;
          o.connect(vg); vg.connect(g); o.start(t0); o.stop(t0 + dur + 0.6);
        });
      });
      g.gain.setValueAtTime(0, t0);
      g.gain.linearRampToValueAtTime(vel, t0 + dur * 0.3);
      g.gain.setValueAtTime(vel, t0 + dur * 0.62);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur + 0.5);
    }

    /* upright bass: short round pluck, a little string in the attack */
    function bass(t0, midi, vel) {
      var f = mtof(midi), g = ctx.createGain();
      var lp = ctx.createBiquadFilter();
      lp.type = "lowpass"; lp.frequency.value = 340; lp.Q.value = 1.4;
      g.connect(lp); C.panTo(lp, -0.06);
      [["sine", 1], ["triangle", 0.28]].forEach(function (v) {
        var o = ctx.createOscillator(); o.type = v[0]; o.frequency.value = f;
        var vg = ctx.createGain(); vg.gain.value = v[1];
        o.connect(vg); vg.connect(g); o.start(t0); o.stop(t0 + 1.5);
      });
      g.gain.setValueAtTime(0, t0);
      g.gain.linearRampToValueAtTime(vel, t0 + 0.02);
      g.gain.exponentialRampToValueAtTime(vel * 0.2, t0 + 0.5);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.3);
    }

    /* brushed shaker, wide and very quiet: texture, not a beat */
    function brush(t0, vel, pan) {
      var s = ctx.createBufferSource(); s.buffer = C.noise;
      s.playbackRate.value = rnd(1.1, 1.35);
      var bp = ctx.createBiquadFilter();
      bp.type = "bandpass"; bp.frequency.value = rnd(3800, 5600); bp.Q.value = 0.7;
      var g = ctx.createGain();
      s.connect(bp); bp.connect(g); C.panTo(g, pan);
      g.gain.setValueAtTime(0, t0);
      g.gain.linearRampToValueAtTime(vel, t0 + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.26);
      s.start(t0, rnd(0, 4)); s.stop(t0 + 0.35);
    }

    /* vibraphone bell: sine partials, long tail, used sparingly */
    function bell(t0, midi, vel) {
      var f = mtof(midi), g = ctx.createGain();
      C.panTo(g, rnd(-0.5, 0.5));
      [[1, 0.5, 3.4], [4.0, 0.10, 1.8], [9.2, 0.03, 0.9]].forEach(function (p) {
        var o = ctx.createOscillator(); o.type = "sine";
        o.frequency.value = f * p[0];
        var vg = ctx.createGain();
        vg.gain.setValueAtTime(0, t0);
        vg.gain.linearRampToValueAtTime(p[1] * vel, t0 + 0.02);
        vg.gain.exponentialRampToValueAtTime(0.0001, t0 + p[2]);
        o.connect(vg); vg.connect(g); o.start(t0); o.stop(t0 + p[2] + 0.1);
      });
      /* slow tremolo, the vibraphone fan */
      var trem = ctx.createOscillator(), tg = ctx.createGain();
      trem.frequency.value = 4.2; tg.gain.value = 0.22;
      g.gain.value = 0.78; trem.connect(tg); tg.connect(g.gain);
      trem.start(t0); trem.stop(t0 + 3.6);
    }

    function bar(t0, idx) {
      var b = idx % 4, loop = Math.floor(idx / 4);
      var ch = CH[b];

      pad(t0, ch.pad, BAR, 0.055);
      bass(t0, ch.root, 0.30);
      if (b !== 2) bass(t0 + 2.5 * BEAT, ch.fifth, 0.18);

      /* piano figure: four notes, loosely placed, never metronomic */
      ch.arp.forEach(function (m, i) {
        var t = t0 + [0, 1.5, 2.25, 3.25][i] * BEAT + rnd(-0.02, 0.03);
        var oct = loop % 3 === 2 && i > 1 ? 12 : 0;
        felt(t, m + oct, rnd(1.5, 2.3), 0.085 - i * 0.008, rnd(-0.3, 0.3));
      });

      /* shaker on the two soft beats only */
      brush(t0 + BEAT, 0.013, 0.42);
      brush(t0 + 3 * BEAT, 0.010, -0.36);

      /* melody for this bar */
      MEL.forEach(function (n) {
        if (n[0] < b * 4 || n[0] >= b * 4 + 4) return;
        var t = t0 + (n[0] - b * 4) * BEAT;
        var m = n[1] - (loop % 3 === 1 ? 12 : 0);
        felt(t, m, n[2], 0.105, rnd(-0.14, 0.14));
      });

      /* one bell per loop at most, on the turn back to the top */
      if (b === 3 && Math.random() < 0.55) bell(t0 + 2 * BEAT, pick([81, 84, 88]), 0.055);
      if (b === 1 && Math.random() < 0.22) bell(t0 + 3 * BEAT, pick([76, 79]), 0.04);
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
    var v = room(ctx, C);
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
