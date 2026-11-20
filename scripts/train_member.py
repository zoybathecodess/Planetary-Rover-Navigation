"""Train ONE ensemble member (DQN + randomized prior + bootstrap).
   python scripts/train_member.py --config configs/sim32_id_ensemble.yaml --seed 1003 --out results/task4/train/ens_s1_m3"""
from _common import ROOT, parse  # noqa: F401

import torch

from src.agents.ensemble_member import EnsembleMemberDQN
from src.config import load_config
from src.evaluation.evaluator import make_env
from src.seeding import seed_everything
from src.training.loops import train_dqn
from src.utils.run_meta import write_meta

args, ov = parse("Train ensemble member")
cfg = load_config(ROOT / args.config, ov)
out = args.out or f"{cfg.run.out_dir}_member_s{cfg.run.seed}"
torch.set_num_threads(cfg.run.torch_threads)
seed_everything(cfg.run.seed)
write_meta(out, cfg.to_dict())
probe, _ = make_env(cfg.env, cfg.run.seed)
agent = EnsembleMemberDQN(probe.obs_dim, probe.n_actions, cfg.dqn, seed=cfg.run.seed)
s = train_dqn(agent, cfg, out)
print(f"[MEMBER] train SR(last100)={s['train_time_SR_last100']:.2f}  greedy val SR={s['greedy_val_200']['success_rate']:.2f}  "
      f"wall={s['wall_seconds']}s  -> {out}")
