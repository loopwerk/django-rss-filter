# How to contribute

> [!IMPORTANT]
> If you use LLM / "AI" tools for your contributions, please read and follow the [Generative AI / LLM Policy][llm]

## Workflow

First off, thank you for considering to contribute!

- Only contribute code that you fully understand. See also the [AI policy][llm].
- No contribution is too small! Please submit as many fixes for typos and grammar bloopers as you can!
- Before starting big contributions, talk to us first. Don't waste energy / tokens on something that we do not want. Rejecting a huge PR is unpleasant for everybody.
- Try to limit each pull request to one change only.
- Always add tests and docs for your code.
- Format the code with `ruff`: `uv run ruff format .` or `just format`.
- Keep PR descriptions and code comments short and to the point.

## Tests

Unit tests can be run with `uv run pytest` or `just test`.

[llm]: https://github.com/loopwerk/.github/blob/main/AI_POLICY.md
