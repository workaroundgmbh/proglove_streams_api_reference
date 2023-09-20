#!/usr/bin/env bash

# Retrieve script folder
SCRIPT_FOLDER=$(cd "$(dirname "$0")" && pwd)
SCRIPT_DESCRIPTION="Install Python dependencies"

source "${SCRIPT_FOLDER}/include/common.sh"

main() {
	echo_level_1 "Install Python dependencies"

	echo_level_2 "Update core packages"
	pip3 install -U pip wheel setuptools >/dev/null

	local -r packages=(
		'poetry==1.6.1'
	)

	echo_level_2 "Install ${packages[*]}"
	pip3 install "${packages[@]}" >/dev/null

	echo "Install Poetry dependencies"
	poetry install --no-root --no-ansi
}

trap 'atexit' EXIT

main
