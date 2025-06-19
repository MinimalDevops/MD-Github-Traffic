// main.cue
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

lint: base & {
	withExec: [
		["pip", "install", "-r", "requirements-dev.txt"],
		["ruff", "."]
	]
}

test: base & {
	withExec: [
		["pip", "install", "-r", "requirements-dev.txt"],
		["pytest"]
	]
}

dagger.#Plan & {
	pipeline: {
		lint: lint
		test: test
	}
}
