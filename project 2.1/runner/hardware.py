"""Detects the machine's hardware specs and the CPU/RAM the trainings are allowed to use.

"Total" values describe the machine. "Allocated" values describe what the runs get: the cores
this process may run on (CPU affinity / docker --cpuset-cpus) and, inside a container, the
docker --cpus and --memory limits. Values from the config's 'hardware' section win over detection.
"""

import os
import platform
import subprocess

import psutil

CGROUP_DIR = "/sys/fs/cgroup"  # cgroup v2: inside a container these files hold its limits

# SMBIOS memory type numbers (Win32_PhysicalMemory.SMBIOSMemoryType)
RAM_TYPES = {
    20: "DDR",
    21: "DDR2",
    24: "DDR3",
    26: "DDR4",
    27: "LPDDR",
    28: "LPDDR2",
    29: "LPDDR3",
    30: "LPDDR4",
    34: "DDR5",
    35: "LPDDR5",
}


def read_cpu_model():
    system = platform.system()
    if system == "Windows":
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
            )
            return winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        except OSError:
            pass
    elif system == "Linux":
        try:
            with open("/proc/cpuinfo") as file:
                for line in file:
                    if line.startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            pass
    return platform.processor() or "unknown"


def read_max_ghz():
    """The max clock the system reports (on Windows this is often the base clock)"""
    try:
        freq = psutil.cpu_freq()
    except (OSError, NotImplementedError):
        freq = None
    if freq is None:
        return 0.0
    return round((freq.max or freq.current) / 1000, 2)


def read_ram_windows():
    """RAM speed (MHz) and type of the first memory module, via PowerShell (Windows only)"""
    if platform.system() != "Windows":
        return None, None
    command = (
        "Get-CimInstance Win32_PhysicalMemory | Select-Object -First 1 | "
        "ForEach-Object { \"$($_.ConfiguredClockSpeed),$($_.Speed),$($_.SMBIOSMemoryType)\" }"
    )
    try:
        output = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.strip()
        configured, rated, memory_type = output.split(",")
    except (OSError, ValueError, subprocess.SubprocessError):
        return None, None
    speed = None
    for value in [configured, rated]:  # the speed it runs at, else the rated speed
        if value.isdigit() and int(value) > 0:
            speed = int(value)
            break
    ram_type = None
    if memory_type.isdigit():
        ram_type = RAM_TYPES.get(int(memory_type))
    return speed, ram_type


def read_cgroup(name):
    try:
        with open(os.path.join(CGROUP_DIR, name)) as file:
            return file.read().strip()
    except OSError:
        return None


def read_container_cpu_limit():
    """docker --cpus as a number of cores, or None when there is no limit"""
    value = read_cgroup("cpu.max")  # e.g. "200000 100000" (= 2 cores) or "max 100000"
    if value is None:
        return None
    parts = value.split()
    if len(parts) != 2 or parts[0] == "max":
        return None
    return int(parts[0]) / int(parts[1])


def read_container_ram_limit_mb():
    """docker --memory in MB, or None when there is no limit"""
    value = read_cgroup("memory.max")  # bytes or "max"
    if value is None or not value.isdigit():
        return None
    return round(int(value) / (1024 * 1024))


def read_allowed_cores():
    """The logical cores this process (and so the trainings) may run on"""
    try:
        return sorted(psutil.Process().cpu_affinity())
    except (AttributeError, psutil.Error):  # cpu_affinity doesn't exist on macOS
        return list(range(psutil.cpu_count(logical=True) or 1))


def detect(overrides):
    """Returns the hardware columns of RunData plus what the sampling needs:
    allowed_cores, allocated_cpus (what 100% CPU means), p_core_ids, e_core_ids"""
    overrides = overrides or {}
    logical_total = psutil.cpu_count(logical=True) or 1
    allowed = read_allowed_cores()
    allocated_cpus = float(len(allowed))
    cpu_limit = read_container_cpu_limit()
    if cpu_limit is not None:
        allocated_cpus = min(allocated_cpus, cpu_limit)

    p_ids = overrides.get("p_cores")
    e_ids = overrides.get("e_cores")
    if p_ids is None and e_ids is None:  # unknown split: every core counts as a P-core
        p_ids = list(allowed)
        e_ids = []
    p_ids = [core for core in (p_ids or []) if core in allowed]
    e_ids = [core for core in (e_ids or []) if core in allowed]

    max_ghz = read_max_ghz()
    p_max_ghz = overrides.get("p_core_max_ghz")
    if p_max_ghz is None:
        p_max_ghz = max_ghz
    e_max_ghz = overrides.get("e_core_max_ghz")
    if e_max_ghz is None:
        e_max_ghz = 0.0
    if len(e_ids) == 0:
        e_max_ghz = 0.0

    ram_total_mb = round(psutil.virtual_memory().total / (1024 * 1024))
    ram_limit_mb = read_container_ram_limit_mb()
    if ram_limit_mb is None or ram_limit_mb > ram_total_mb:
        ram_limit_mb = ram_total_mb

    ram_speed = overrides.get("ram_speed_mhz")
    ram_type = overrides.get("ram_type")
    if ram_speed is None or ram_type is None:
        detected_speed, detected_type = read_ram_windows()
        if ram_speed is None:
            ram_speed = detected_speed
        if ram_type is None:
            ram_type = detected_type

    return {
        "os_name": platform.system(),
        "cpu_model": read_cpu_model(),
        "cpu_physical_cores_total": psutil.cpu_count(logical=False) or logical_total,
        "cpu_logical_cores_total": logical_total,
        "cpu_p_cores_allocated": len(p_ids),  # logical cores (threads)
        "cpu_e_cores_allocated": len(e_ids),
        "cpu_p_core_max_ghz": float(p_max_ghz),
        "cpu_e_core_max_ghz": float(e_max_ghz),
        "ram_total_mb": ram_total_mb,
        "ram_allocated_limit_mb": ram_limit_mb,
        "ram_speed_mhz": ram_speed if ram_speed is not None else 0,
        "ram_type": ram_type if ram_type is not None else "unknown",
        # for the sampling, not stored
        "allowed_cores": allowed,
        "allocated_cpus": allocated_cpus,
        "p_core_ids": p_ids,
        "e_core_ids": e_ids,
    }


def describe(specs):
    """One line for the batch header"""
    text = (
        f"{specs['cpu_model']} | {specs['cpu_physical_cores_total']} cores / "
        f"{specs['cpu_logical_cores_total']} threads, {round(specs['allocated_cpus'], 2)} allocated "
        f"(P {specs['cpu_p_cores_allocated']}, E {specs['cpu_e_cores_allocated']}) | "
        f"RAM {specs['ram_total_mb']} MB (limit {specs['ram_allocated_limit_mb']} MB), "
        f"{specs['ram_type']} {specs['ram_speed_mhz']} MHz"
    )
    return text
