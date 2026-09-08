# Proteção da branch `main`

A infraestrutura local do repositório está preparada para proteção obrigatória da `main`.

## Ruleset recomendado

Target: `main`

Regras:

- Restrict deletions
- Block force pushes
- Require a pull request before merging
- Require status checks to pass
  - `Site integrity / validate`
- Require conversation resolution before merging

## Observação

`CODEOWNERS`, o template de Pull Request e o workflow `Site integrity` já estão versionados. A ativação do ruleset depende de permissão administrativa do repositório no GitHub.
