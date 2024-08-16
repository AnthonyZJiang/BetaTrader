run_windows() {
    echo "Running on Windows"
    cd .venv/Scripts
    activate
    cd ../../
    python sim.py
}

run_macos() {
    echo "Running on macOS"
    source .venv/bin/activate
    python sim.py
}

if [[ $OSTYPE == "darwin"* ]]; then
    run_macos
elif [[ $OSTYPE == "msys" ]]; then
    run_windows
fi