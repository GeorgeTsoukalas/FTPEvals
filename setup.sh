#!/bin/bash

# Install dependencies
echo "===> Installing dependencies <==="
pip install -r requirements.txt
echo "===> Dependencies installed successfully <==="

echo "===> Installing Lean <==="
# Install Lean if not already installed
export LEAN_VERSION="4.15.0"
install-lean-repl
echo "===> Lean installed successfully <==="

echo "===> Installing ITP <==="
# Install itp-interface
install-itp-interface
echo "===> ITP installed successfully <==="

echo "==> Cloning submodules <==="
# Clone the submodules
git submodule update --init --recursive
echo "==> Submodules cloned successfully <==="

echo "==> Generating Putnam solutions <==="
python data/putnambench/lean4/scripts/rewrite_solutions.py
echo "==> Putnam solutions generated successfully <==="
pushd data/putnambench/lean4
echo "==> Setting up lake cache <==="
lake exe cache get
echo "==> Cache setup successfully <==="
echo "==> Building Putnam with solutions <==="
lake build putnam_with_solutions
echo "==> Built Putnam with solutions successfully <==="
popd
