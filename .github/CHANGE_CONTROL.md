# Change control

Mudanças na `main` devem ser tratadas como produção.

## Classificação

- **Baixo risco:** texto, metadados, ajustes visuais isolados.
- **Médio risco:** rotas, redirects, sitemap, assets compartilhados.
- **Alto risco:** `CNAME`, home, PDFs publicados, workflows e estrutura de publicação.

## Exigências mínimas

- branch dedicada;
- Pull Request;
- `Site integrity / validate` aprovado;
- rollback explícito para mudanças de médio/alto risco;
- preservação de URL para conteúdo já publicado.

A ativação do ruleset nativo da `main` transforma essas políticas em enforcement de servidor.
