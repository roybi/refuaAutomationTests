// Simulates the homepage run list (refua_service/static/index.html) against a fake API, with runs arriving while pages are loaded.
// Run from the repository root: node tools/tests/js/runlist_sim.js (exit code 1 on any FAIL). Used by tools/tests/test_homepage_run_list.py.
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync('refua_service/static/index.html', 'utf8');
const script = html.match(/<script>([\s\S]*)<\/script>/)[1];
const block = script.slice(script.indexOf('const PAGE = 50'), script.indexOf('function select(id)'));

function makeWorld(total) {
  let runs = Array.from({ length: total }, (_, i) => ({ id: 'run-' + String(total - i).padStart(4, '0'), status: 'passed' }));
  const world = { rendered: [], calls: 0 };
  world.addRun = () => { runs.unshift({ id: 'run-' + String(runs.length + 1).padStart(4, '0'), status: 'passed' }); };
  const els = {};
  const el = id => els[id] || (els[id] = { value: '', hidden: false, textContent: '', className: '' });
  const ctx = {
    $: el, selected: null, URLSearchParams,
    api: async path => {
      world.calls++;
      await new Promise(r => setTimeout(r, Math.random() * 3));
      const q = new URLSearchParams(path.split('?')[1]);
      const limit = +q.get('limit'), offset = +(q.get('offset') || 0);
      if (limit > 500) throw new Error('limit too large');
      return runs.slice(offset, offset + limit);
    },
    renderRuns: list => { world.rendered = list.map(r => r.id); },
    showDetail: async () => {}, console,
  };
  vm.createContext(ctx);
  vm.runInContext(block + '\nthis.refresh = refresh; this.loadMore = loadMore; this.filtersChanged = filtersChanged;', ctx);
  world.ctx = ctx; world.runs = () => runs;
  return world;
}

function assertNoGap(world, label) {
  const expected = world.runs().slice(0, world.rendered.length).map(r => r.id);
  const ok = JSON.stringify(expected) === JSON.stringify(world.rendered);
  console.log((ok ? 'PASS ' : 'FAIL ') + label + ' (' + world.rendered.length + ' shown)');
  if (!ok) { console.log(' expected head', expected.slice(0, 3), 'got', world.rendered.slice(0, 3)); process.exitCode = 1; }
}

(async () => {
  let w = makeWorld(180);
  await w.ctx.refresh(); assertNoGap(w, 'first page');
  await w.ctx.loadMore(); assertNoGap(w, 'after Load more');
  w.addRun(); await w.ctx.refresh(); assertNoGap(w, 'new run after Load more (the old bug)');
  w.addRun(); w.addRun(); await w.ctx.refresh(); assertNoGap(w, 'two more runs');
  await w.ctx.loadMore(); assertNoGap(w, 'Load more again');
  await w.ctx.loadMore(); assertNoGap(w, 'Load more to the end');
  console.log((w.rendered.length === w.runs().length ? 'PASS ' : 'FAIL ') + 'all runs reachable: ' + w.rendered.length + '/' + w.runs().length);
  if (w.rendered.length !== w.runs().length) process.exitCode = 1;
  w.ctx.$('loadMore'); console.log((w.ctx.$('loadMore').hidden ? 'PASS ' : 'FAIL ') + 'Load more hidden at the end');

  w = makeWorld(300);
  await w.ctx.refresh();
  const jobs = [w.ctx.loadMore(), w.ctx.refresh(), w.ctx.loadMore()];  // overlapping calls
  w.addRun(); jobs.push(w.ctx.refresh());
  await Promise.all(jobs); await w.ctx.refresh();
  assertNoGap(w, 'overlapping refresh and Load more');
  const ids = w.rendered; console.log((new Set(ids).size === ids.length ? 'PASS ' : 'FAIL ') + 'no duplicates');
  if (new Set(ids).size !== ids.length) process.exitCode = 1;

  w = makeWorld(700);
  await w.ctx.refresh();
  for (let i = 0; i < 13; i++) await w.ctx.loadMore();
  w.addRun(); await w.ctx.refresh();
  assertNoGap(w, '700 runs, new run after many pages (reload needs more than one API call)');
})();