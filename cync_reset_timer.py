"""Terminal stoplight timer for power-cycling (factory resetting) Cync / C by GE lights.

Green = switch ON, red = switch OFF, yellow = get ready to switch.
Sequences come from Cync's support article "Factory Reset Smart Light Bulbs":
https://cyncsupport.gelighting.com/s/article/resetting-light-bulbs
"""

from __future__ import annotations

import math
import os
import sys
import time


Step = tuple[str, int]

# Each sequence ends with a final "turn ON and leave it", added in run_reset().
SEQUENCES: dict[str, dict] = {
    "1": {
        "name": "Standard (latest firmware)",
        "about": "Most Cync bulbs incl. Reveal & Deco. ON 1s / OFF 1s, x5. Try first.",
        "steps": [("OFF", 3)] + [("ON", 1), ("OFF", 1)] * 5,
        "confirm": "The bulb flashes when the reset worked.",
    },
    "2": {
        "name": "Alternate 1 (firmware 2.8+)",
        "about": "Older bulbs & pre-2020 light strips. ON 8s / OFF 2s, x5.",
        "steps": [("OFF", 5)] + [("ON", 8), ("OFF", 2)] * 5,
        "confirm": "The bulb flashes on and off 3 times when the reset worked.",
    },
    "3": {
        "name": "Alternate 2 (firmware 2.7 and earlier)",
        "about": "Legacy C by GE bulbs. Mixed 8s and 2s rhythm.",
        "steps": [("OFF", 5), ("ON", 8)]
        + [("OFF", 2), ("ON", 2)] * 3
        + [("OFF", 2), ("ON", 8)] * 2
        + [("OFF", 2)],
        "confirm": "The bulb flashes on and off 3 times when the reset worked.",
    },
    "4": {
        "name": "Wafer downlight",
        "about": "Flip the switch 5 times. Cync gives no timing, so this uses 1s.",
        "steps": [("OFF", 3)] + [("ON", 1), ("OFF", 1)] * 5,
        "confirm": "The light blinks when the reset worked.",
    },
}

WARN_SECONDS = 1.5  # show "GET READY" this long before each switch
WIDTH = 44

IS_TTY = sys.stdout.isatty()
USE_COLOR = IS_TTY and "NO_COLOR" not in os.environ

# ANSI style codes: (background block style, foreground-only style)
STYLES = {
    "ON": ("1;30;102", "1;92"),  # black on bright green / green text
    "OFF": ("1;97;41", "1;91"),  # white on red / red text
}
WARN = "1;30;103"  # black on bright yellow
DIM = "2"
BOLD = "1"

BIG_DIGITS = {
    "0": ["###", "# #", "# #", "# #", "###"],
    "1": [" # ", "## ", " # ", " # ", "###"],
    "2": ["###", "  #", "###", "#  ", "###"],
    "3": ["###", "  #", "###", "  #", "###"],
    "4": ["# #", "# #", "###", "  #", "  #"],
    "5": ["###", "#  ", "###", "  #", "###"],
    "6": ["###", "#  ", "###", "# #", "###"],
    "7": ["###", "  #", "  #", "  #", "  #"],
    "8": ["###", "# #", "###", "# #", "###"],
    "9": ["###", "# #", "###", "  #", "###"],
}


def style(text: str, codes: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{codes}m{text}\033[0m"


def bell() -> None:
    if IS_TTY:
        print("\a", end="", flush=True)


def draw(lines: list[str]) -> None:
    """Redraw the screen in place without flicker."""
    if IS_TTY:
        out = "\033[H" + "".join(f"{line}\033[K\n" for line in lines) + "\033[J"
    else:
        out = "\n".join(lines) + "\n"
    print(out, end="", flush=True)


def banner(text: str, codes: str) -> list[str]:
    pad = " " * WIDTH
    return [style(pad, codes), style(text.center(WIDTH), codes), style(pad, codes)]


def big_number(value: int, codes: str) -> list[str]:
    rows = []
    for row in range(5):
        glyphs = (BIG_DIGITS[d][row] for d in str(value))
        line = "  ".join(glyphs).replace("#", "██").replace(" ", "  ")
        rows.append(style(line.center(WIDTH).rstrip(), codes))
    return rows


def timeline(steps: list[tuple[str, int | None]], current: int) -> list[str]:
    """One colored chip per step; finished steps fade, current one is marked."""
    chips = []
    for i, (state, seconds) in enumerate(steps):
        label = "ON" if seconds is None else str(seconds)
        chip = f"{label:^3}"
        if i < current:
            chips.append(style(chip, DIM))
        else:
            chips.append(style(chip, STYLES[state][0]))
    pointer = " " * (current * 4) + " ▲"
    return [" ".join(chips), style(pointer, BOLD)]


def legend() -> str:
    return "  ".join(
        [
            style(" ON ", STYLES["ON"][0]) + " = switch on",
            style(" OFF ", STYLES["OFF"][0]) + " = switch off",
            style(" READY ", WARN) + " = switch soon",
        ]
    )


def header(name: str) -> list[str]:
    return [style("CYNC BULB RESET", BOLD) + "  " + style(name, DIM), ""]


def run_step(name: str, steps: list[tuple[str, int | None]], index: int) -> None:
    state, seconds = steps[index]
    assert seconds is not None
    block, text = STYLES[state]
    next_state, next_seconds = steps[index + 1]
    next_text = f"TURN {next_state}" + (
        f" for {next_seconds}s" if next_seconds else " and leave it"
    )
    # 1-second steps are too short for a warning; the beep carries them.
    warn_for = min(WARN_SECONDS, seconds / 2) if seconds >= 2 else 0

    bell()
    ends = time.monotonic() + seconds
    while (remaining := ends - time.monotonic()) > 0:
        filled = int(WIDTH * (seconds - remaining) / seconds)
        bar = style("█" * filled, text) + style("░" * (WIDTH - filled), DIM)

        if remaining <= warn_for:
            upcoming = style(f" GET READY → {next_text} ".center(WIDTH), WARN)
        else:
            upcoming = style(f"Next: {next_text}", DIM)

        draw(
            header(name)
            + banner(f"TURN {state}", block)
            + [""]
            + big_number(math.ceil(remaining), text)
            + ["", bar, "", upcoming, ""]
            + [style(f"Step {index + 1} of {len(steps)}", BOLD)]
            + timeline(steps, index)
            + ["", style("Ctrl+C to stop", DIM)]
        )
        time.sleep(min(0.05, remaining))


def run_reset(sequence: dict) -> bool:
    name = sequence["name"]
    steps: list[tuple[str, int | None]] = [*sequence["steps"], ("ON", None)]

    if IS_TTY:
        print("\033[2J", end="")
    draw(
        header(name)
        + [style("The whole sequence (seconds per step):", BOLD), ""]
        + timeline(steps, 0)[:1]
        + ["", legend(), ""]
        + [
            "1. Stand at a plain on/off switch (no dimmers or 3-way lamps).",
            "2. Turn the bulb " + style(" OFF ", STYLES["OFF"][0]) + " now.",
            "3. Press Enter. The timer then runs on its own,",
            "   so don't press anything else.",
            "4. Match the switch to the big color block.",
            "   It beeps at every change, and a "
            + style(" GET READY ", WARN)
            + " warning",
            "   appears just before longer steps end.",
        ]
    )
    input("\nBulb OFF? Press Enter to start... ")

    if IS_TTY:
        print("\033[?25l\033[2J", end="")  # hide cursor
    try:
        for index in range(len(steps) - 1):
            run_step(name, steps, index)
    finally:
        if IS_TTY:
            print("\033[?25h", end="")  # show cursor

    bell()
    block, text = STYLES["ON"]
    draw(
        header(name)
        + banner("TURN ON AND LEAVE IT ON", block)
        + ["", style("Sequence complete.", text), ""]
        + ["Watch the bulb. " + sequence["confirm"]]
        + ["", style(f"Step {len(steps)} of {len(steps)}", BOLD)]
        + timeline(steps, len(steps) - 1)
    )
    answer = input("\nDid it flash? [y/n] ").strip().lower()
    return answer.startswith("y")


def main() -> None:
    hint = ""
    while True:
        if IS_TTY:
            print("\033[2J\033[H", end="")
        print(style("CYNC / C BY GE RESET TIMER", BOLD))
        print()
        print("Choose a reset sequence:")
        for key, sequence in SEQUENCES.items():
            print(f"  {style(key, STYLES['ON'][1])}. {sequence['name']}")
            print(f"     {style(sequence['about'], DIM)}")
        print(f"  {style('q', DIM)}. Quit")
        if hint:
            print("\n" + style(hint, "1;93"))
        choice = input(f"\nEnter 1-{len(SEQUENCES)} or q: ").strip().lower()

        if choice == "q":
            return
        if choice not in SEQUENCES:
            hint = f"Please choose 1-{len(SEQUENCES)} or q."
            continue

        if run_reset(SEQUENCES[choice]):
            print(style("\nReset successful! Set the bulb up again in the Cync app.", STYLES["ON"][1]))
            return
        next_key = str(int(choice) + 1)
        if choice in ("1", "2"):
            hint = f"No flash? Try option {next_key} next."
        else:
            hint = "No flash? Try another fixture, or update firmware in the Cync app."


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if IS_TTY:
            print("\033[?25h", end="")
        print("\nReset sequence stopped.")
