# Freedom Organic Control Plane V4

Sistema de decisão para crescimento orgânico da Freedom Book com foco em evidência, estabilidade e custo operacional mínimo.

## Princípio

A V4 não tenta publicar mais. Ela tenta **decidir melhor**.

O sistema separa cinco perguntas:

1. O que está começando a ganhar tração?
2. O que está perdendo tração de forma material?
3. Qual URL já possui autoridade para absorver uma intenção?
4. Onde o grafo interno está deixando autoridade subutilizada?
5. Quais páginas já aparecem em AI Overviews / AI Mode e com qual nível de evidência?

Nenhuma dessas respostas autoriza publicação automática.

## 1. Search Intelligence V1

`scripts/seo_intelligence.py`

Analisa uma janela do Google Search Console e classifica oportunidades por consulta/página:

- `CTR_OPPORTUNITY`
- `STRIKING_DISTANCE`
- `EXPAND_EXISTING_PAGE`
- `NEW_INTENT_REVIEW`
- `OBSERVE`

Também sinaliza canibalização e aplica gates antes de qualquer revisão de nova URL.

## 2. Temporal Intelligence

`scripts/seo_temporal.py`

Compara duas janelas equivalentes do Search Console. Exemplos recomendados:

- últimos 7 dias completos vs. 7 dias completos anteriores;
- últimos 28 dias completos vs. 28 dias completos anteriores.

Estados:

- `BREAKOUT` — crescimento forte de impressões acompanhado de melhora relevante de posição;
- `ACCELERATING_STRIKING_DISTANCE` — URL avançando dentro da faixa aproximadamente 8–20;
- `EMERGING` — crescimento de demanda ainda sem confirmação suficiente;
- `DEFEND_RANKING` — página relevante no top 10 com deterioração material;
- `DECAYING` — queda de impressões acompanhada por perda de posição;
- `STABLE` — sem mudança temporal material;
- `NEW_OBSERVED` — linha nova na janela atual, sem histórico comparável;
- `NOT_IN_CURRENT_EXPORT` — linha ausente no export atual, sem inferir tráfego zero.

### Regra crítica de segurança

Uma consulta ausente no export atual **não é tratada como zero**. Search Console pode devolver apenas as principais linhas; ausência de linha não comprova desaparecimento da demanda.

## 3. Generative Visibility Intelligence

`scripts/generative_visibility.py`

Lê o export oficial do relatório de performance da IA generativa do Search Console para páginas exibidas em recursos como AI Overviews e AI Mode.

Estados:

- `STRONG_AI_VISIBILITY`
- `AI_VISIBLE`
- `EARLY_AI_SIGNAL`
- `AI_ZERO_OR_UNAVAILABLE`
- `NOT_IN_AI_EXPORT`

### Regra crítica de segurança

O Search Console informa que valores apresentados como `~` ou indisponíveis podem ser exportados como zero. Por isso, zero **não é interpretado como ausência comprovada de visibilidade em IA**. Da mesma forma, linha ausente não vira zero por causa dos limites de linhas dos relatórios.

Quando um export regular por página também é fornecido, o sistema calcula uma razão observacional IA/Web, sem tratá-la como sinal interno de ranking.

## 4. Internal Link Intelligence

`scripts/internal_link_intelligence.py`

Constrói um grafo dirigido usando somente URLs indexáveis presentes no sitemap e links internos reais encontrados nos HTMLs.

Mede:

- indegree;
- outdegree;
- páginas órfãs;
- dead ends;
- páginas sub-linkadas;
- links guia → guia;
- distribuição de autoridade por PageRank local determinístico;
- similaridade tópica para sugestões revisáveis de links.

O relatório nunca edita HTML automaticamente. Toda sugestão usa `REVIEW_INTERNAL_LINK`.

## 5. Gates editoriais

Antes de criar uma nova URL, a operação deve preferir nesta ordem:

1. consolidar a URL vencedora existente;
2. melhorar cobertura de intenção;
3. reforçar links internos semanticamente relevantes;
4. corrigir CTR/snippet quando a posição já é boa;
5. investigar canibalização;
6. verificar se há sinal de visibilidade generativa na URL vencedora;
7. somente então revisar a hipótese de uma nova URL.

## Execução

### Janela única

```bash
python3 scripts/seo_intelligence.py search-console.csv \
  --json-output reports/seo-intelligence.json \
  --markdown-output reports/seo-intelligence.md
```

### Evolução temporal

```bash
python3 scripts/seo_temporal.py current.csv previous.csv \
  --json-output reports/seo-temporal.json \
  --markdown-output reports/seo-temporal.md
```

### Visibilidade em IA generativa

```bash
python3 scripts/generative_visibility.py ai-pages.csv \
  --web-csv web-pages.csv \
  --json-output reports/generative-visibility.json \
  --markdown-output reports/generative-visibility.md
```

### Autoridade interna

```bash
python3 scripts/internal_link_intelligence.py \
  --json-output reports/internal-links.json \
  --markdown-output reports/internal-links.md
```

## Ferramentas e custo

Base obrigatória:

- Google Search Console — gratuito;
- relatórios de performance e IA generativa do Search Console — gratuitos;
- Python 3 — gratuito;
- GitHub — infraestrutura atual;
- GitHub Actions — CI atual;
- GitHub Pages — produção atual.

Nenhuma ferramenta SEO/AEO/GEO paga é requisito da arquitetura.

## Política operacional

O Control Plane recomenda; o PR decide; o CI prova; o Production Smoke confirma.

Fluxo:

`evidência → hipótese → alteração mínima → PR → CI → merge → produção → observação temporal`

Não existe publicação automática, keyword stuffing, doorway generation ou criação em massa de conteúdo.