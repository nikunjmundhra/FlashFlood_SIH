#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Opening PravahAI Dashboard in your default browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
  open "$DIR/dashboard/pravahai_dashboard.html"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  xdg-open "$DIR/dashboard/pravahai_dashboard.html"
else
  start "$DIR/dashboard/pravahai_dashboard.html"
fi
