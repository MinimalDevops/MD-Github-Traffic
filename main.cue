// main.cue
package dagger

import (
	"dagger.io/dagger"
)

// Base container
base: dagger.#Container & {
	from: "python:3.11-slim"
	workdir: "/src"
	withMountedDirectory: "/src": dagger.#FS & {
		source: dagger.#Local & {
			path: "./"
		}
	}
}

// Lint function (top-level, callable)
lint: dagger.#Function & {
	description: "Run linting with Ruff"
	output: base.withExec([
		["pip", "install", "-r", "requirements-dev.txt"],
		["ruff", "."]
	]).stdout
}

// Test function (top-level, callable)
test: dagger.#Function & {
	description: "Run tests with Pytest"
	output: base.withExec([
		["pip", "install", "-r", "requirements-dev.txt"],
		["pytest"]
	]).stdout
}
