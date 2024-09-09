run_windows() {
    echo "Running on Windows"
    cd .venv/Scripts
    activate
    cd ../../
    python sim.py $1
}

run_macos() {
    echo "Running on macOS"
    source .venv/bin/activate
    python sim.py $1
}

if [[ $OSTYPE == "darwin"* ]]; then
    run_macos $1
elif [[ $OSTYPE == "msys" ]]; then
    run_windows $1
fi