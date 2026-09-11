# Freedom Control Center V2

Console operacional privado da Freedom Book. O site editorial continua em GitHub Pages, enquanto o Control Center é entregue separadamente pelo Netlify em `freedom-book-admin.netlify.app/admin/` com Team SSO obrigatório. O antigo `/admin/` público permanece retirado do GitHub Pages.

## Princípios

- **PR only:** nenhuma escrita direta em `main`.
- **Human approved:** o Cérebro pode calcular, preparar e acompanhar decisões, mas não faz auto-merge nem mutação direta de produção.
- **Private by default:** interface, GSC, decision ledger, audit trail e backend administrativo ficam atrás do acesso da equipe Netlify.
- **Policy as code:** `control-plane.json` define escopo, caminhos bloqueados, budgets, thresholds SEO, objetivos, guardrails e experimentos ativos.
- **Evidence first:** decisões usam release, CI, Search Console finalizado, experimentos, inventário e histórico; ausência de evidência não é tratada como falha técnica.
- **Causalidade temporal:** um experimento só entra em janela de decisão quando o GSC finalizado alcança a data mínima, usando comparação pré/pós de mesmo tamanho.
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
9. **Conhecimento** — política operacional versionada sem persistir métricas privadas no repositório público.
10. **Cérebro operacional V2** — closed-loop decision engine, observabilidade, lifecycle editorial, decision ledger e vínculo experimento → Change Set → PR → observação.

## Closed-loop Decision Engine

O ciclo operacional é:

`evidência → decisão → Change Set → PR → CI/deploy → observação → KEEP | ITERATE | REVERT | INCONCLUSIVE`

O motor usa linhas diárias do Search Console para montar uma janela pós-intervenção e uma janela pré-intervenção do mesmo tamanho. A data do calendário, sozinha, nunca abre uma decisão. O dataset finalizado precisa alcançar `minimumDecisionDate` e satisfazer os critérios mínimos do experimento.

Decisões ficam no **Decision Ledger privado** em Netlify Blobs. Quando `ITERATE` ou `REVERT` prepara uma mudança, o contexto causal é mantido em `sessionStorage` apenas durante a sessão e anexado ao PR server-side. O PR recebe um marcador estruturado com `decisionId`, `experimentId`, verdict e fingerprint da evidência, permitindo rastrear o ciclo sem colocar métricas do GSC no GitHub.

## Backend privado

As Netlify Functions e libs implementam contratos separados:

- **Operational Brain V2:** avaliação determinística, fila causal, observabilidade, lifecycle editorial e reconciliação do decision loop.
- **Decision Engine / Ledger:** janelas pré/pós equivalentes, gates de GSC finalizado, recomendações e registros privados.
- **Audit trail:** histórico persistente em Netlify Blobs, sem armazenar secrets.
- **GSC Sync:** coleta privada automática diária via OAuth readonly e persistência do snapshot atual + baseline em Netlify Blobs.
- **GitHub Server Publish:** criação server-side de PRs para Change Sets textuais e vínculo opcional ao Decision Ledger. O fluxo manual de sessão GitHub permanece como fallback e continua obrigatório para bundles binários de livros.

Secrets nunca pertencem ao repositório. Eles devem existir somente nas Environment Variables privadas do projeto Netlify.
