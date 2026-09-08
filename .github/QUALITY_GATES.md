# Quality gates

## Obrigatório para publicação

**Site integrity / validate** valida:

- arquivos essenciais e `CNAME`;
- presença do sitemap em `robots.txt`;
- existência de PDFs publicados;
- tamanho mínimo dos PDFs;
- assinatura binária `%PDF-` dos PDFs;
- domínio canônico do sitemap;
- duplicidade de URLs no sitemap;
- existência local de cada rota publicada no sitemap;
- ausência de canonicals legados com `www`.

O ruleset da `main` deve exigir esse check antes do merge.
