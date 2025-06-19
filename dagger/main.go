package main

import (
  "context"

  "dagger.io/dagger"
)

type Module struct{}

// Lint runs Ruff in a container.
func (m *Module) Lint(ctx context.Context) (string, error) {
  c, err := dagger.Connect(ctx, dagger.WithLogOutput(nil))
  if err != nil {
    return "", err
  }
  defer c.Close()

  src := c.Host().Directory(".")
  out, err := c.Container().
    From("python:3.11-slim").
    WithWorkdir("/src").
    WithMountedDirectory("/src", src).
    WithExec([]string{"pip", "install", "-r", "requirements-dev.txt"}).
    WithExec([]string{"ruff", "."}).
    Stdout(ctx)
  return out, err
}

// Test runs Pytest in a container.
func (m *Module) Test(ctx context.Context) (string, error) {
  c, err := dagger.Connect(ctx, dagger.WithLogOutput(nil))
  if err != nil {
    return "", err
  }
  defer c.Close()

  src := c.Host().Directory(".")
  out, err := c.Container().
    From("python:3.11-slim").
    WithWorkdir("/src").
    WithMountedDirectory("/src", src).
    WithExec([]string{"pip", "install", "-r", "requirements-dev.txt"}).
    WithExec([]string{"pytest"}).
    Stdout(ctx)
  return out, err
}
