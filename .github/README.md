# GitHub automation

Arquivos desta pasta:

- `workflows/site-integrity.yml` — valida integridade estrutural, PDFs e sitemap.
- `CODEOWNERS` — define proprietário padrão e áreas críticas.
- `pull_request_template.md` — checklist obrigatório para mudanças.
- `BRANCH_PROTECTION.md` — contrato recomendado para proteção da `main`.
- `PULL_REQUEST_POLICY.md` — política de integração.
- `SECURITY_POLICY.md` — política operacional do repositório.

A única camada que não pode ser aplicada por arquivo é o ruleset administrativo da branch `main`; ele deve ser ativado nas configurações do repositório.
