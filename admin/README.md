# Freedom Control Center V2

Console operacional privado da Freedom Book. O site editorial continua em GitHub Pages, enquanto o Control Center é entregue separadamente pelo Netlify em `freedom-book-admin.netlify.app/admin/` com Team SSO obrigatório. O antigo `/admin/` público foi retirado do GitHub Pages.

## Princípios

- **PR only:** nenhuma escrita direta em `main`.
- **Private by default:** interface e backend administrativo ficam atrás do acesso da equipe Netlify.
- **Policy as code:** `control-plane.json` define escopo, caminhos bloqueados, budgets, thresholds SEO e experimentos ativos.
- **Evidence first:** decisões usam release, CI, Search Console, experimentos e histórico; ausência de evidência não é tratada como falha técnica.
- **Release truth:** alterações editoriais atualizam SHA-256 no `release.json`; o runtime privado também gera release criptográfico dos bytes servidos pelo Netlify.
- **Defense in depth:** Admin Integrity + Admin Production Smoke + Site Integrity + Production Smoke + barreira anônima Netlify.

## Módulos

1. **Comando** — saúde técnica, pipelines e fila operacional.
2. **Conteúdo / Book Publisher** — catálogo, novo livro, capa, PDF e bundle atômico.
3. **SEO Intelligence** — GSC atual/baseline, tendências, CTR, striking distance, canibalização e PDF × HTML.
4. **Experimentos** — janela temporal e regra explícita de decisão.
5. **Monetização** — suporte, afiliados e premium sob guardrails.
6. **Deploy & Releases** — PRs, runs, hashes e produção.
7. **Qualidade** — gates técnicos normalizados e diagnóstico exportável.
8. **Editor seguro / Change Set** — staging, diff, preflight, risco e PR-only.
9. **Conhecimento** — memória operacional versionada, sem persistir métricas privadas do GSC no repositório.
10. **Cérebro operacional** — backend privado que combina release, CI, GSC, experimentos e audit trail para produzir uma fila de ações priorizadas.

## Backend privado

As Netlify Functions implementam quatro contratos independentes:

- **Operational Brain:** avaliação determinística e priorização por evidência.
- **Audit trail:** histórico persistente em Netlify Blobs, sem armazenar secrets.
- **GSC Sync:** coleta privada automática diária quando OAuth do Search Console estiver configurado.
- **GitHub Server Publish:** criação server-side de PRs para Change Sets textuais quando `FCC_GITHUB_TOKEN` estiver configurado. O fluxo manual de sessão GitHub permanece como fallback e continua obrigatório para bundles binários de livros.

Secrets nunca pertencem ao repositório. Eles devem existir somente nas Environment Variables privadas do projeto Netlify.
