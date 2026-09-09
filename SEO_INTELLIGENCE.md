# Freedom Search Intelligence

Camada de decisão orgânica da Freedom Book baseada em dados reais do Google Search Console.

## Objetivo

Transformar consultas, impressões, cliques, CTR, posição e páginas observadas em decisões auditáveis de SEO sem criar páginas em massa e sem depender de ferramentas pagas.

O motor **não publica conteúdo automaticamente**. Ele classifica oportunidades e exige evidência antes de recomendar nova URL.

## Fonte de dados gratuita

Use o relatório **Desempenho > Resultados da pesquisa** do Google Search Console e exporte CSV contendo, quando disponível:

- consulta;
- página;
- cliques;
- impressões;
- CTR;
- posição média.

O script aceita cabeçalhos em português ou inglês e não exige bibliotecas externas.

## Execução

```bash
python3 scripts/seo_intelligence.py search-console.csv \
  --json-output reports/seo-intelligence.json \
  --markdown-output reports/seo-intelligence.md
```

## Decisões

### `CTR_OPPORTUNITY`
Página já aparece bem, recebe volume suficiente e apresenta CTR baixo para a posição. A primeira hipótese deve ser melhorar title, snippet provável, promessa editorial e alinhamento de intenção — não criar outra URL.

### `STRIKING_DISTANCE`
Consulta com impressões e posição aproximadamente entre 8 e 20. Prioridade para fortalecer a página existente: cobertura semântica, seção específica, links internos e clareza de resposta.

### `EXPAND_EXISTING_PAGE`
A consulta possui afinidade suficiente com um guia existente. O motor favorece consolidar autoridade na URL atual em vez de fragmentar o cluster.

### `NEW_INTENT_REVIEW`
Sinal preliminar de intenção pouco coberta. Isso **não autoriza uma nova página** por si só.

### `REVIEW_FOR_NEW_URL`
Só aparece quando um cluster passa simultaneamente por gates mínimos:

- pelo menos 100 impressões agregadas;
- pelo menos 3 consultas distintas;
- baixa similaridade com guias atuais;
- nenhuma página existente domina 55% ou mais das impressões do cluster.

Mesmo após esses gates, a criação da URL continua sendo uma decisão editorial revisada por humano/PR.

## Canibalização

O motor sinaliza uma consulta quando duas ou mais páginas dividem de forma material as impressões. O objetivo é descobrir casos em que páginas concorrentes deveriam ser consolidadas, diferenciadas ou receber links internos mais claros.

## Guardrails

- nenhuma métrica é inventada;
- nenhum volume estimado de ferramenta de terceiros é tratado como dado real;
- nenhuma página é criada automaticamente;
- nenhuma palavra-chave é injetada dinamicamente para tentar enganar o buscador;
- não existe regra de “uma consulta = uma URL”;
- dados de Search Console são usados para melhorar utilidade e alinhamento editorial, não para produzir doorway pages;
- alterações de conteúdo continuam passando por branch, PR, `validate`, `release.json`, GitHub Pages e production smoke.

## Ferramentas

A versão inicial depende somente de:

- Google Search Console — gratuito;
- Python 3 — gratuito;
- GitHub Actions — dentro da franquia disponível da conta/repositório;
- GitHub Pages — hospedagem atual do projeto.

Integrações externas são opcionais. Quando houver alternativa gratuita de qualidade, ela deve ser preferida antes de qualquer serviço pago.
