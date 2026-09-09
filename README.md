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
- `assets/route-recovery.v1.js` — fallback client-side para aliases conhecidos que ainda alcancem o `404.html`.
- `route-shims.generated.json` — manifesto determinístico das rotas estáticas de compatibilidade servidas pelo GitHub Pages.
- `*/index.html` nas rotas compatíveis — shims estáticos `noindex` que eliminam 404 HTTP em variantes com barra final e aliases históricos conhecidos.
- `assets/covers/` — capas WebP estáticas otimizadas para GitHub Pages.
- `assets/icons/` — ícones PWA/Apple otimizados.
- `site-data.generated.json` — contrato de dados do catálogo.
- `ebook/` — PDFs publicados.
- `imagens/` — originais das capas, logos e QR.
- `og/` — imagens sociais.
- `feed.xml` — feed Atom dos títulos disponíveis.
- `sitemap.xml` — sitemap canônico com descoberta de imagens das capas.
- `release.json` — hashes SHA-256 dos artefatos críticos esperados em produção, incluindo o manifesto de rotas.
- `deploy-marker.json` — provenance da origem, branch e provedor de produção.
- `robots.txt` — política de rastreamento e descoberta do sitemap.
- `_redirects` — mapa declarativo de compatibilidade e fonte de verdade para aliases; o GitHub Pages não o executa como regra de servidor.
- `.github/workflows/site-integrity.yml` — gate obrigatório antes do merge.
- `.github/workflows/route-integrity.yml` — valida aliases, barras finais, shims estáticos e proteção contra open redirect.
- `.github/workflows/production-smoke.yml` — validação geral do domínio depois do deploy.
- `.github/workflows/route-production-smoke.yml` — prova pós-deploy de que cada rota compatível responde no HTTP com o shim exato e que rotas desconhecidas continuam 404.
- `product/`, `locked/` e páginas `kit-*` — legado AchadosTube/Shopee preservado para compatibilidade e tráfego existente.
- `assets/legacy-offer.v1.css` + `assets/legacy-consent.v1.js` — superfície leve das páginas legadas de afiliado, com consentimento antes de métricas e sem urgência/estoque/preço simulados.

## Integridade visual das capas

As capas editoriais nunca podem ser recortadas para preencher um quadro. `assets/cover-integrity.v1.css` preserva a proporção natural da arte com `object-fit: contain` e remove dependência de `aspect-ratio: 2/3` nas superfícies de catálogo, destaque e landing individual. Os HTMLs editoriais também não fixam `width`/`height` nas capas, evitando que metadados antigos imponham uma proporção incorreta.

## Compatibilidade de rotas no GitHub Pages

O GitHub Pages não interpreta `_redirects` como Netlify/Vercel. Por isso, confiar apenas no `404.html` e em JavaScript deixava uma falha real no nível HTTP: a variante `/proposito-maior/`, por exemplo, continuava respondendo 404 antes da execução do navegador.

A proteção agora tem duas camadas. `scripts/generate-route-shims.py` materializa de forma determinística páginas estáticas `index.html` para as variantes canônicas com barra final e aliases conhecidos. Cada shim retorna conteúdo HTML real pelo GitHub Pages, permanece `noindex,follow`, aponta `canonical` para a URL correta e redireciona para o destino esperado. `assets/route-recovery.v1.js` continua como fallback adicional para casos conhecidos que ainda alcancem o 404, preservando query string e fragmento.

`route-shims.generated.json` registra caminho público, arquivo, destino e SHA-256 de cada shim. `Site integrity / validate` e `Route integrity` bloqueiam drift local; `Route production smoke` verifica os bytes no domínio publicado e também confirma que uma rota desconhecida continua retornando 404.

URLs canônicas continuam sem barra final. As rotas de compatibilidade existem somente para recuperação e preservação de tráfego antigo.

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
10. Alterações em aliases/canônicas devem regenerar os shims e manter `route-shims.generated.json` coerente.
11. Uma release só é considerada realmente publicada quando **Production smoke** passa; mudanças de compatibilidade de rotas também exigem **Route production smoke** verde.

## Release

Release editorial atual: `2026.09.08-v2.2.5`.

`deploy-marker.json` identifica a cadeia de deploy ativa; `release.json` identifica criptograficamente os bytes críticos da release e é a autoridade do smoke pós-deploy.
