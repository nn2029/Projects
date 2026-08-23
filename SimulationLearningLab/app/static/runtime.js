async function bootRuntime() {
  const root = document.getElementById('app');
  const url = window.SLL_SPEC_URL || 'simulation-spec.json';
  let spec;
  try {
    const res = await fetch(url);
    spec = await res.json();
    if (!res.ok) throw new Error(spec.detail || 'Could not load simulation spec');
  } catch (err) {
    root.innerHTML = `<main class="rt-shell"><section class="rt-panel"><h1>Runtime error</h1><p>${err.message}</p></section></main>`;
    return;
  }

  const progressKey = `sll-progress:${window.SLL_SESSION_ID || spec.title}`;
  const saved = (() => { try { return JSON.parse(localStorage.getItem(progressKey) || '{}'); } catch { return {}; } })();
  const state = {
    spec,
    stageIndex: Math.min(Number(saved.stageIndex || 0), Math.max(0, spec.stages.length - 1)),
    scenarioId: saved.scenarioId || ((spec.scenarios && spec.scenarios[0] && spec.scenarios[0].id) || null),
    questionState: saved.questionState || {},
    visited: new Set(saved.visited || [0]),
  };

  function persist() {
    localStorage.setItem(progressKey, JSON.stringify({
      stageIndex: state.stageIndex,
      scenarioId: state.scenarioId,
      questionState: state.questionState,
      visited: Array.from(state.visited),
    }));
  }
  function esc(v) { return String(v ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c])); }
  function activeScenario() { return (spec.scenarios || []).find(x => x.id === state.scenarioId) || { id:'default', label:'Default', state_overrides:{} }; }
  function scenarioBaseState() { return { ...(spec.state || {}), ...(activeScenario().state_overrides || {}) }; }
  function currentStage() { return spec.stages[state.stageIndex]; }
  function cumulativeState() {
    const out = scenarioBaseState();
    spec.stages.slice(0, state.stageIndex + 1).forEach(stage => Object.assign(out, stage.state_patch || {}));
    return out;
  }
  function answerStats() {
    let total = 0, answered = 0, correct = 0;
    spec.stages.forEach(stage => (stage.questions || []).forEach((q, i) => {
      total += 1;
      const key = `${stage.id}:${i}`;
      const answer = state.questionState[key];
      if (answer !== undefined && answer !== null && answer !== '') {
        answered += 1;
        if (Array.isArray(q.choices) ? Number(answer) === q.answer_index : true) correct += 1;
      }
    }));
    return { total, answered, correct };
  }
  function mastery() {
    const a = answerStats();
    const stagePart = spec.stages.length ? state.visited.size / spec.stages.length : 0;
    const recallPart = a.total ? a.correct / a.total : stagePart;
    return Math.round((stagePart * .45 + recallPart * .55) * 100);
  }
  function entityCards(layoutClass='entity-grid') {
    const focus = new Set(currentStage().focus_entities || []);
    return `<div class="${layoutClass}">${(spec.entities || []).map(entity => `
      <article class="entity ${focus.has(entity.id) ? 'focus' : ''}">
        <div class="entity-tag">${esc(entity.kind || 'entity')}</div>
        <h4>${esc(entity.label)}</h4><p>${esc(entity.detail || '')}</p>
      </article>`).join('')}</div>`;
  }
  function renderStateMachine() {
    const focus = new Set(currentStage().focus_entities || []);
    const entities = spec.entities || [];
    return `<div class="flow-line">${entities.map((e, i) => `
      <div class="flow-node ${focus.has(e.id) ? 'active' : ''}"><span>${esc(e.kind || 'state')}</span><strong>${esc(e.label)}</strong><small>${esc(e.detail || '')}</small></div>
      ${i < entities.length - 1 ? '<div class="flow-arrow">→</div>' : ''}`).join('')}</div>`;
  }
  function renderFactory() {
    const focus = new Set(currentStage().focus_entities || []);
    return `<div class="factory-floor"><div class="conveyor"></div>${(spec.entities || []).map((e,i) => `
      <div class="factory-station ${focus.has(e.id) ? 'active' : ''}" style="--i:${i}"><div class="chimney"></div><strong>${esc(e.label)}</strong><small>${esc(e.detail || '')}</small></div>`).join('')}</div>`;
  }
  function renderCircuit() {
    const focus = new Set(currentStage().focus_entities || []);
    return `<div class="circuit-board">${(spec.entities || []).map((e,i) => `
      <div class="circuit-node ${focus.has(e.id) ? 'active' : ''}"><span class="port left"></span><strong>${esc(e.label)}</strong><small>${esc(e.kind || 'signal')}</small><span class="port right"></span></div>
      ${i < (spec.entities || []).length - 1 ? '<div class="wire"></div>' : ''}`).join('')}</div>`;
  }
  function renderAgentField() {
    const focus = new Set(currentStage().focus_entities || []);
    const entities = spec.entities || [];
    return `<div class="agent-field">${entities.map((e,i) => {
      const x = 12 + ((i * 29) % 74), y = 18 + ((i * 41) % 64);
      return `<div class="agent ${focus.has(e.id) ? 'active' : ''}" style="left:${x}%;top:${y}%"><span>${esc(e.label)}</span></div>`;
    }).join('')}</div>`;
  }
  function renderTimeline() {
    const focus = new Set(currentStage().focus_entities || []);
    return `<div class="timeline-view">${(spec.entities || []).map((e,i) => `<div class="timeline-item ${focus.has(e.id) ? 'active' : ''}"><div class="timeline-marker">${i+1}</div><div><strong>${esc(e.label)}</strong><p>${esc(e.detail || '')}</p></div></div>`).join('')}</div>`;
  }
  function renderRobotWorld() {
    const focus = new Set(currentStage().focus_entities || []);
    return `<div class="robot-world"><div class="robot-core"><div class="robot-head"></div><div class="robot-body">ROBOT</div></div><div class="robot-orbit">${(spec.entities || []).map((e,i) => `<div class="robot-module ${focus.has(e.id) ? 'active' : ''} module-${i%6}"><strong>${esc(e.label)}</strong><small>${esc(e.kind || '')}</small></div>`).join('')}</div></div>`;
  }
  function renderLayerStack() {
    const focus = new Set(currentStage().focus_entities || []);
    return `<div class="layer-stack">${(spec.entities || []).map((e,i) => `<div class="layer ${focus.has(e.id) ? 'active' : ''}" style="--depth:${i}"><span>${esc(e.kind || 'layer')}</span><strong>${esc(e.label)}</strong><small>${esc(e.detail || '')}</small></div>`).join('')}</div>`;
  }
  function renderIsometricTown() {
    const focus = new Set(currentStage().focus_entities || []);
    return `<div class="iso-town">${(spec.entities || []).map((e,i) => `<div class="iso-building ${focus.has(e.id) ? 'active' : ''}" style="--x:${(i%4)*23};--y:${Math.floor(i/4)*34}"><div class="roof"></div><div class="front"><strong>${esc(e.label)}</strong><small>${esc(e.kind || '')}</small></div></div>`).join('')}</div>`;
  }
  function renderMechanismView() {
    const g = spec.visual_grammar;
    if (g === 'factory') return renderFactory();
    if (g === 'circuit') return renderCircuit();
    if (g === 'agent-field') return renderAgentField();
    if (g === 'timeline') return renderTimeline();
    if (g === 'robot-world') return renderRobotWorld();
    if (g === 'layer-stack') return renderLayerStack();
    if (g === 'isometric-town') return renderIsometricTown();
    return renderStateMachine();
  }
  function renderStateTable() {
    const stateObj = cumulativeState();
    return Object.entries(stateObj).map(([key,value]) => `<div class="state-row"><span>${esc(key)}</span><strong>${esc(typeof value === 'object' ? JSON.stringify(value) : value)}</strong></div>`).join('') || '<p class="muted">No state variables defined.</p>';
  }
  function renderProvenance() {
    const rows = currentStage().provenance || [];
    if (!rows.length) return '<p class="muted">No stage-specific provenance attached.</p>';
    return rows.map(row => `<div class="prov-row"><strong>${esc(row.asset_id || 'asset')}</strong><span>${esc(row.timestamp || '')}</span><p>${esc(row.observation || row.note || '')}</p></div>`).join('');
  }
  function renderQuestions() {
    const stage = currentStage();
    if (!stage.questions || !stage.questions.length) return '<p class="muted">No active-recall prompt for this stage.</p>';
    return stage.questions.map((q,i) => {
      const key = `${stage.id}:${i}`, answer = state.questionState[key];
      const multiple = Array.isArray(q.choices) && q.choices.length, answered = answer !== undefined && answer !== null && answer !== '';
      const isCorrect = multiple ? Number(answer) === q.answer_index : answered;
      return `<div class="question-card"><div class="question-type">${esc(q.type || 'checkpoint')}</div><h4>${esc(q.prompt)}</h4>
        ${multiple ? `<div class="choices">${q.choices.map((choice,idx) => `<button class="choice ${String(answer)===String(idx)?'selected':''}" data-q="${key}" data-answer="${idx}">${esc(choice)}</button>`).join('')}</div>` : `<textarea class="free-answer" data-q="${key}" placeholder="Type your answer here...">${esc(answer || '')}</textarea><div class="free-actions"><button class="secondary" data-submit-free="${key}">Save answer</button></div>`}
        ${answered ? `<div class="feedback ${isCorrect?'ok':'warn'}"><strong>${multiple ? (isCorrect?'Correct':'Try again') : 'Saved response'}</strong><p>${esc(q.explanation || q.answer_text || '')}</p></div>` : ''}</div>`;
    }).join('');
  }
  function renderLedger() {
    return (spec.fidelity_ledger || []).map(row => `<div class="ledger-row"><div class="ledger-meta"><span class="class-badge">${esc(row.classification)}</span>${row.confidence!==null&&row.confidence!==undefined?`<span class="confidence">${Math.round(Number(row.confidence)*100)}%</span>`:''}</div><h4>${esc(row.element)}</h4><p>${esc(row.detail || '')}</p></div>`).join('');
  }
  function renderStageRail() {
    return spec.stages.map((stage,idx) => `<button class="stage-pill ${idx===state.stageIndex?'active':''} ${state.visited.has(idx)?'visited':''}" data-stage="${idx}"><span>${String(idx+1).padStart(2,'0')}</span>${esc(stage.label)}</button>`).join('');
  }
  function render() {
    const stage = currentStage(), scenario = activeScenario(), stats = answerStats(), score = mastery();
    state.visited.add(state.stageIndex); persist();
    root.innerHTML = `<main class="rt-shell grammar-${spec.visual_grammar}">
      <section class="hero rt-panel"><div class="hero-top"><div><div class="eyebrow">SIMULATION LEARNING LAB · ${esc(spec.visual_grammar).toUpperCase()}</div><h1>${esc(spec.title)}</h1><p>${esc(spec.objective || '')}</p></div>
      <div class="hero-controls"><div class="mastery-card"><div><span>Mastery</span><strong>${score}%</strong></div><div class="meter"><i style="width:${score}%"></i></div><small>${stats.correct}/${stats.total || 0} recall prompts correct · ${state.visited.size}/${spec.stages.length} stages explored</small></div>
      <label>Scenario<select id="scenarioSelect">${(spec.scenarios||[]).map(s=>`<option value="${esc(s.id)}" ${s.id===state.scenarioId?'selected':''}>${esc(s.label)}</option>`).join('')}</select></label><div class="nav-buttons"><button class="secondary" id="resetBtn">Reset</button><button class="secondary" id="prevBtn" ${state.stageIndex===0?'disabled':''}>Previous</button><button id="nextBtn" ${state.stageIndex===spec.stages.length-1?'disabled':''}>Next</button></div></div></div>
      <div class="challenge-box"><strong>Guided intro</strong><p>${esc(spec.lesson?.guided_intro || '')}</p>${scenario.description?`<p><strong>Current scenario:</strong> ${esc(scenario.description)}</p>`:''}</div></section>

      <section class="grid-main"><article class="rt-panel stage-panel"><div class="section-head"><div><span class="step">STAGE</span><h2>${esc(stage.label)}</h2></div><span class="chip">${state.stageIndex+1}/${spec.stages.length}</span></div><p class="stage-summary">${esc(stage.summary)}</p><div class="stage-rail">${renderStageRail()}</div>
      <div class="scene-grid"><section><h3>Mechanism view</h3><div class="mechanism-frame">${renderMechanismView()}</div></section><section><h3>State trace</h3><div class="state-box">${renderStateTable()}</div></section></div></article>
      <article class="rt-panel qa-panel"><div class="section-head"><div><span class="step">LEARN</span><h2>Active recall</h2></div></div><div class="questions">${renderQuestions()}</div><div class="challenge-box small"><strong>Challenge</strong><p>${esc(spec.lesson?.challenge_prompt || 'Manipulate the scenario and explain the result.')}</p></div></article></section>

      <section class="grid-main bottom"><article class="rt-panel provenance-panel"><div class="section-head"><div><span class="step">TRACE</span><h2>Provenance</h2></div></div><div class="provenance-list">${renderProvenance()}</div></article>
      <article class="rt-panel ledger-panel"><div class="section-head"><div><span class="step">FIDELITY</span><h2>Accuracy & simplifications</h2></div></div><div class="ledger-list">${renderLedger()}</div></article></section>
    </main>`;

    document.getElementById('scenarioSelect')?.addEventListener('change', e => { state.scenarioId=e.target.value; state.stageIndex=0; render(); });
    document.getElementById('resetBtn')?.addEventListener('click', () => { state.stageIndex=0; state.questionState={}; state.visited=new Set([0]); localStorage.removeItem(progressKey); render(); });
    document.getElementById('prevBtn')?.addEventListener('click', () => { state.stageIndex=Math.max(0,state.stageIndex-1); render(); });
    document.getElementById('nextBtn')?.addEventListener('click', () => { state.stageIndex=Math.min(spec.stages.length-1,state.stageIndex+1); render(); });
    document.querySelectorAll('[data-stage]').forEach(btn => btn.addEventListener('click', () => { state.stageIndex=Number(btn.dataset.stage); render(); }));
    document.querySelectorAll('.choice').forEach(btn => btn.addEventListener('click', () => { state.questionState[btn.dataset.q]=Number(btn.dataset.answer); render(); }));
    document.querySelectorAll('[data-submit-free]').forEach(btn => btn.addEventListener('click', () => { const key=btn.dataset.submitFree; const textarea=document.querySelector(`textarea[data-q="${key}"]`); state.questionState[key]=textarea?textarea.value.trim():''; render(); }));
  }
  render();
}
bootRuntime();
