# AchadosTube / Freedom Book

Repositório do site público **achadostube.com.br**.

## Estrutura

- `index.html` — home atual da Freedom Book.
- `*.html` — páginas públicas de livros e páginas legadas que ainda podem receber tráfego externo.
- `ebook/` — PDFs publicados da Freedom Book.
- `imagens/` — capas, logos, QR e imagens editoriais.
- `og/` — imagens para Open Graph/compartilhamento.
- `product/` e páginas `kit-*` — conteúdo legado do projeto AchadosTube/Shopee; mantido para preservar URLs existentes.
- `assets/` — recursos compartilhados do site.
- `CNAME` — domínio customizado do GitHub Pages.
- `sitemap.xml` / `robots.txt` — descoberta e indexação pelos buscadores.

## Regras de manutenção

1. Não substituir PDFs por placeholders ou arquivos vazios.
2. Manter URLs públicas existentes sempre que possível; páginas antigas devem redirecionar em vez de simplesmente desaparecer.
3. Usar `https://achadostube.com.br/` como origem canônica principal.
4. Alterações relevantes devem passar por branch/PR antes de chegar à `main`.
5. Antes de publicar um livro, validar página, capa e PDF.
6. Não duplicar a home em vários arquivos grandes; aliases legados devem ser redirects leves.

## Produção

A branch `main` é a origem publicada. O domínio configurado é `achadostube.com.br`.

A organização V2.1 da Freedom Book consolida SEO, catálogo, privacidade, sitemap, robots e recuperação de downloads corrompidos sem remover o conteúdo legado do AchadosTube.
