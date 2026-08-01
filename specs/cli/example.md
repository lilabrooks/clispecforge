---
status: current
owner: product
deciders: [Lila Brooks]
---
# Greeting CLI

## Purpose
Print a greeting for one required name.

## Commands
- `greet NAME`

## Inputs
- `NAME`: required positional argument.

## Outputs
- Prints `Hello, NAME`.
- Returns exit code `0`.

## Behavior
The command should preserve the exact name passed by the user.

## Acceptance tests
- Given `greet Lila`, stdout is `Hello, Lila`.
- Given `greet "Python CLI"`, stdout is `Hello, Python CLI`.
- Given no name, the command returns parser exit code `2`.
