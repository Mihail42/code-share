"""Runs a batch of ML-Agents trainings against a Unity build, one after another, and records them.

Run from the project root: python runner/run_and_record_batch.py [--config FILE] [--runs N]
Every finished run is stored in the local database (storage/runs.db, table our_run_data).
Every run, failed and interrupted ones included, is also appended to performance.csv as a backup;
failed runs additionally keep their train.log. Upload to Supabase separately: python runner/sync_to_cloud.py
CPU % is of the CPU the runs may use (100 = every allocated core busy), over the trainer + Unity build(s).
CPU/RAM/clock are sampled from the moment training starts (Unity connected), not while ML-Agents is loading.
"""

import argparse
import csv
import json
import os
import random
import re
import shutil
import signal
import subprocess
import sys
import threading
import traceback
import time

import psutil
import yaml

RUNNER_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(RUNNER_DIR)
sys.path.insert(0, ROOT)  # for the storage package

from dotenv import load_dotenv  # noqa: E402

import hardware  # noqa: E402
import run_record  # noqa: E402
from storage import local_store, storage_scripts  # noqa: E402

DEFAULT_CONFIG = os.path.join(RUNNER_DIR, "configs", "automation", "default.yaml")
ENTRY = os.path.join(RUNNER_DIR, "mlagents_entry.py")
MAX_SEED = 2147483647
STATUS_INTERVAL_S = 60  # how often the batch prints a status report
TRAINING_STARTED = "Connected new brain"  # ML-Agents prints this once Unity is connected and training begins
BLOCKED_SIGNS = ["4551", "Application Control", "Smart App Control"]  # Windows blocked a file
BLOCKED_HINT = (
    "Windows blocked a file from running (Smart App Control / App Control). "
    "See Windows Security > App & browser control > Protection history for which file."
)

# e.g. "[INFO] 3DBall. Step: 200000. Time Elapsed: 334.339 s. Mean Reward: 10.556. Std of Reward: 12.853. Training."
# groups: 1 behavior, 2 step, 3 elapsed, 4 mean reward, 5 std of reward
NUMBER = r"(-?\d+(?:\.\d+)?)"
SUMMARY_LINE = re.compile(
    r"\] (\S+)\. Step: (\d+)\. Time Elapsed: " + NUMBER + r" s\. "
    r"Mean Reward: " + NUMBER + r"\. Std of Reward: " + NUMBER
)


def log(message):
    print("[" + time.strftime("%H:%M:%S") + "] " + message, flush=True)


def blocked_by_windows(text):
    return any(sign in text for sign in BLOCKED_SIGNS)


# Read the config
def load_config(path, runs):
    """Reads the config (every key must be set, see default.yaml) and checks it"""
    with open(path) as file:
        config = yaml.safe_load(file)
    if runs is not None:  # command line override
        config["total_runs"] = runs
    config["config_path"] = os.path.abspath(path)
    config["training_config_path"] = os.path.normpath(os.path.join(ROOT, config["training_config"]))
    config["env_path"] = os.path.normpath(os.path.join(ROOT, config["env_path"]))
    config["output_dir"] = os.path.normpath(os.path.join(ROOT, config["output_dir"]))
    config["work_dir"] = os.path.join(config["output_dir"], "_work")  # ML-Agents output
    config["csv_path"] = os.path.join(config["output_dir"], "performance.csv")
    if not os.path.exists(config["env_path"]):
        sys.exit("Unity build not found: " + config["env_path"])
    if not os.path.exists(config["training_config_path"]):
        sys.exit("Training config not found: " + config["training_config_path"])
    if config["seed_mode"] not in ["fixed", "increment", "random"]:
        sys.exit("seed_mode must be fixed, increment or random")
    if config["experiment_type"] not in run_record.EXPERIMENT_TYPES:
        sys.exit("experiment_type must be one of: " + ", ".join(run_record.EXPERIMENT_TYPES))
    if not isinstance(config["num_envs"], int) or config["num_envs"] < 1:
        sys.exit("num_envs must be a whole number of at least 1")
    for argument in config["extra_args"]:
        if argument.startswith("--num-envs"):
            sys.exit("Set num_envs in the config instead of --num-envs in extra_args")
    return config


def make_seeds(config):
    first_seed = config["seed"]
    if first_seed is None:
        first_seed = random.randint(0, MAX_SEED)
    seeds = []
    for i in range(config["total_runs"]):
        if config["seed_mode"] == "fixed":  # identical seeds measures system noise/variance
            seeds.append(first_seed)
        elif config["seed_mode"] == "increment":
            seeds.append(first_seed + i)
        else:
            seeds.append(random.randint(0, MAX_SEED))
    return seeds


def prepare_output(config):
    """Creates the folders and performance.csv, or checks an existing CSV's columns"""
    os.makedirs(config["work_dir"], exist_ok=True)
    if not os.path.exists(config["csv_path"]):
        with open(config["csv_path"], "w", newline="") as file:
            csv.writer(file).writerow(run_record.CSV_FIELDS)
        return
    with open(config["csv_path"]) as file:
        header = file.readline().strip().split(",")
    if header != run_record.CSV_FIELDS:
        sys.exit(config["csv_path"] + " has different columns; rename or move it first")


def open_database():
    """The local SQLite database, created from the latest schema when needed"""
    conn = local_store.get_db()
    local_store.init_db(conn)
    return conn


# One training run with recordings
class Run:
    """One training - trainer process, CPU/RAM/clock samples and reward summaries"""

    def __init__(self, run_id, seed, config, specs):
        self.run_id = run_id
        self.seed = seed
        self.config = config
        self.specs = specs
        self.cpu_samples = []  # trainer + Unity build(s), % of the allocated CPU
        self.background_samples = []  # everything else on the allocated cores, % of the allocated CPU
        self.p_core_samples = []  # average % of the P-cores (whole system)
        self.e_core_samples = []  # average % of the E-cores (whole system)
        self.clock_samples = []  # current CPU clock in GHz
        self.ram_samples = []  # trainer + Unity build(s), MB
        self.summaries = []  # one per summary line: step, elapsed, mean, std
        self.streak = 0  # summary lines in a row with mean reward >= threshold
        self.converged_at = None  # the summary where the streak was reached
        self.final_steps = None  # exact step count from ML-Agents' status file
        self.early_stopped = False
        self.interrupted = False
        self.output = []  # the trainer's output lines, saved for failed runs
        self.start_error = None  # set when the trainer could not be started at all
        self.training_started_at = None  # when Unity connected; sampling starts then
        self.counters_started = False  # the first sample after the start only starts the CPU counters
        self.process = None
        command = [
            sys.executable,
            ENTRY,
            config["training_config_path"],
            "--run-id=" + run_id,
            "--env=" + config["env_path"],
            "--results-dir=" + config["work_dir"],
            "--seed=" + str(seed),
            "--base-port=" + str(config["base_port"]),
            "--num-envs=" + str(config["num_envs"]),
        ]
        if config["no_graphics"]:
            command.append("--no-graphics")
        command.extend(config["extra_args"])
        environment = os.environ.copy()
        environment["PYTHONUNBUFFERED"] = "1"  # send output lines right away
        log(f"Starting {run_id} (seed {seed}, {config['num_envs']} env(s))")
        self.start_time = time.time()
        self.processes = {}  # trainer + Unity build(s)
        self.reader = None
        try:
            self.process = psutil.Popen(
                command,
                cwd=ROOT,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace",
                # own process group: the terminal's Ctrl+C doesn't reach it, stop() is used instead
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        except (OSError, psutil.Error) as error:
            self.start_error = str(error)
            self.output.append("Could not start the trainer: " + self.start_error + "\n")
            log(f"{run_id}: could not start the trainer: {self.start_error}")
            if blocked_by_windows(self.start_error):
                log(BLOCKED_HINT)
            return
        self.processes[self.process.pid] = self.process
        self.reader = threading.Thread(target=self.read_output, daemon=True)
        self.reader.start()

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def stop(self):
        """Asks mlagents-learn to save its model and exit (see mlagents_entry.py)"""
        try:
            if self.is_running():
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
        except OSError:  # it ended in the meantime
            pass

    def read_output(self):
        """Runs in its own thread: shows the trainer's output and reads its summary lines"""
        behavior = None  # only the first behavior's summaries are tracked
        for line in self.process.stdout:
            self.output.append(line)
            print(line, end="", flush=True)
            if self.training_started_at is None and TRAINING_STARTED in line:
                self.training_started_at = time.time()
            match = SUMMARY_LINE.search(line)
            if match is None:
                continue
            if behavior is None:
                behavior = match.group(1)
            if match.group(1) == behavior:
                step = int(match.group(2))
                elapsed = float(match.group(3))
                self.add_summary(step, elapsed, float(match.group(4)), float(match.group(5)))

    def add_summary(self, step, elapsed, mean, std):
        """Records a summary line and checks for convergence (and early stop)"""
        summary = {"step": step, "elapsed": elapsed, "mean": mean, "std": std}
        self.summaries.append(summary)
        early_stop = self.config["early_stop"]
        if self.converged_at is not None:
            return
        if mean >= early_stop["threshold"]:
            self.streak += 1
        else:
            self.streak = 0
        if self.streak < early_stop["consecutive"]:
            return
        self.converged_at = summary
        if early_stop["enabled"]:
            log(f"{self.run_id}: mean reward reached the threshold at step {step} - stopping early")
            self.early_stopped = True
            self.stop()

    def measure(self):
        """Adds one sample of CPU, RAM and clock (trainer + children, and the whole system).
        Nothing is sampled until training has started, so loading ML-Agents/Unity isn't counted."""
        if self.training_started_at is None:
            return
        try:
            for child in self.process.children(recursive=True):
                if child.pid not in self.processes:
                    child.cpu_percent()  # the first call only starts the CPU counter
                    self.processes[child.pid] = child
        except psutil.Error:
            pass
        if not self.counters_started:  # CPU % is measured between two calls: start the counters
            for process in self.processes.values():
                try:
                    process.cpu_percent()
                except psutil.Error:
                    pass
            psutil.cpu_percent(percpu=True)
            self.counters_started = True
            return
        cpu = 0.0  # in % of one core
        ram = 0
        for pid in self.processes:
            try:
                cpu += self.processes[pid].cpu_percent()
                ram += self.processes[pid].memory_info().rss
            except psutil.Error:  # the process has ended
                pass
        allocated = self.specs["allocated_cpus"]
        self.cpu_samples.append(cpu / allocated)
        self.ram_samples.append(ram / (1024 * 1024))

        per_core = psutil.cpu_percent(percpu=True)  # since the previous call, % per logical core
        allowed = [core for core in self.specs["allowed_cores"] if core < len(per_core)]
        system = sum(per_core[core] for core in allowed)
        self.background_samples.append(max(0.0, (system - cpu) / allocated))
        for ids, samples in [
            (self.specs["p_core_ids"], self.p_core_samples),
            (self.specs["e_core_ids"], self.e_core_samples),
        ]:
            ids = [core for core in ids if core < len(per_core)]
            if len(ids) > 0:
                samples.append(sum(per_core[core] for core in ids) / len(ids))
        try:
            freq = psutil.cpu_freq()
            if freq is not None and freq.current:
                self.clock_samples.append(freq.current / 1000)
        except (OSError, NotImplementedError):
            pass

    def read_final_steps(self):
        """The exact step count is in ML-Agents' status file (a bit past the last summary line)"""
        status_path = os.path.join(
            self.config["work_dir"], self.run_id, "run_logs", "training_status.json"
        )
        try:
            with open(status_path) as file:
                status = json.load(file)
            for behavior in status:
                if behavior != "metadata":
                    self.final_steps = status[behavior]["final_checkpoint"]["steps"]
                    break
        except (OSError, ValueError, KeyError, TypeError):  # no status file: keep the summary line's step
            pass

    # Write results
    def finish(self, conn, identity):
        """Stores the run in the database (finished runs only) and the CSV, then prints a summary"""
        duration = time.time() - self.start_time
        if self.reader is not None:
            self.reader.join(timeout=10)  # let it read the last output lines
        self.read_final_steps()
        exit_code = self.process.returncode if self.process is not None else None
        row = run_record.build_row(self, self.config, self.specs, identity, duration, exit_code)

        problem = None
        if self.start_error is not None:
            problem = "could not start: " + self.start_error
        elif exit_code != 0:
            problem = f"exit code {exit_code}"
        elif self.interrupted:
            problem = "interrupted"
        elif len(self.summaries) == 0:
            problem = "no reward summaries"
        if problem is None:
            problem = run_record.save_to_db(conn, row)
            if problem is not None:
                problem = "database error: " + problem
        row["saved_to_db"] = problem is None

        with open(self.config["csv_path"], "a", newline="") as file:
            csv.DictWriter(file, fieldnames=run_record.CSV_FIELDS).writerow(row)
        if problem is not None:
            run_dir = os.path.join(self.config["output_dir"], self.run_id)
            os.makedirs(run_dir, exist_ok=True)
            with open(os.path.join(run_dir, "train.log"), "w", encoding="utf-8") as file:
                file.writelines(self.output)
        shutil.rmtree(os.path.join(self.config["work_dir"], self.run_id), ignore_errors=True)

        stored = "saved to database" if problem is None else f"NOT saved to database ({problem})"
        if problem is not None and self.start_error is None and blocked_by_windows("".join(self.output)):
            log(f"{self.run_id}: {BLOCKED_HINT}")
        log(
            f"Finished {self.run_id}: {stored}, {row['duration_s']} s, "
            f"steps {row['total_steps_executed']}, mean reward {row['final_mean_reward']} "
            f"+/- {row['final_std_reward']}, CPU avg {row['ml_agents_avg_cpu_util']}%, "
            f"RAM avg {row['avg_ram_usage_mb']} MB"
        )

    def status(self):
        """One line about the running training, for the periodic status report."""
        text = f"    {self.run_id}: running {round(time.time() - self.start_time)} s"
        if len(self.summaries) > 0:
            last = self.summaries[-1]
            text += f", step {last['step']}, mean reward {last['mean']}"
        if len(self.cpu_samples) > 0:
            text += f", CPU {round(self.cpu_samples[-1], 1)}%, RAM {round(self.ram_samples[-1])} MB"
        return text


# Run the batch
def run_batch(config, specs, conn, identity):
    batch_id = time.strftime("%Y%m%d_%H%M%S")
    total = config["total_runs"]
    print(f"Batch {batch_id}: {total} run(s), one after another, experiment type {config['experiment_type']}")
    print("  operator: " + identity["name"] + " on " + identity["machine"])
    print("  hardware: " + hardware.describe(specs))
    print("  config:   " + config["config_path"])
    print("  training: " + config["training_config_path"])
    print("  database: " + str(local_store.DB_PATH))
    print("  backup:   " + config["csv_path"])
    print("Keep this terminal open until 'Done.' - press Ctrl+C once to stop safely.\n", flush=True)
    seeds = make_seeds(config)
    interrupted = False
    for index in range(total):
        if interrupted:
            break
        run_id = "run_" + batch_id + "_" + str(index + 1).zfill(3)
        run = Run(run_id, seeds[index], config, specs)
        last_status = time.time()
        while run.is_running():
            try:
                time.sleep(config["sample_interval_s"])
                if run.is_running():
                    run.measure()
                if time.time() - last_status >= STATUS_INTERVAL_S:
                    last_status = time.time()
                    log(f"Still running - {index} of {total} runs done:")
                    print(run.status(), flush=True)
            except KeyboardInterrupt:
                if not interrupted:
                    print("\nInterrupted - stopping the running training (it saves its model)...")
                interrupted = True
                run.interrupted = True
                run.stop()
        try:
            run.finish(conn, identity)
        except Exception:  # keep the batch going; the run's result is lost
            log(f"{run_id}: recording the result failed:")
            traceback.print_exc()
        if run.start_error is not None:  # the next runs would fail the same way
            log("Stopping the batch: the trainer could not be started.")
            break


def main():
    # Simple help screen for CLI usage
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="automation config (YAML)")
    parser.add_argument("--runs", type=int, help="override total_runs")
    args = parser.parse_args()
    sys.stdout.reconfigure(errors="replace")  # don't crash on characters the console can't show

    load_dotenv(os.path.join(ROOT, ".env"))
    try:
        identity = {"name": storage_scripts.get_name(), "machine": storage_scripts.get_machine_name()}
    except ValueError as error:
        sys.exit(str(error))
    config = load_config(args.config, args.runs)
    specs = hardware.detect(config.get("hardware"))
    prepare_output(config)
    conn = open_database()
    try:
        run_batch(config, specs, conn, identity)
    finally:
        conn.close()
    shutil.rmtree(config["work_dir"], ignore_errors=True)
    print("\nDone. Database: " + str(local_store.DB_PATH) + " | backup: " + config["csv_path"])
    print("Upload to Supabase with: python runner/sync_to_cloud.py")


if __name__ == "__main__":
    main()
