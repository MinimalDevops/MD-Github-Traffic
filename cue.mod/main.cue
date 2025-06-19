package github_traffic_monitor

import (
	"dagger.io/dagger"
)

base: dagger.#Container & {
	from: "python:3.11-slim"
	workdir: "/src"
	withMountedDirectory: "/src": dagger.#FS & {
		source: dagger.#Local & {
			path: "./"
		}
	}
}

lint: dagger.#Function & {
	description: "Run Ruff linter"
	output: base.withExec([
		["pip", "install", "-r", "requirements-dev.txt"],
		["ruff", "."]
	]).stdout
}

test: dagger.#Function & {
	description: "Run Pytest"
	output: base.withExec([
		["pip", "install", "-r", "requirements-dev.txt"],
		["pytest"]
	]).stdout
}
