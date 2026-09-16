#!/bin/zsh
# Open the defence deck in LibreOffice Impress with IBM Plex fonts.
# Homebrew LibreOffice ignores ~/Library/Fonts unless FONTCONFIG_FILE points at a
# config that lists it (~/.config/fontconfig/fonts.conf).
DECK="$(cd "$(dirname "$0")/../.." && pwd)/iut_submissions/presentation/Defence/SWE_Orthogonal Defect Classification on Defects4JUsing an LLM-Driven Scientific Approach_Defence_Presentation.pptx"
pkill -f soffice 2>/dev/null
FONTCONFIG_FILE="$HOME/.config/fontconfig/fonts.conf" /Applications/LibreOffice.app/Contents/MacOS/soffice --impress "$DECK" >/dev/null 2>&1 &
