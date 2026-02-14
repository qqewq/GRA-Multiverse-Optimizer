# src/gra_multiverse/vpn_module.py

"""
EN:
VPN / network helper module for GRA-Multiverse-Optimizer.

This module treats different VPN configurations as level-0 subsystems
and a single meta-node as level 1. It uses the multiverse functional
to score configurations and select the one that is "most consistent"
with the meta-goal (e.g., stability / stealth).

RU:
Модуль-помощник для VPN / сетевых конфигураций в GRA-Multiverse-Optimizer.

Разные конфигурации VPN рассматриваются как подсистемы уровня 0,
а единый мета-узел — как уровень 1. Мультиверсный функционал используется
для оценки конфигураций и выбора той, которая наилучшим образом
соответствует мета-цели (например, стабильность / незаметность).
"""

from typing import List, Dict, Any, Callable, Tuple
import numpy as np

from .core import Level, Goal, MultiverseState, MultiverseFunctional
from .optimizer import MultiverseOptimizer


# --- Простейший "эмбеддер" конфигов --- #

def default_vpn_embed(cfg: Dict[str, Any]) -> np.ndarray:
    """
    EN:
    Very simple embedding from a VPN configuration dict into a numeric vector.
    This is only a placeholder; you should replace it with a more meaningful
    encoding (e.g., one-hot for protocol, normalized latency, etc.).

    RU:
    Очень простое отображение конфигурации VPN (dict) в числовой вектор.
    Это заглушка; её следует заменить на более разумное кодирование
    (one-hot для протокола, нормализованные задержки и т.п.).
    """
    # Define some toy features
    protocol_map = {"tcp": 0, "udp": 1, "tls": 2, "grpc": 3, "ws": 4}
    # Fixed vector length (for prototype)
    vec = np.zeros(8, dtype=np.float32)

    # Feature 0: protocol
    proto = cfg.get("protocol", "tcp").lower()
    vec[0] = protocol_map.get(proto, 0)

    # Feature 1: port (scaled)
    port = float(cfg.get("port", 443))
    vec[1] = port / 65535.0

    # Feature 2: obfuscation flag
    vec[2] = 1.0 if cfg.get("obfuscation", False) else 0.0

    # Feature 3: region / country latency proxy
    latency = float(cfg.get("latency_ms", 100.0))
    vec[3] = latency / 1000.0  # normalize

    # Feature 4: jitter
    jitter = float(cfg.get("jitter_ms", 10.0))
    vec[4] = jitter / 500.0

    # Feature 5: packet_loss
    loss = float(cfg.get("packet_loss", 0.01))
    vec[5] = loss

    # Feature 6: rkn_blocked (0/1)
    vec[6] = 1.0 if cfg.get("rkn_blocked", False) else 0.0

    # Feature 7: uptime score (0..1)
    vec[7] = float(cfg.get("uptime_score", 0.5))

    # Normalize
    norm = np.linalg.norm(vec) + 1e-9
    return (vec / norm).astype(np.complex128)


def default_index_dim_fn(a: Tuple[int, ...]) -> int:
    """
    EN: Use last index as level indicator.
    RU: Используем последний индекс как показатель уровня.
    """
    return a[-1]


# --- Основная функция выбора конфигурации --- #

def select_best_vpn_config(
    configs: List[Dict[str, Any]],
    meta_goal: str = "max_stability_and_stealth",
    embed_fn: Callable[[Dict[str, Any]], np.ndarray] = default_vpn_embed,
    lambda0: float = 1.0,
    alpha: float = 0.8,
    step_size: float = 1e-2,
    max_steps: int = 50,
) -> Dict[str, Any]:
    """
    EN:
    Given a list of VPN configuration dictionaries, build a simple multiverse
    (level 0: configs, level 1: meta-node), run multiverse optimization,
    and return the configuration that best matches the optimized meta-state.

    RU:
    По списку конфигураций VPN (dict) строит простой мультиверс
    (уровень 0: конфиги, уровень 1: мета-узел), запускает мультиверсную
    оптимизацию и возвращает конфигурацию, которая лучше всего
    соответствует оптимизированному мета-состоянию.

    Parameters / Параметры:
        configs: список конфигов VPN.
        meta_goal: строка-описание мета-цели (пока используется только для логики целей).
        embed_fn: функция cfg -> np.ndarray (эмбеддер конфигурации).
        lambda0, alpha: гиперпараметры Λ_l.
        step_size, max_steps: параметры оптимизатора.

    Returns / Возвращает:
        dict с полями:
            "config" – выбранная конфигурация,
            "index"  – её индекс,
            "debug"  – служебная информация.
    """
    if len(configs) == 0:
        return {"config": {}, "index": -1, "debug": "no configs provided"}

    # 1. Levels & goals
    level0 = Level(index=0, name="vpn_configs")
    level1 = Level(index=1, name="vpn_meta")

    goal0 = Goal(level=level0, description="local VPN quality (stability, latency, etc.)")
    goal1 = Goal(level=level1, description=f"meta-goal: {meta_goal}")

    levels = [level0, level1]
    goals = [goal0, goal1]

    # 2. Initial multiverse state
    # Use indices (i, 0) for configs and (0, 1) for meta-node.
    states: Dict[Tuple[int, ...], np.ndarray] = {}

    embeds = [embed_fn(cfg) for cfg in configs]
    for i, e in enumerate(embeds):
        states[(i, 0)] = e.copy()

    # Meta-node: average embedding
    meta_vec = np.mean(np.stack(embeds, axis=0), axis=0)
    states[(0, 1)] = meta_vec.astype(np.complex128)

    psi = MultiverseState(states)

    # 3. Functional & optimizer
    functional = MultiverseFunctional(
        levels=levels,
        goals=goals,
        lambda0=lambda0,
        alpha=alpha,
        index_dim_fn=default_index_dim_fn,
    )

    optimizer = MultiverseOptimizer(
        functional=functional,
        step_size=step_size,
    )

    # 4. Optimize
    psi_opt = optimizer.run_to_convergence(
        state=psi,
        max_steps=max_steps,
        tol=1e-6,
        callback=None,
    )

    # 5. Choose config closest to optimized meta-node
    meta_opt = psi_opt[(0, 1)]
    best_idx = 0
    best_sim = -1.0

    for i, e in enumerate(embeds):
        num = float(np.real(np.vdot(e, meta_opt)))
        denom = (np.linalg.norm(e) * np.linalg.norm(meta_opt) + 1e-9)
        sim = num / denom
        if sim > best_sim:
            best_sim = sim
            best_idx = i

    return {
        "config": configs[best_idx],
        "index": best_idx,
        "debug": f"best_cosine_similarity={best_sim:.4f}, n_configs={len(configs)}",
    }
