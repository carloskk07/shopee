# Proteção da branch `main`

O ruleset **Protect main** está ativo e trata `main` como produção.

## Contrato efetivo

- Restrict deletions
- Block force pushes
- Require a pull request before merging
- Require status checks to pass: `validate`
- Require branch to be up to date before merge
- Require conversation resolution before merging
- Require linear history
- Allowed merge method: Squash
- Required approvals: 0
- Bypass: nenhum

## Release

Uma mudança editorial não termina no merge. O contrato completo é:

`branch -> PR -> validate -> squash/main -> Vercel -> Production smoke`

`release.json` é a autoridade criptográfica do conteúdo editorial publicado.
