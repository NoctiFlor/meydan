// Original procedural groove plans. These describe rhythm/harmony events only;
// they contain no sampled audio or transcribed melody.
(() => {
  const freezeProfile = profile => Object.freeze({
    ...profile,
    kick: Object.freeze(profile.kick),
    snare: Object.freeze(profile.snare),
    hat: Object.freeze(profile.hat.map(row => Object.freeze(row))),
    bass: Object.freeze(profile.bass),
    chords: Object.freeze(profile.chords.map(row => Object.freeze(row)))
  });

  // Plans loop every eight quarter-note beats. Pitch values are relative
  // semitones, deliberately short and harmonic rather than melodic phrases.
  const profiles = Object.freeze({
    meydan_demo: freezeProfile({
      id: 'meydan_demo', name: 'Meydan Groove', wave: 'triangle', rootMidi: 45,
      kick:  [1,0,1,0,1,0,1,0],
      snare: [0,1,0,1,0,1,0,1],
      hat:   [[0,.5],[0,.5],[0,.5],[0,.5],[0,.5],[0,.5],[0,.5],[0,.5]],
      bass:  [0,null,0,7,0,null,5,7],
      chords:[[0,4,7],null,[0,4,7],null,[5,9,12],null,[7,11,14],null]
    }),
    gece_isiklari: freezeProfile({
      id: 'gece_isiklari', name: 'Gece Işıkları', wave: 'sawtooth', rootMidi: 42,
      kick:  [1,0,1,0,1,0,1,1],
      snare: [0,1,0,1,0,1,0,1],
      hat:   [[0,.5],[.5],[0,.5],[.5],[0,.5],[.5],[0,.5],[.25,.75]],
      bass:  [0,0,null,7,5,5,null,7],
      chords:[[0,3,7],null,[0,3,7],null,[5,8,12],null,[7,10,14],null]
    }),
    sahil_ritmi: freezeProfile({
      id: 'sahil_ritmi', name: 'Sahil Ritmi', wave: 'sine', rootMidi: 47,
      kick:  [1,1,1,1,1,1,1,1],
      snare: [0,1,0,1,0,1,0,1],
      hat:   [[.5],[.5],[.5],[.5],[.5],[.5],[.5],[.25,.5,.75]],
      bass:  [0,null,7,null,5,null,7,10],
      chords:[[0,4,7,11],null,[7,11,14],null,[5,9,12],null,[7,11,14],null]
    })
  });

  const LOOP_BEATS = 8;
  function profileFor(id) {
    return profiles[id] || profiles.meydan_demo;
  }

  function generateBeat(id, beatIndex) {
    if (!Number.isInteger(beatIndex) || beatIndex < 0) throw new Error('beatIndex must be a non-negative integer');
    const profile = profileFor(id);
    const step = beatIndex % LOOP_BEATS;
    const events = [];
    if (profile.kick[step]) events.push({kind:'kick', offsetBeats:0, velocity:step===0?1:.86});
    if (profile.snare[step]) events.push({kind:'snare', offsetBeats:0, velocity:.78});
    for (const offsetBeats of profile.hat[step]) events.push({kind:'hat', offsetBeats, velocity:offsetBeats===0?.42:.34});
    const bass = profile.bass[step];
    if (bass !== null) events.push({kind:'bass', offsetBeats:0, midi:profile.rootMidi+bass, durationBeats:.72, wave:profile.wave});
    const chord = profile.chords[step];
    if (chord) events.push({kind:'chord', offsetBeats:0, midi:chord.map(note=>profile.rootMidi+12+note), durationBeats:.82});
    return events;
  }

  function generateLoop(id, loopNumber=0) {
    if (!Number.isInteger(loopNumber) || loopNumber < 0) throw new Error('loopNumber must be a non-negative integer');
    const startBeat=loopNumber*LOOP_BEATS;
    return Array.from({length:LOOP_BEATS},(_,index)=>({
      beat:startBeat+index,
      events:generateBeat(id,startBeat+index)
    }));
  }

  globalThis.MeydanMusic = {profiles, LOOP_BEATS, profileFor, generateBeat, generateLoop};
})();
