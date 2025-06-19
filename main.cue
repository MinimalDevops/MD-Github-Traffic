package dagger

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
	description: "Run linting with Ruff"
	output: base.withExec([
		["pip", "install", "-r", "requirements-dev.txt"],
		["ruff", "."]
	]).stdout
}
