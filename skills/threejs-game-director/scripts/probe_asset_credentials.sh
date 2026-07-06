#!/usr/bin/env bash
# Report SET/MISSING for optional asset-generation API keys without printing values.
# Checks the current environment plus the user's zsh AND bash login profiles, so a
# key exported in ~/.bash_profile is found even when zsh is installed, and vice
# versa. Note: keys exported only in the current interactive session (not in a
# profile) may read MISSING here.
#
# ALPHA3D_API_KEY is only needed for the API-key path of the 3D/image generators.
# The Alpha3D MCP connector authenticates over OAuth and needs no env var, so a
# MISSING ALPHA3D_API_KEY does NOT block the MCP path.
set -uo pipefail

check_key() {
  local name="$1"
  # 1. Already exported in the current environment.
  if [ -n "${!name:-}" ]; then
    echo SET
    return
  fi
  # 2. zsh login profiles.
  if command -v zsh >/dev/null 2>&1; then
    if zsh -lc "source \"\$HOME/.zprofile\" >/dev/null 2>&1; source \"\$HOME/.zshrc\" >/dev/null 2>&1; [ -n \"\${$name:-}\" ]" >/dev/null 2>&1; then
      echo SET
      return
    fi
  fi
  # 3. bash login profiles.
  if command -v bash >/dev/null 2>&1; then
    if bash -lc "source \"\$HOME/.bash_profile\" >/dev/null 2>&1; source \"\$HOME/.bashrc\" >/dev/null 2>&1; [ -n \"\${$name:-}\" ]" >/dev/null 2>&1; then
      echo SET
      return
    fi
  fi
  echo MISSING
}

for key in ALPHA3D_API_KEY GEMINI_API_KEY ELEVENLABS_API_KEY; do
  printf "%s=%s\n" "$key" "$(check_key "$key")"
done
