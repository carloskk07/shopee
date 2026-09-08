# AchadosTube / Freedom Book

Repositório público de `achadostube.com.br`.

## Produção atual

O núcleo editorial atual é a **Freedom Book V2.2.1**. A publicação é tratada como um contrato verificável:

`branch -> PR -> Site integrity / validate -> main -> GitHub Pages -> Production smoke`

A origem pública `https://achadostube.com.br/` é publicada pelo **GitHub Pages** a partir da `main`. O `CNAME` é a autoridade do domínio dentro do repositório. Endpoints exclusivos da Vercel, como `/_vercel/image`, não podem ser usados no HTML de produção.

A branch `main` é protegida por ruleset ativo e aceita somente fluxo por Pull Request com **Squash**, status check obrigatório e bloqueio de force push/deleção.

## Estrutura

- `index.html` — home Freedom Book.
- `*.html` — páginas editoriais públicas e páginas legadas preservadas.
- `assets/style.v2.2.css` — CSS versionado da Freedom Book.
- `assets/app.v2.2.js` — runtime, catálogo, compartilhamento e consentimento.
- `assets/covers/` — capas WebP estáticas otimizadas para GitHub Pages.
- `site-data.generated.json` — contrato de dados do catálogo.
- `ebook/` — PDFs publicados.
- `imagens/` — originais das capas, logos e QR.
- `og/` — imagens sociais.
- `release.json` — hashes SHA-256 dos artefatos críticos esperados em produção.
- `deploy-marker.json` — provenance da origem, branch e provedor de produção.
- `sitemap.xml` / `robots.txt` — descoberta e indexação.
- `.github/workflows/site-integrity.yml` — gate obrigatório antes do merge.
- `.github/workflows/production-smoke.yml` — validação do domínio depois do deploy.
- `product/`, `locked/` e páginas `kit-*` — legado AchadosTube/Shopee preservado para compatibilidade e tráfego existente.

## Regras de manutenção

1. Nunca atualizar `main` diretamente; usar branch + PR.
2. Não publicar PDFs vazios, placeholders ou sem assinatura `%PDF-`.
3. Não anunciar PDF/landing que não exista.
4. Preservar URLs antigas quando houver tráfego potencial.
5. Usar `https://achadostube.com.br/` como origem canônica.
6. Não carregar GA4/TikTok antes do consentimento correspondente.
7. Alterações de catálogo devem manter `site-data.generated.json`, HTML e sitemap coerentes.
8. Não referenciar endpoints de outro provedor no HTML público.
9. Uma release só é considerada realmente publicada quando **Production smoke** passa.

## Release

Release editorial atual: `2026.09.08-v2.2.1`.

`deploy-marker.json` identifica a cadeia de deploy ativa; `release.json` identifica criptograficamente os bytes críticos da release e é a autoridade do smoke pós-deploy.
