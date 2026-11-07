"""Starts mlagents-learn so the runner can stop it cleanly.

Each training runs in its own process group, so it doesn't get the terminal's Ctrl+C.
The runner sends CTRL_BREAK (SIGBREAK) instead; this turns it into a KeyboardInterrupt,
which ML-Agents handles by saving the model and exiting.
"""

import signal

from mlagents.trainers.learn import main


def _stop(signum, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGBREAK, _stop)

if __name__ == "__main__":
    main()
