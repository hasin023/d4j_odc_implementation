"""Recompute every statistic reported in Chapter 6 of the defence book from the raw
classification artifacts, using the pipeline's own comparison functions.

Scopes: the five projects evaluated before Closure (257 bugs), Closure alone (153),
and all six projects (410). Bootstrap CIs and permutation p-values are Monte Carlo
estimates (fixed seed 20260915); endpoints move by about +/-0.01-0.03 between seeds.

Usage (from the repo root, venv active):
    python scripts/analysis/recompute_rq_statistics.py six       # 410-bug figures
    python scripts/analysis/recompute_rq_statistics.py closure
    python scripts/analysis/recompute_rq_statistics.py five

Explained in docs/defence_math/.
"""
import json, math, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
sys.path.insert(0, str(ROOT))
from d4j_odc_pipeline.comparison import compare_classifications, compute_cohens_kappa
from d4j_odc_pipeline.odc import family_for
from d4j_odc_pipeline.analysis import compute_taxonomy_grounding_metrics

V2 = ROOT / ".dist/study/artifacts_v2"
FULL = ROOT / ".dist/study/artifacts_full"
TRI = {"Checking", "Algorithm/Method", "Assignment/Initialization"}


def load(base, mode, key, tag):
    p = base / mode / f"{key}_{mode}" / f"classification.{tag}.json"
    return json.loads(p.read_text()) if p.exists() else None


keys = sorted({d.name.rsplit("_", 1)[0] for d in (V2 / "prefix").iterdir() if d.is_dir()},
              key=lambda k: (k.split("_")[0], int(k.split("_")[1])))
DATA = {}
for k in keys:
    rec = {m: {t: load(V2, m, k, t) for t in ("scientific-open", "few-open")} for m in ("prefix", "postfix")}
    rec["zero"] = {m: load(FULL, m, k, "zero-free") for m in ("prefix", "postfix")}
    if all(rec[m][t] for m in ("prefix", "postfix") for t in ("scientific-open", "few-open")):
        ctxp = V2 / "prefix" / f"{k}_prefix" / "context.json"
        rec["ctx"] = json.loads(ctxp.read_text())
        DATA[k] = rec
proj = lambda k: k.split("_")[0]
R = random.Random(20260915)


def pct(x): return f"{100*x:.1f}%"


def kappa(pairs):
    v = compute_cohens_kappa(pairs); return v if v is not None else float("nan")


def boot(fn, items, B=2000):
    vals = []
    for _ in range(B):
        s = [items[R.randrange(len(items))] for _ in items]
        v = fn(s)
        if v == v: vals.append(v)
    vals.sort(); return vals[int(0.025*len(vals))], vals[int(0.975*len(vals))-1]


def mcnemar(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    p = 2 * sum(math.comb(n, i) for i in range(k+1)) / 2**n
    return min(1.0, p)


def tvd(a, b):
    ca, cb = Counter(a), Counter(b); n = len(a)
    return 0.5 * sum(abs(ca[t]/n - cb[t]/n) for t in set(ca) | set(cb))


def chi2(rows_labels):
    # rows_labels: list of (project, label)
    projs = sorted({p for p, _ in rows_labels}); types = sorted({t for _, t in rows_labels})
    def stat(pairs):
        tab = Counter(pairs); rp = Counter(p for p, _ in pairs); ct = Counter(t for _, t in pairs); n = len(pairs)
        return sum((tab[(p, t)] - rp[p]*ct[t]/n)**2 / (rp[p]*ct[t]/n) for p in projs for t in types)
    obs = stat(rows_labels)
    ps = [p for p, _ in rows_labels]; ls = [t for _, t in rows_labels]
    ge = 0
    for _ in range(10000):
        R.shuffle(ls)
        if stat(list(zip(ps, ls))) >= obs - 1e-9: ge += 1
    n = len(rows_labels); dof = (len(projs)-1)*(len(types)-1)
    V = math.sqrt(obs / (n * (min(len(projs), len(types)) - 1)))
    return obs, dof, (ge+1)/10001, V


def mod_classes(ctx):
    raw = (ctx.get("hidden_oracles") or {}).get("classes.modified", "") or ""
    return [c.strip() for c in re.split(r"[;,\s]+", raw) if c.strip()]


def probes(c): return [t for t in (c.get("turns") or []) if t.get("probe")]


def analyse(label, ks):
    n = len(ks)
    out = {"scope": label, "n": n}
    print(f"\n##################  {label}  (n={n})  ##################")
    print("projects:", dict(Counter(proj(k) for k in ks)))
    lab = lambda k, m, t: DATA[k][m][t]["odc_type"]
    conds = {"sci": "scientific-open", "few": "few-open"}
    # ---------- RQ1
    print("\n[RQ1] distribution")
    for m in ("prefix", "postfix"):
        for c, t in conds.items():
            cnt = Counter(lab(k, m, t) for k in ks)
            tri = sum(cnt[x] for x in TRI)
            print(f"  {c}-{m}: {dict(cnt.most_common())}  tri={tri}/{n}={pct(tri/n)}")
    for c, t in conds.items():
        if len({proj(k) for k in ks}) < 2: break
        o, dof, p, V = chi2([(proj(k), lab(k, "prefix", t)) for k in ks])
        print(f"  chi2 {c}-prefix: chi2={o:.2f} dof={dof} MCp={p:.3f} V={V:.3f}")
    print("  per-project sci prefix:")
    for pj in sorted({proj(k) for k in ks}):
        pk = [k for k in ks if proj(k) == pj]; cnt = Counter(lab(k, "prefix", "scientific-open") for k in pk)
        print(f"    {pj}: n={len(pk)} ALG={cnt['Algorithm/Method']} CHK={cnt['Checking']} ASN={cnt['Assignment/Initialization']} rest={len(pk)-cnt['Algorithm/Method']-cnt['Checking']-cnt['Assignment/Initialization']}")
    print(f"  TVD sci-pre vs few-pre = {tvd([lab(k,'prefix','scientific-open') for k in ks],[lab(k,'prefix','few-open') for k in ks]):.3f}")
    for c, t in conds.items():
        print(f"  TVD {c} pre vs post = {tvd([lab(k,'prefix',t) for k in ks],[lab(k,'postfix',t) for k in ks]):.3f}")
    # ---------- RQ2
    print("\n[RQ2] escapes")
    allc = [DATA[k][m][t] for k in ks for m in ("prefix", "postfix") for t in conds.values()]
    print(f"  total={len(allc)} other_primary={sum(c['odc_type']=='Other' for c in allc)}"
          f" other_in_alts={sum(any(a.get('type')=='Other' for a in (c.get('alternative_types') or [])) for c in allc)}"
          f" justification={sum(bool(c.get('other_justification')) for c in allc)}"
          f" types_used={sorted(set(c['odc_type'] for c in allc))}")
    for m in ("prefix", "postfix"):
        for c, t in conds.items():
            print(f"  review flags {c}-{m} = {sum(bool(DATA[k][m][t].get('needs_human_review')) for k in ks)}"
                  f"  lowconf(<0.5) = {sum((DATA[k][m][t].get('confidence') or 1) < 0.5 for k in ks)}")
    rare = Counter(c["odc_type"] for c in allc)
    print(f"  rare usage: REL={rare['Relationship']} INT={rare['Interface/O-O Messages']} FCO={rare['Function/Class/Object']} TIM={rare['Timing/Serialization']}")
    print(f"  rule of three: per-cond {pct(3/n)}  pooled {pct(3/len(allc))}")
    # ---------- RQ3 / RQ5
    print("\n[RQ3] four levels")
    res = {}
    for c, t in conds.items():
        comps = {k: compare_classifications(DATA[k]["prefix"][t], DATA[k]["postfix"][t]) for k in ks}
        res[c] = comps
        strict = sum(r.strict_match for r in comps.values())/n
        pairs = [(lab(k, "prefix", t), lab(k, "postfix", t)) for k in ks]
        kap = kappa(pairs)
        s_ci = boot(lambda s: sum(a == b for a, b in s)/len(s), pairs)
        k_ci = boot(kappa, pairs)
        top2 = sum(r.top2_match for r in comps.values())/n
        fam = sum(r.family_match for r in comps.values())/n
        drift = [k for k in ks if not comps[k].strict_match]
        nm = sum(comps[k].top2_match for k in drift); fm = sum(comps[k].family_match for k in drift)
        unrel = [k for k in drift if not comps[k].top2_match and not comps[k].family_match]
        # shuffle baseline
        t2s, fs = [], []
        post = [DATA[k]["postfix"][t] for k in ks]
        for _ in range(200):
            R.shuffle(post)
            cc = [compare_classifications(DATA[k]["prefix"][t], p) for k, p in zip(ks, post)]
            t2s.append(sum(x.top2_match for x in cc)/n); fs.append(sum(x.family_match for x in cc)/n)
        print(f"  {c}: strict={pct(strict)} CI=({pct(s_ci[0])}-{pct(s_ci[1])}) kappa={kap:.3f} CI=({k_ci[0]:.3f}-{k_ci[1]:.3f})"
              f" top2={pct(top2)} fam={pct(fam)} | drifts={len(drift)} ({pct(len(drift)/n)}) nearmiss={nm} {pct(nm/len(drift))}"
              f" famInDrift={fm} {pct(fm/len(drift))} unrelated={len(unrel)} ({pct(len(unrel)/len(drift))} of drifts, {pct(len(unrel)/n)} of all) {unrel}"
              f" | shuffle top2={pct(sum(t2s)/len(t2s))} fam={pct(sum(fs)/len(fs))}")
        dp = Counter()
        for k in drift: dp[(lab(k, 'prefix', t), lab(k, 'postfix', t))] += 1
        und = Counter()
        for (a, b), v in dp.items(): und[tuple(sorted((a, b)))] += v
        tri_d = sum(v for (a, b), v in dp.items() if a in TRI and b in TRI)
        print(f"     drift pairs: {[(p, v, dp[p], dp[(p[1], p[0])]) for p, v in und.most_common(6)]}  inTriangle={tri_d}/{len(drift)}={pct(tri_d/len(drift))}")
    # strategy agreement
    for m in ("prefix", "postfix"):
        pairs = [(lab(k, m, "scientific-open"), lab(k, m, "few-open")) for k in ks]
        print(f"  sci-vs-few {m}: {pct(sum(a==b for a,b in pairs)/n)} kappa={kappa(pairs):.3f}")
    # ---------- per project
    print("\n[RQ5] per project")
    sdk = {"sci": [], "few": []}
    for pj in sorted({proj(k) for k in ks}):
        pk = [k for k in ks if proj(k) == pj]
        row = [pj, len(pk)]
        for c, t in conds.items():
            pairs = [(lab(k, "prefix", t), lab(k, "postfix", t)) for k in pk]
            kv = kappa(pairs); ci = boot(kappa, pairs); sdk[c].append(kv)
            row += [pct(sum(a == b for a, b in pairs)/len(pk)), f"{kv:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]"]
        pre = sum(lab(k, 'prefix', 'scientific-open') == lab(k, 'prefix', 'few-open') for k in pk)/len(pk)
        post = sum(lab(k, 'postfix', 'scientific-open') == lab(k, 'postfix', 'few-open') for k in pk)/len(pk)
        row += [f"stratAgree pre={pct(pre)} post={pct(post)}", f"dK={sdk['sci'][-1]-sdk['few'][-1]:+.3f}"]
        print("  ", row)
    if len(sdk['sci']) < 2: sdk['sci'] += sdk['sci']; sdk['few'] += sdk['few']
    sd = lambda xs: math.sqrt(sum((x - sum(xs)/len(xs))**2 for x in xs)/(len(xs)-1))
    wins = sum(a > b for a, b in zip(sdk['sci'], sdk['few']))
    P = len(sdk['sci'])
    print(f"  sd sci={sd(sdk['sci']):.3f} few={sd(sdk['few']):.3f} min sci={min(sdk['sci']):.3f} few={min(sdk['few']):.3f}"
          f" wins={wins}/{P} signtest one-sided p={sum(math.comb(P,i) for i in range(wins,P+1))/2**P:.3f}")
    # ---------- RQ4b
    print("\n[RQ4b] loop vs few")
    trip = [(lab(k, 'prefix', 'scientific-open'), lab(k, 'postfix', 'scientific-open'),
             lab(k, 'prefix', 'few-open'), lab(k, 'postfix', 'few-open')) for k in ks]
    dk = kappa([(a, b) for a, b, _, _ in trip]) - kappa([(c, d) for _, _, c, d in trip])
    diffs = []
    for _ in range(5000):
        s = [trip[R.randrange(n)] for _ in range(n)]
        v = kappa([(a, b) for a, b, _, _ in s]) - kappa([(c, d) for _, _, c, d in s])
        if v == v: diffs.append(v)
    diffs.sort()
    p2 = 2*min(sum(d <= 0 for d in diffs), sum(d >= 0 for d in diffs))/len(diffs)
    print(f"  dKappa={dk:.3f} CI=[{diffs[int(.025*len(diffs))]:.3f}, {diffs[int(.975*len(diffs))-1]:.3f}] p~{p2:.3f}")
    so = sum(a == b and not c == d for a, b, c, d in trip); fo = sum(c == d and not a == b for a, b, c, d in trip)
    print(f"  McNemar raw: sci-only={so} few-only={fo} p={mcnemar(so, fo):.3f}")
    cons = [x for x in trip if x[1] == x[3]]
    sm = sum(x[0] == x[1] for x in cons); fm_ = sum(x[2] == x[3] for x in cons)
    so2 = sum(x[0] == x[1] and x[2] != x[3] for x in cons); fo2 = sum(x[2] == x[3] and x[0] != x[1] for x in cons)
    print(f"  consensus n={len(cons)} sci={pct(sm/len(cons))} few={pct(fm_/len(cons))} McNemar {so2}/{fo2} p={mcnemar(so2, fo2):.3f}")
    print(f"  all four agree: {sum(len(set(x))==1 for x in trip)} ({pct(sum(len(set(x))==1 for x in trip)/n)})")
    few_alg = sum(x[2] == 'Algorithm/Method' for x in trip); print(f"  few prefix ALG count={few_alg}")
    # probes
    for m in ("prefix", "postfix"):
        zero = sum(len(probes(DATA[k][m]['scientific-open'])) == 0 for k in ks)
        print(f"  zero-probe sci-{m}: {zero}")
    instore = retrieved = 0
    byp = defaultdict(lambda: [0, 0])
    for k in ks:
        ctx = DATA[k]["ctx"]; mc = mod_classes(ctx)
        names = {s.get("class_name") for s in ctx.get("code_snippets") or []}
        if any(c in names for c in mc): instore += 1
        c = DATA[k]["prefix"]["scientific-open"]
        got = False
        for tr in probes(c):
            if tr["probe"].get("name") != "snippet": continue
            obs = tr.get("observation") or ""
            if isinstance(obs, (dict, list)): obs = json.dumps(obs)
            if '"error"' in obs[:40]: continue
            if any(re.search(r'"class_name":\s*"' + re.escape(x) + '"', obs) for x in mc): got = True
        retrieved += got
        pc = len(probes(c)); b = min(pc, 3)
        byp[b][0] += 1; byp[b][1] += c["odc_type"] == lab(k, "postfix", "scientific-open")
    print(f"  modified class in store={instore}/{n} ({pct(instore/n)})  retrieved by prefix probe={retrieved}/{n} -> not reached {pct(1-retrieved/n)}")
    print("  agreement by probes:", {b: f"{v[1]}/{v[0]}={pct(v[1]/v[0])}" for b, v in sorted(byp.items())})
    # ---------- RQ4a
    zk = [k for k in ks if DATA[k]["zero"]["prefix"] and DATA[k]["zero"]["postfix"]]
    print(f"\n[RQ4a] zero-free coverage {len(zk)}/{n}")
    if zk:
        zl = [DATA[k]["zero"]["prefix"]["odc_type"] for k in zk]
        cnt = Counter(zl)
        H = -sum(v/len(zl)*math.log2(v/len(zl)) for v in cnt.values())
        tiers = [("zero-free", [DATA[k]["zero"]["prefix"] for k in zk]),
                 ("few-open", [DATA[k]["prefix"]["few-open"] for k in zk]),
                 ("scientific-open", [DATA[k]["prefix"]["scientific-open"] for k in zk])]
        g = compute_taxonomy_grounding_metrics(tiers=tiers)
        rep = sum(DATA[k]["zero"]["prefix"]["odc_type"] == DATA[k]["zero"]["postfix"]["odc_type"] for k in zk)
        zp = [(DATA[k]["zero"]["prefix"]["odc_type"], DATA[k]["zero"]["postfix"]["odc_type"]) for k in zk]
        unk = g["tiers"]["zero-free"]["mapped_distribution"].get("Unknown", 0)
        print(f"  distinct={len(cnt)} singletons={sum(v==1 for v in cnt.values())} top={cnt.most_common(3)} entropy={H:.3f}"
              f" reproducible={rep}/{len(zk)}={pct(rep/len(zk))} kappa={kappa(zp):.3f} vocabRed={g['vocabulary_reduction_ratio']} unknownMapped={unk}")
        for t in ("few-open", "scientific-open"):
            fl = [DATA[k]["prefix"][t]["odc_type"] for k in zk]; c2 = Counter(fl)
            print(f"  {t}: distinct={len(c2)} entropy={-sum(v/len(fl)*math.log2(v/len(fl)) for v in c2.values()):.3f}")
            nz = lambda s: re.sub(r"\s+", " ", s.strip().lower())
            a = sum(DATA[k]['prefix'][t]['odc_type'] == DATA[k]['postfix'][t]['odc_type'] and not nz(DATA[k]['zero']['prefix']['odc_type']) == nz(DATA[k]['zero']['postfix']['odc_type']) for k in zk)
            b = sum(not DATA[k]['prefix'][t]['odc_type'] == DATA[k]['postfix'][t]['odc_type'] and nz(DATA[k]['zero']['prefix']['odc_type']) == nz(DATA[k]['zero']['postfix']['odc_type']) for k in zk)
            print(f"    McNemar vs zero: {a}/{b} p={mcnemar(a,b):.2e}")


five = [k for k in DATA if proj(k) != "Closure"]
clos = [k for k in DATA if proj(k) == "Closure"]
which = sys.argv[1] if len(sys.argv) > 1 else "all"
if which in ("five", "all"): analyse("FIVE ORIGINAL PROJECTS", five)
if which in ("closure", "all"): analyse("CLOSURE", clos)
if which in ("six", "all"): analyse("ALL SIX PROJECTS", five + clos)
