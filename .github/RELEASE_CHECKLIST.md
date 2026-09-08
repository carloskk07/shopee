# Checklist de publicação

Antes de integrar uma mudança em `main`:

- [ ] `Site integrity / validate` passou.
- [ ] Home abre sem regressão visual evidente.
- [ ] Páginas alteradas abrem e usam a origem canônica correta.
- [ ] PDFs alterados abrem e não são placeholders.
- [ ] URLs antigas continuam funcionando ou redirecionam.
- [ ] `sitemap.xml` corresponde às páginas públicas.
- [ ] `robots.txt` aponta para o sitemap oficial.
- [ ] Existe estratégia de rollback simples.

Após o merge:

- [ ] Confirmar o commit publicado na `main`.
- [ ] Confirmar o domínio `achadostube.com.br`.
- [ ] Se houver falha, reverter o commit/PR imediatamente.
