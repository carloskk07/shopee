# Freedom Control Center

Painel operacional do site Freedom Book/AchadosTube. O shell é servido em `/admin/`, fica fora do sitemap e usa `noindex,nofollow,noarchive,nosnippet`.

## Segurança operacional

O painel inicia em modo leitura. Para criar alterações, o operador fornece um GitHub fine-grained PAT limitado ao repositório `carloskk07/shopee`, com `Contents: Read and write` e `Pull requests: Read and write`. O token fica apenas em memória JavaScript e é removido ao atualizar/fechar a aba; não é salvo em cookies, `localStorage`, `sessionStorage` ou arquivos do repositório.

A publicação nunca escreve diretamente na `main`: cria uma branch, gera um único commit via Git Data API, atualiza automaticamente SHA-256 de arquivos já controlados por `release.json` e abre um Pull Request. Workflows GitHub são bloqueados no editor.

## Search Console

A V1 importa CSV do Google Search Console localmente no navegador. A integração OAuth direta é deliberadamente adiada até existir um backend autenticado; credenciais Google não devem ser incorporadas ao GitHub Pages.

## Limite de segurança conhecido

GitHub Pages é hospedagem pública. Portanto o shell HTML do painel não é uma área privada no sentido de controle de acesso no servidor; somente as ações de escrita são autenticadas. Uma futura V2 pode mover apenas o `/admin` para backend com autenticação server-side, mantendo o site público estático.
