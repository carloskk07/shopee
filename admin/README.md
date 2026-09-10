# Freedom Control Center V2

Console operacional privado-em-escrita e público-em-shell para a Freedom Book, entregue em `/admin/` sem alterar o hosting editorial em GitHub Pages.

## Princípios

- **PR only:** nenhuma escrita direta em `main`.
- **Credencial efêmera:** token GitHub somente na memória da aba; nunca é persistido.
- **Policy as code:** `control-plane.json` define escopo, caminhos bloqueados, budgets, thresholds SEO e experimentos ativos.
- **Evidence first:** Search Console é importado localmente; atual e baseline podem ser comparados antes de sugerir ação.
- **Causalidade:** experimentos registram início, data mínima de decisão, alvos e regra de promoção.
- **Release truth:** arquivos editoriais alterados recebem SHA-256 atualizado em `release.json` automaticamente no Change Set publicado.
- **Defense in depth:** Admin Integrity + Admin Production Smoke + CI público existente.

## Módulos V2

1. **Comando** — quality score, release parity, pipelines e fila de decisão por risco/ROI.
2. **Conteúdo** — inventário de livros/guias, anomalias e editor contextual.
3. **SEO Intelligence** — GSC atual/baseline, tendências, CTR opportunity, striking distance, canibalização e PDF × HTML.
4. **Experimentos** — janela temporal e de dados para decisões com atribuição limpa.
5. **Monetização** — estado, toggles guardados e edição avançada de `monetization.json`.
6. **Deploy & Releases** — PRs, runs, hashes e produção.
7. **Qualidade** — score ponderado por gates e diagnóstico exportável.
8. **Editor seguro** — allowlist de extensões, bloqueio de workflows/admin/release e validação local.
9. **Change Set** — staging recuperável na sessão, diff, backup, risco e preflight.
10. **Command palette** — `Ctrl/Cmd + K` para ações frequentes.

## Limite deliberado

O shell continua em GitHub Pages e portanto a URL `/admin/` não é uma fronteira de autenticação server-side. Ela é `noindex,nofollow,noarchive,nosnippet`, sem trackers e sem segredos. Escrita exige GitHub autenticado. A próxima camada correta é um backend privado para OAuth 2.0 do Search Console e autenticação server-side, sem migrar o site editorial.
