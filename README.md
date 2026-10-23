# Cync Reset Stoplight 🚦

**How to factory reset a Cync / C by GE smart bulb**, with a free stoplight-style timer that tells you exactly when to flip the light switch. Covers the standard Cync reset and the older firmware sequences.

**▶ Use it in your browser: https://kenthorburn.github.io/cync-reset-stoplight/**

| Color | Meaning |
| --- | --- |
| 🟢 Green | Switch **ON** |
| 🔴 Red | Switch **OFF** |
| 🟡 Yellow | Get ready, a change is coming |

Resetting these bulbs means flipping a switch in an exact rhythm, like "ON 8 seconds, OFF 2 seconds", over and over. Counting Mississippis while staring at a wall switch is error-prone. This tool shows a big color, counts down each step, and beeps (or says "on" / "off") at every change. You just follow the color.

## Reset sequences

From Cync's support article [Factory Reset Smart Light Bulbs](https://cyncsupport.gelighting.com/s/article/resetting-light-bulbs). If you don't know your bulb's firmware, start at the top and work down.

| Sequence | For | Steps | Success signal |
| --- | --- | --- | --- |
| **Standard** | Most Cync bulbs on current firmware, including Reveal and Deco | Start OFF. ON 1s, OFF 1s, ×5 | Bulb flashes |
| **Alternate 1** | Older bulbs (firmware 2.8+), light strips made before 2020 | OFF 5s. ON 8s, OFF 2s, ×5. Then ON | Flashes 3 times |
| **Alternate 2** | Legacy C by GE bulbs (firmware 2.7 and earlier) | OFF 5s, ON 8s. OFF 2s, ON 2s, ×3. OFF 2s, ON 8s, ×2. OFF 2s, then ON | Flashes 3 times |
| **Wafer downlight** | Cync wafer downlights | Flip ON/OFF 5 times or until it blinks (no timing given, so the timer uses 1s) | Light blinks |

Tips:

- Use a **plain on/off switch**. Dimmers, 3-way lamps and multi-function switches won't work. A power strip with a switch works too.
- No flash? Try another fixture, then the next sequence down, then update firmware in the Cync app (**Settings → Firmware Updates**).
- If the bulb is still in your Cync app, deleting it there also factory resets it.

Devices with a reset button, such as newer light strips (hold about 10s), switches and the C-Reach bridge, are listed on the website's reference section.

## Terminal version

The same timer runs in a terminal with color blocks, large digits and a bell at every change. It needs Python 3.9+ and has no dependencies.

```sh
python3 cync_reset_timer.py
```

## Project layout

```
docs/index.html        The website (one static file, served by GitHub Pages)
docs/llms.txt          Plain-text version of the guide for AI assistants
docs/sitemap.xml       Sitemap for search engines
docs/og-image.png      Preview image for link shares
cync_reset_timer.py    Terminal version
```

The sequence data lives in both code files. `docs/index.html` also repeats it as static text (the reference table, the FAQ and the JSON-LD in `<head>`), and so do `docs/llms.txt` and this README. If you change a sequence, update all of them.

To run the site locally, open `docs/index.html` in a browser. No build step.

## Disclaimer

An unofficial community tool. It is not affiliated with or endorsed by GE, GE Lighting, Savant or Cync. Product names are trademarks of their owners. Reset steps can change with firmware, so check the official support page if something doesn't match.

## License

[MIT](LICENSE)
