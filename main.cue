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

lintContainer: base & {
	withExec: [
		["pip", "install", "-r", "requirements-dev.txt"],
		["ruff", "."]
	]
}

testContainer: base & {
	withExec: [
		["pip", "install", "-r", "requirements-dev.txt"],
		["pytest"]
	]
}

lint: dagger.#Function & {
	description: "Run linting using ruff"
	output: lintContainer.stdout
}

test: dagger.#Function & {
	description: "Run tests using pytest"
	output: testContainer.stdout
}
