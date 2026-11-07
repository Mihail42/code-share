"""Turns one finished training run into a RunData row (local database) and a CSV row (backup)."""

import os
import uuid
from dataclasses import fields

import yaml

from storage import local_store
from storage.run_data_model import ExperimentType, RunData

TABLE = "our_run_data"
RUN_DATA_FIELDS = [field.name for field in fields(RunData)]
EXPERIMENT_TYPES = [item.value for item in ExperimentType]

# fmt: off
# CSV-only columns (first), followed by every RunData column
EXTRA_CSV_FIELDS = [
    "run_id", "saved_to_db",                            # identification / was it stored in the database
    "exit_code", "interrupted", "early_stopped",        # how it ended
    "reached_threshold",                                # the real convergence result (converged is always 1 for now)
    "num_envs", "agents_per_env",                       # not in the database yet
    "duration_s", "startup_s", "training_elapsed_s",    # whole run / loading until Unity connected / ML-Agents' time
    "best_mean_reward",
]
# fmt: on
CSV_FIELDS = EXTRA_CSV_FIELDS + RUN_DATA_FIELDS

HARDWARE_FIELDS = [
    "os_name", "cpu_model", "cpu_physical_cores_total", "cpu_logical_cores_total",
    "cpu_p_cores_allocated", "cpu_e_cores_allocated", "cpu_p_core_max_ghz",
    "cpu_e_core_max_ghz", "ram_total_mb", "ram_allocated_limit_mb", "ram_speed_mhz", "ram_type",
]  # fmt: skip


def read_hyperparameters(run_config_path, fallback_path):
    """Reads the settings the run actually used: ML-Agents writes them, with all its defaults
    filled in, to <results>/<run_id>/configuration.yaml. Falls back to the training config."""
    path = run_config_path if os.path.exists(run_config_path) else fallback_path
    with open(path, encoding="utf-8") as file:
        config = yaml.safe_load(file)
    behavior = list(config["behaviors"].values())[0]  # the runner tracks the first behavior
    hyper = behavior.get("hyperparameters") or {}
    network = behavior.get("network_settings") or {}
    extrinsic = (behavior.get("reward_signals") or {}).get("extrinsic") or {}
    algo = str(behavior.get("trainer_type", "")).upper()

    values = {
        "algo": algo,
        "learning_rate": hyper.get("learning_rate"),
        "learning_rate_schedule": hyper.get("learning_rate_schedule"),
        "batch_size": hyper.get("batch_size"),
        "buffer_size": hyper.get("buffer_size"),
        "normalize": network.get("normalize"),
        "hidden_units": network.get("hidden_units"),
        "num_layers": network.get("num_layers"),
        "vis_encode_type": network.get("vis_encode_type"),
        "gamma": extrinsic.get("gamma"),
        "reward_strength": extrinsic.get("strength"),
        "keep_checkpoints": behavior.get("keep_checkpoints"),
        "max_steps": behavior.get("max_steps"),
        "time_horizon": behavior.get("time_horizon"),
        "summary_freq": behavior.get("summary_freq"),
    }
    # PPO columns stay empty for SAC runs and the other way around
    for column, key in [("ppo_beta", "beta"), ("ppo_epsilon", "epsilon"),
                        ("ppo_lambd", "lambd"), ("ppo_num_epoch", "num_epoch")]:  # fmt: skip
        values[column] = hyper.get(key) if algo == "PPO" else None
    for column, key in [("sac_buffer_init_steps", "buffer_init_steps"), ("sac_tau", "tau"),
                        ("sac_steps_per_update", "steps_per_update"),
                        ("sac_save_replay_buffer", "save_replay_buffer"),
                        ("sac_init_entcoef", "init_entcoef"),
                        ("sac_reward_signal_steps_per_update", "reward_signal_steps_per_update")]:  # fmt: skip
        values[column] = hyper.get(key) if algo == "SAC" else None
    return values


def average(samples, digits):
    if len(samples) == 0:
        return None
    return round(sum(samples) / len(samples), digits)


def peak(samples, digits):
    if len(samples) == 0:
        return None
    return round(max(samples), digits)


def build_row(run, config, specs, identity, duration, exit_code):
    """Every CSV column for one run; values stay None when there is no data (e.g. a crash at the start)"""
    row = {name: None for name in CSV_FIELDS}
    early_stop = config["early_stop"]

    # identification
    row["run_id"] = run.run_id
    row["id"] = str(uuid.uuid4())
    row["name"] = identity["name"]
    row["machine_id"] = identity["machine"]
    row["experiment_type"] = config["experiment_type"]
    row["seed"] = run.seed

    # how it ended
    row["exit_code"] = exit_code
    row["interrupted"] = run.interrupted
    row["early_stopped"] = run.early_stopped
    row["num_envs"] = config["num_envs"]
    row["agents_per_env"] = config["agents_per_env"]
    row["duration_s"] = round(duration, 1)
    if run.training_started_at is not None:
        row["startup_s"] = round(run.training_started_at - run.start_time, 1)

    # hardware + hyperparameters
    for name in HARDWARE_FIELDS:
        row[name] = specs[name]
    run_config_path = os.path.join(config["work_dir"], run.run_id, "configuration.yaml")
    try:
        row.update(read_hyperparameters(run_config_path, config["training_config_path"]))
    except (OSError, ValueError, KeyError, IndexError, AttributeError) as error:
        print(f"{run.run_id}: could not read the hyperparameters ({error})", flush=True)

    # runtime telemetry
    row["ml_agents_avg_cpu_util"] = average(run.cpu_samples, 2)
    row["ml_agents_peak_cpu_util"] = peak(run.cpu_samples, 2)
    row["background_avg_cpu_util"] = average(run.background_samples, 2)
    row["p_core_avg_util"] = average(run.p_core_samples, 2) if specs["p_core_ids"] else 0.0
    row["e_core_avg_util"] = average(run.e_core_samples, 2) if specs["e_core_ids"] else 0.0
    row["avg_effective_clock_ghz"] = average(run.clock_samples, 2)
    row["avg_ram_usage_mb"] = average(run.ram_samples, 1)
    row["peak_ram_usage_mb"] = peak(run.ram_samples, 1)

    # results
    row["convergence_threshold"] = early_stop["threshold"]
    row["consecutive_hits_above_threshold"] = early_stop["consecutive"]
    row["reached_threshold"] = run.converged_at is not None
    row["converged"] = True  # placeholder: every stored run counts as converged for now
    if len(run.summaries) > 0:
        last = run.summaries[-1]
        steps = run.final_steps if run.final_steps is not None else last["step"]
        row["total_steps_executed"] = steps
        row["final_mean_reward"] = last["mean"]
        row["final_std_reward"] = last["std"]
        row["best_mean_reward"] = max(summary["mean"] for summary in run.summaries)
        row["training_elapsed_s"] = last["elapsed"]
        if last["elapsed"] > 0:
            row["step_throughput"] = round(last["step"] / last["elapsed"], 2)
        if run.converged_at is not None:
            row["steps_to_convergence"] = run.converged_at["step"]
            row["time_to_convergence_s"] = run.converged_at["elapsed"]
        else:  # never reached the threshold: the whole run
            row["steps_to_convergence"] = steps
            row["time_to_convergence_s"] = last["elapsed"]
    return row


def save_to_db(conn, row):
    """Inserts the run into the local database; returns an error text, or None when it worked"""
    try:
        run_data = RunData(**{name: row[name] for name in RUN_DATA_FIELDS})
        local_store.insert_run(conn, TABLE, run_data)
    except Exception as error:  # e.g. a missing value in a NOT NULL column
        return str(error)
    return None
