# AchadosTube / Freedom Book

Repositório público de `achadostube.com.br`.

## Produção atual

O núcleo editorial atual é a **Freedom Book V2.2.5**. A publicação é tratada como um contrato verificável:

`branch -> PR -> Site integrity / validate -> main -> GitHub Pages -> Production smoke`

A origem pública `https://achadostube.com.br/` é publicada pelo **GitHub Pages** a partir da `main`. O `CNAME` é a autoridade do domínio dentro do repositório. Endpoints exclusivos da Vercel, como `/_vercel/image`, não podem ser usados no HTML de produção.

A branch `main` é protegida por ruleset ativo e aceita somente fluxo por Pull Request com **Squash**, status check obrigatório e bloqueio de force push/deleção.

## Estrutura

- `index.html` — home Freedom Book.
- `autor-arthur-magnus.html` — entidade editorial pública do autor.
- `*.html` — páginas editoriais públicas e páginas legadas preservadas.
- `assets/style.v2.2.5.css` — CSS ativo da release, versionado no próprio nome do arquivo.
- `assets/app.v2.2.5.js` — runtime ativo, catálogo, consentimento, telemetria e funil editorial.
- `assets/covers/` — capas WebP estáticas otimizadas para GitHub Pages.
- `assets/icons/` — ícones PWA/Apple otimizados.
- `site-data.generated.json` — contrato de dados do catálogo.
- `ebook/` — PDFs publicados.
- `imagens/` — originais das capas, logos e QR.
- `og/` — imagens sociais.
- `feed.xml` — feed Atom dos títulos disponíveis.
- `sitemap.xml` — sitemap canônico com descoberta de imagens das capas.
- `release.json` — hashes SHA-256 dos artefatos críticos esperados em produção.
- `deploy-marker.json` — provenance da origem, branch e provedor de produção.
- `robots.txt` — política de rastreamento e descoberta do sitemap.
- `.github/workflows/site-integrity.yml` — gate obrigatório antes do merge.
- `.github/workflows/production-smoke.yml` — validação do domínio depois do deploy.
- `product/`, `locked/` e páginas `kit-*` — legado AchadosTube/Shopee preservado para compatibilidade e tráfego existente.
- `assets/legacy-offer.v1.css` + `assets/legacy-consent.v1.js` — superfície leve das páginas legadas de afiliado, com consentimento antes de métricas e sem urgência/estoque/preço simulados.

## Estratégia de cache

GitHub Pages não oferece controle fino de `Cache-Control` por arquivo neste repositório. Por isso, CSS e JavaScript ativos usam **versionamento no nome do arquivo** (`style.v2.2.5.css` / `app.v2.2.5.js`). O HTML é a autoridade que troca a versão dos assets; uma release nova não deve reutilizar o mesmo nome para bytes diferentes.

Os arquivos históricos podem coexistir por compatibilidade, mas o HTML editorial ativo não pode referenciar versões antigas. O `Site integrity` bloqueia regressões desse contrato.

## Telemetria e funil

GA4 e TikTok continuam condicionados ao consentimento correspondente. A V2.2.5 mantém metadados editoriais de baixo risco para melhorar leitura do funil sem enviar texto pesquisado, UTMs brutas ou referrer completo:

- release;
- tipo de página;
- origem ampla (`direct`, `internal`, `search`, `social`, `referral` ou `unknown`);
- comprimento da busca e quantidade de resultados;
- livro, posição e ação editorial quando aplicável.

## Regras de manutenção

1. Nunca atualizar `main` diretamente; usar branch + PR.
2. Não publicar PDFs vazios, placeholders ou sem assinatura `%PDF-`.
3. Não anunciar PDF/landing que não exista.
4. Preservar URLs antigas quando houver tráfego potencial.
5. Usar `https://achadostube.com.br/` como origem canônica.
6. Não carregar GA4/TikTok antes do consentimento correspondente.
7. Alterações de catálogo devem manter `site-data.generated.json`, HTML, `feed.xml` e sitemap coerentes.
8. Não referenciar endpoints de outro provedor no HTML público.
9. Não reutilizar o nome de um asset versionado para conteúdo diferente.
10. Uma release só é considerada realmente publicada quando **Production smoke** passa.

## Release

Release editorial atual: `2026.09.08-v2.2.5`.

`deploy-marker.json` identifica a cadeia de deploy ativa; `release.json` identifica criptograficamente os bytes críticos da release e é a autoridade do smoke pós-deploy.
