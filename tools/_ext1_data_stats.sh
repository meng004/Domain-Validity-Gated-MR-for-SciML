#!/usr/bin/env bash
# Diagnostic: inspect airfoil target/edge/feature statistics to explain why the
# under-trained MGN loss is pinned at 1.0 (normalized-mean prediction).
set -uo pipefail
export http_proxy="http://127.0.0.1:7897" https_proxy="http://127.0.0.1:7897" no_proxy="localhost,127.0.0.1"
source "$HOME/ext1-venv/bin/activate"
cd /mnt/d/Codes/Domain-Validity-Gated-MR-for-SciML
python - <<'PY'
import sys, json, numpy as np
sys.path.insert(0, "tools")
import run_physicsnemo_mgn_airfoil_workflow as af
meta = json.loads((af.STAGE_DIR / "meta.json").read_text())
traj_len = 600
NINSPECT = 5
recs = list(af.iter_trajectories("train", meta, NINSPECT))
print(f"inspecting {len(recs)} train trajectories; trajectory_length={meta['trajectory_length']} dt={meta['dt']}")

# Per-frame target-delta magnitude across the trajectory (is signal only in early transient?)
frames = [0,1,2,5,10,25,50,100,200,300,450,598]
print("\n[per-frame target-delta magnitude] (mean over nodes, avg over %d trajs)" % len(recs))
print(" frame |   ||dvel||      ||drho||       |vel|        |rho|")
for t in frames:
    dv, dr, av, ar = [], [], [], []
    for rec in recs:
        _,_,_,feat,tgt,_,_,vel,rho = af.build_graph(rec, t)
        dv.append(np.mean(np.linalg.norm(tgt[:, :2], axis=1)))
        dr.append(np.mean(np.abs(tgt[:, 2])))
        av.append(np.mean(np.linalg.norm(vel, axis=1)))
        ar.append(np.mean(np.abs(rho[:,0])))
    print(f" {t:5d} | {np.mean(dv):.6e} {np.mean(dr):.6e}  {np.mean(av):.4e}  {np.mean(ar):.4e}")

# Aggregate target stats (raw) over a spread of frames -> what z-score sees
stats = af.AirfoilStats()
cache = []
for rec in recs:
    for t in np.linspace(0, traj_len-2, 20, dtype=int):
        _,_,_,feat,tgt,ei,ea,_,_ = af.build_graph(rec, int(t))
        stats.update(feat, tgt); cache.append((feat,tgt,ei,ea))
fm,fs,tm,ts = stats.finalize()
print("\n[normalization stats over linspace(0,598,20) frames]")
print(" feat_mean:", np.round(fm,4)); print(" feat_std :", np.round(fs,4))
print(" tgt_mean :", np.round(tm,6)); print(" tgt_std  :", np.round(ts,6))

# target channel raw percentiles (heavy tail? outlier-dominated std?)
allt = np.concatenate([c[1] for c in cache], axis=0)
print("\n[raw target percentiles per channel dvx,dvy,drho]")
for c,name in enumerate(["dvx","dvy","drho"]):
    col = allt[:,c]
    pct = np.percentile(np.abs(col),[50,90,99,99.9,100])
    print(f"  {name}: abs p50={pct[0]:.3e} p90={pct[1]:.3e} p99={pct[2]:.3e} p99.9={pct[3]:.3e} max={pct[4]:.3e}  std={col.std():.3e}")

# edge attribute magnitudes (UNNORMALIZED raw mesh distances -> could saturate encoders)
ei,ea = cache[0][2], cache[0][3]
print("\n[edge_attr raw magnitude] (rel_x, rel_y, norm) -- unnormalized?")
print("  min:", np.round(ea.min(0),5), " max:", np.round(ea.max(0),5), " mean|.|:", np.round(np.abs(ea).mean(0),5))
print("  feature raw ranges: vel/rho/onehot columns")
allf = np.concatenate([c[0] for c in cache], axis=0)
print("  feat min:", np.round(allf.min(0),4), " max:", np.round(allf.max(0),4))

# What fraction of normalized-target energy is in the top-1% nodes (outlier domination)?
tz = (allt - tm)/ts
e = (tz**2).sum(1)
order = np.argsort(e)[::-1]
top1 = int(0.01*len(e))
print("\n[normalized-target energy] total nodes=%d; top-1%% nodes hold %.1f%% of squared-error energy"
      % (len(e), 100*e[order[:top1]].sum()/e.sum()))
print("  => if a model predicts 0, normalized MSE = mean(z^2) = %.4f (this is the 1.0 plateau)" % (tz**2).mean())
PY
