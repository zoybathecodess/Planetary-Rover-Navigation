"""Train the PPO baseline.  python scripts/train_ppo.py --config configs/baseline_10x10_onboard.yaml --seed 0"""
from _common import ROOT, parse  # noqa: F401

import torch

from src.agents.ppo_agent import PPOAgent
from src.config import load_config
from src.evaluation.evaluator import make_env
from src.seeding import seed_everything
from src.training.loops import train_ppo
from src.utils.run_meta import write_meta

args, ov = parse("Train PPO")
cfg = load_config(ROOT / args.config, ov)
out = args.out or f"{cfg.run.out_dir}_ppo_s{cfg.run.seed}"
torch.set_num_threads(cfg.run.torch_threads)
seed_everything(cfg.run.seed)
write_meta(out, cfg.to_dict())
probe, _ = make_env(cfg.env, cfg.run.seed)  # basic (10x10) or advanced (32x32) env, per cfg.env.kind
agent = PPOAgent(probe.obs_dim, probe.n_actions, cfg.ppo, seed=cfg.run.seed)
s = train_ppo(agent, cfg, out)
test_txt = f"greedy test SR={s['greedy_test_200']['success_rate']:.2f}  " if "greedy_test_200" in s else ""
print(f"[PPO] train SR(last100)={s['train_time_SR_last100']:.2f}  greedy val SR={s['greedy_val_200']['success_rate']:.2f}  "
      f"{test_txt}wall={s['wall_seconds']}s  -> {out}")
