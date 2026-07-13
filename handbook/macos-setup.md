# macOS Setup — for Hardware Engineers on Mac

**PCB Flow runs on macOS.** The main [handbook](README.md) instructions apply unchanged; this
page covers the few Mac specifics. (Linux users can follow the handbook directly.)

## The essentials

1. **`python3` works as-is.** macOS ships or brews Python 3; the docs' `python3 tools/doctor.py`
   commands run unchanged. If `python3` is missing: `brew install python`.
2. **The `.sh` helpers work** (unlike Windows). `automation/kicad/drc.sh` and the Chrome launch
   recipe run in Terminal.
3. **Install tools with Homebrew** (recommended):
   ```bash
   brew install --cask visual-studio-code google-chrome kicad
   brew install python git node
   ```
   EasyEDA Pro: download the macOS app from <https://pro.easyeda.com> (or use it in Chrome).

## Verify your environment

```bash
python3 tools/doctor.py     # lists each tool with ✅ / ⚠️ / ❌ and how to fix gaps
```

## Chrome / EasyEDA automation on Mac

The AI reads your live EasyEDA board through Chrome. Two options (same as Linux):

- **Recommended — the EasyEDA Bridge:** install the **`run-api-gateway`** extension in EasyEDA
  Pro, tick *"allow external interaction"*, and run the bridge server. See
  [`automation/easyeda/README.md`](../automation/easyeda/README.md). No profile juggling.
- **Fallback — raw Chrome DevTools:** `python3 tools/launch_easyeda.py` launches Chrome with
  remote debugging. Keep one EasyEDA window open and signed in.

## Notes

- macOS may block first-run of `kicad` / Chrome — approve them in **System Settings ▸ Privacy
  & Security**.
- Everything else — the 12 phases, the AI workflow, the checkpoints — is identical to the
  handbook. Continue at [`04 · Your first project`](04-your-first-project.md).

> Platform status: PCB Flow is developed and validated on Linux; the macOS/Windows tooling is
> built and unit-tested but still benefits from real-world validation — please file issues.
