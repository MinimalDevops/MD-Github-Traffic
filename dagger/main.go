package main

import (
  "context"
  "dagger.io/dagger"
)

type Module struct{}  // your module’s root type

// Lint runs Ruff in a container.
func (m *Module) Lint(ctx context.Context) (string, error) {
  c, err := dagger.Connect(ctx)
  if err != nil {
    return "", err
  }
  defer c.Close()

  src := c.Host().Directory(".")
  out, err := c.Container().
    From("python:3.11-slim").
    WithMountedDirectory("/src", src).
    WithWorkdir("/src").
    WithExec([]string{"pip", "install", "-r", "requirements-dev.txt"}).
    WithExec([]string{"ruff", "."}).
    Stdout(ctx)
  return out, err
}

// Test runs Pytest in a container.
func (m *Module) Test(ctx context.Context) (string, error) {
  c, err := dagger.Connect(ctx)
  if err != nil {
    return "", err
  }
  defer c.Close()

  src := c.Host().Directory(".")
  out, err := c.Container().
    From("python:3.11-slim").
    WithMountedDirectory("/src", src).
    WithWorkdir("/src").
    WithExec([]string{"pip", "install", "-r", "requirements-dev.txt"}).
    WithExec([]string{"pytest"}).
    Stdout(ctx)
  return out, err
}