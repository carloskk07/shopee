# Contribuição e publicação

Este repositório publica o site `achadostube.com.br`. Mudanças devem ser tratadas como alterações de produção.

## Fluxo recomendado

1. Criar uma branch a partir de `main`.
2. Fazer alterações pequenas e rastreáveis.
3. Abrir Pull Request para `main`.
4. Aguardar o check **Site integrity** concluir com sucesso.
5. Revisar URLs públicas, PDFs e sitemap.
6. Fazer merge por squash quando a alteração representar uma única unidade lógica.

## Não fazer

- Não substituir PDFs por placeholders, arquivos vazios ou arquivos sem assinatura `%PDF-`.
- Não alterar `CNAME` sem mudança intencional de domínio.
- Não remover URLs públicas sem redirect.
- Não duplicar a home inteira em aliases legados.
- Não inserir URLs canônicas com `www`; a origem oficial é `https://achadostube.com.br/`.

## Proteção recomendada da `main`

No GitHub, habilitar uma regra/ruleset para `main` com:

- Require a pull request before merging;
- Require status checks to pass before merging;
- status check obrigatório: **Site integrity / validate**;
- Require conversation resolution before merging;
- Block force pushes;
- Block deletions.

O repositório já contém `CODEOWNERS`, template de PR e CI compatíveis com essa proteção.
