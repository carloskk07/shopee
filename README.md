# AchadosTube / Freedom Book

Repositório público de `achadostube.com.br`.

## Produção atual

O núcleo editorial atual é a **Freedom Book V2.2**. A publicação é tratada como um contrato verificável:

`branch -> PR -> Site integrity / validate -> main -> Vercel -> Production smoke`

A branch `main` é protegida por ruleset ativo e aceita somente fluxo por Pull Request com **Squash**, status check obrigatório e bloqueio de force push/deleção.

## Estrutura

- `index.html` — home Freedom Book.
- `*.html` — páginas editoriais públicas e páginas legadas preservadas.
- `assets/style.v2.2.css` — CSS versionado da Freedom Book.
- `assets/app.v2.2.js` — runtime, catálogo, compartilhamento e consentimento.
- `site-data.generated.json` — contrato de dados do catálogo.
- `ebook/` — PDFs publicados.
- `imagens/` — capas, logos e QR.
- `og/` — imagens sociais.
- `release.json` — sentinela da versão esperada em produção.
- `vercel.json` — clean URLs, redirects e headers do deploy Vercel.
- `sitemap.xml` / `robots.txt` — descoberta e indexação.
- `.github/workflows/site-integrity.yml` — gate obrigatório antes do merge.
- `.github/workflows/production-smoke.yml` — validação do domínio depois do deploy.
- `product/`, `locked/` e páginas `kit-*` — legado AchadosTube/Shopee preservado para compatibilidade e tráfego existente.

## Regras de manutenção

1. Nunca atualizar `main` diretamente; usar branch + PR.
2. Não publicar PDFs vazios, placeholders ou sem assinatura `%PDF-`.
3. Não anunciar PDF/landing que não exista.
4. Preservar URLs antigas por redirect quando houver tráfego potencial.
5. Usar `https://achadostube.com.br/` como origem canônica.
6. Não carregar GA4/TikTok antes do consentimento correspondente.
7. Alterações de catálogo devem manter `site-data.generated.json`, HTML e sitemap coerentes.
8. Uma release só é considerada realmente publicada quando **Production smoke** passa.

## Release

Release editorial atual: `2026.09.08-v2.2`.
