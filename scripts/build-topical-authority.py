#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = 'https://achadostube.com.br'
DATE = '2026-09-09'
RELEASE = '2026.09.08-v2.2.5'
GUIDE_CSS = '/assets/editorial-guides.v1.css'

GUIDES = [
    {
        'slug': 'como-encontrar-proposito-na-vida',
        'title': 'Como encontrar propósito na vida com mais clareza',
        'short': 'Como encontrar propósito na vida',
        'description': 'Um processo prático para separar expectativas externas, valores pessoais, prioridades e próximos passos quando você sente que perdeu direção.',
        'kicker': 'Propósito e direção',
        'image': CANON + '/assets/covers/capa-proposito-maior.webp',
        'books': [('proposito-maior', 'Propósito Maior')],
        'keywords': ['propósito', 'direção', 'valores', 'clareza', 'prioridades'],
        'body': '''
<p>Encontrar propósito não exige descobrir uma frase perfeita sobre “a missão da sua vida”. Na prática, propósito costuma ficar mais claro quando você consegue ligar três coisas: o que considera importante, o tipo de pessoa que quer ser nas situações reais e o que merece receber sua energia agora.</p>
<p>Se você está sem direção, o primeiro objetivo não é resolver os próximos dez anos. É reduzir o ruído suficiente para enxergar o próximo passo com mais coerência.</p>
<h2>1. Separe propósito de pressão</h2>
<p>Muita confusão nasce quando expectativas externas são tratadas como desejos pessoais. Família, trabalho, comparação social e medo de ficar para trás podem produzir metas que parecem importantes, mas não combinam com o que você valoriza.</p>
<p>Faça duas colunas. Na primeira, escreva “o que esperam de mim”. Na segunda, “o que eu escolheria mesmo sem precisar provar nada”. Não tente julgar as respostas; observe onde existe conflito. Essa diferença já mostra onde parte da sua energia está sendo gasta.</p>
<h2>2. Procure valores antes de procurar uma grande meta</h2>
<p>Metas mudam. Valores funcionam como critérios. Você pode trocar de trabalho, cidade ou projeto e ainda continuar valorizando autonomia, presença, aprendizado, família, criação, contribuição ou estabilidade.</p>
<p>Escolha no máximo cinco valores que você realmente reconhece na prática. Depois reduza para três. A pergunta útil é: “quando duas opções parecem boas, qual delas respeita melhor esses três critérios?”</p>
<h2>3. Observe o que produz energia e o que produz apenas alívio</h2>
<p>Nem tudo que é agradável aponta direção. Algumas escolhas só diminuem desconforto por alguns minutos. Outras exigem esforço, mas deixam sensação de coerência depois. Durante uma semana, anote atividades que deixam você mais presente, mais interessado ou com vontade de continuar aprendendo.</p>
<p>O padrão é mais valioso do que um momento isolado. Propósito pode aparecer primeiro como recorrência: temas, problemas, pessoas ou atividades para os quais você volta espontaneamente.</p>
<h2>4. Use a regra do próximo passo verificável</h2>
<p>Uma direção vaga fica mais útil quando vira um experimento pequeno. Em vez de “quero mudar de vida”, formule algo que possa ser executado em até sete dias: conversar com alguém da área, reservar duas horas para um projeto, eliminar um compromisso que não faz mais sentido ou testar uma rotina diferente.</p>
<div class="guide-callout"><strong>Teste de clareza:</strong> se o próximo passo é tão grande que você continua apenas pensando nele, reduza até caber na agenda desta semana.</div>
<h2>5. Faça uma revisão de coerência</h2>
<p>No fim da semana, responda: o que eu fiz porque realmente importava? O que fiz no automático? O que aceitei apenas para evitar desconforto? Qual escolha pequena me deixou mais alinhado com quem quero ser?</p>
<p>Propósito não precisa chegar como revelação. Ele pode ser construído pela repetição de escolhas coerentes. Quando essas escolhas começam a apontar na mesma direção, a sensação de “não sei para onde ir” tende a perder força.</p>
<h2>Um exercício de 20 minutos</h2>
<ol class="guide-steps"><li>Liste cinco momentos dos últimos anos em que você se sentiu genuinamente envolvido.</li><li>Marque o que havia em comum entre eles.</li><li>Escolha três valores presentes nesses momentos.</li><li>Identifique uma área da vida que hoje contradiz esses valores.</li><li>Defina uma ação pequena para aproximar essa área do que você considera importante.</li></ol>
<p>O objetivo não é criar uma identidade rígida. É recuperar uma direção suficientemente boa para agir, observar o resultado e ajustar.</p>
'''
    },
    {
        'slug': 'como-melhorar-o-foco-e-reduzir-distracoes',
        'title': 'Como melhorar o foco e reduzir distrações no dia a dia',
        'short': 'Como melhorar o foco',
        'description': 'Um método simples para proteger atenção, diminuir trocas de contexto e transformar prioridades em blocos de trabalho executáveis.',
        'kicker': 'Foco e atenção',
        'image': CANON + '/assets/covers/capa-foco-que-gera-resultados.webp',
        'books': [('foco-que-gera-resultados', 'Foco Que Gera Resultados')],
        'keywords': ['foco', 'distrações', 'atenção', 'prioridades', 'produtividade'],
        'body': '''
<p>Foco não é a capacidade de nunca se distrair. É a capacidade de retornar ao que importa com pouco atrito. Quando o dia é organizado para exigir dezenas de decisões, notificações e trocas de tarefa, depender apenas de força de vontade costuma funcionar mal.</p>
<p>Uma estratégia mais robusta é diminuir o número de coisas competindo pela atenção e deixar a próxima ação óbvia.</p>
<h2>1. Escolha uma prioridade operacional, não uma intenção genérica</h2>
<p>“Trabalhar no projeto” é amplo demais. “Escrever a primeira página”, “revisar os cinco primeiros itens” ou “ligar para três clientes” já define comportamento. Antes de começar, escreva a entrega concreta que tornará o bloco de tempo concluído.</p>
<h2>2. Trabalhe em blocos com começo e fim</h2>
<p>Reserve um período curto o suficiente para parecer executável e longo o suficiente para produzir avanço. Para muitas tarefas, 30 a 60 minutos funcionam melhor do que esperar várias horas livres. Durante o bloco, mantenha apenas o material necessário à vista.</p>
<p>Ao terminar, faça uma pausa real e decida conscientemente se começa outro bloco. Isso reduz a sensação de trabalho infinito.</p>
<h2>3. Reduza trocas de contexto</h2>
<p>Cada troca entre mensagem, navegador, documento, telefone e outra tarefa exige reconstruir mentalmente onde você estava. Agrupe atividades semelhantes: mensagens em determinados horários, tarefas administrativas juntas e trabalho que exige concentração em blocos separados.</p>
<div class="guide-callout"><strong>Regra prática:</strong> antes de abrir uma nova aba ou aplicativo, pergunte se isso é necessário para terminar a entrega definida para o bloco atual.</div>
<h2>4. Tire distrações previsíveis do caminho</h2>
<p>Notificações, celular ao alcance da mão e páginas abertas “para depois” são distrações previsíveis. Em vez de lutar contra cada uma delas, torne-as menos acessíveis durante o período de foco. Silencie notificações não essenciais, feche abas não relacionadas e deixe o celular fora do campo de visão quando a tarefa permitir.</p>
<h2>5. Crie um lugar para pensamentos que aparecem no meio</h2>
<p>Uma parte da distração acontece porque você teme esquecer algo. Mantenha uma nota chamada “depois”. Quando surgir uma ideia ou obrigação que não pertence ao bloco atual, registre em uma linha e volte. Assim você não precisa resolver imediatamente para ter segurança de que não esquecerá.</p>
<h2>6. Meça avanço, não sensação de produtividade</h2>
<p>Um dia cheio pode produzir pouco. Ao fim do período, pergunte o que efetivamente ficou pronto. Uma ou duas entregas importantes concluídas costumam valer mais do que horas alternando entre tarefas pequenas.</p>
<h2>Protocolo rápido de foco</h2>
<ol class="guide-steps"><li>Defina uma única entrega concreta.</li><li>Separe o material necessário.</li><li>Remova notificações e abas não relacionadas.</li><li>Escolha um bloco de 30 a 60 minutos.</li><li>Use uma nota “depois” para não abandonar a tarefa.</li><li>No final, registre o que avançou e escolha o próximo bloco.</li></ol>
<p>O objetivo é transformar foco em sistema. Quanto menos decisões desnecessárias você precisa tomar durante a execução, mais fácil fica manter atenção no que realmente move o trabalho.</p>
'''
    },
    {
        'slug': 'como-criar-disciplina-sem-depender-de-motivacao',
        'title': 'Como criar disciplina sem depender de motivação',
        'short': 'Como criar disciplina',
        'description': 'Um guia para transformar intenção em rotina com compromissos menores, ambiente favorável, consistência e regras simples de retomada.',
        'kicker': 'Disciplina e constância',
        'image': CANON + '/assets/covers/capa-disciplina-e-liberdade.webp',
        'books': [('disciplina-e-liberdade', 'Disciplina é Liberdade')],
        'keywords': ['disciplina', 'motivação', 'constância', 'hábitos', 'rotina'],
        'body': '''
<p>Motivação varia. Disciplina se torna mais confiável quando a ação certa depende menos do seu estado emocional do momento. Isso não significa viver com rigidez; significa reduzir a negociação interna antes de tarefas que você já decidiu que importam.</p>
<h2>1. Torne o compromisso pequeno o suficiente para começar</h2>
<p>Metas grandes criam resistência quando todo começo parece exigir muito. Defina uma versão mínima da atividade: dez minutos de estudo, uma página escrita, uma caminhada curta, uma ligação importante. A versão mínima não é o objetivo final; é a porta de entrada que preserva continuidade.</p>
<h2>2. Defina quando e onde</h2>
<p>“Vou fazer mais” depende de uma decisão futura. “Depois do café, sento à mesa e faço 20 minutos” já tem gatilho, lugar e duração. Quanto mais clara a condição de início, menos espaço sobra para adiar.</p>
<h2>3. Prepare o ambiente antes de precisar de disciplina</h2>
<p>Deixe o material pronto, remova obstáculos previsíveis e facilite a primeira ação. Se você precisa organizar tudo antes de começar, a preparação vira uma etapa extra onde o hábito pode morrer.</p>
<h2>4. Use regras simples para dias ruins</h2>
<p>Constância não significa desempenho idêntico todos os dias. Crie uma regra de manutenção: em dias difíceis, faça a versão mínima. Isso evita transformar uma queda de energia em abandono completo.</p>
<div class="guide-callout"><strong>Regra de retomada:</strong> perder um dia não redefine sua rotina. O compromisso principal é reduzir o intervalo até a próxima execução.</div>
<h2>5. Diferencie disciplina de punição</h2>
<p>Uma rotina sustentável precisa caber na vida real. Se o plano ignora sono, trabalho, família, imprevistos e descanso, ele depende de condições perfeitas. Ajustar volume não é fracasso; pode ser a decisão que mantém a prática viva.</p>
<h2>6. Acompanhe evidência de consistência</h2>
<p>Marque cada execução em um calendário ou lista simples. O registro não serve para criar culpa, mas para mostrar o padrão real. Depois de duas semanas, você consegue identificar horários que funcionam, obstáculos recorrentes e metas que talvez estejam grandes demais.</p>
<h2>Estrutura de disciplina em seis passos</h2>
<ol class="guide-steps"><li>Escolha uma ação importante.</li><li>Defina uma versão mínima.</li><li>Determine horário ou gatilho de início.</li><li>Prepare o ambiente com antecedência.</li><li>Crie uma regra para dias ruins.</li><li>Revise o padrão semanalmente e ajuste o volume.</li></ol>
<p>A disciplina mais útil não é a que prova força. É a que transforma decisões importantes em ações repetíveis sem consumir toda a sua energia mental.</p>
'''
    },
    {
        'slug': 'como-recomecar-com-mais-clareza',
        'title': 'Como recomeçar com mais clareza sem tentar mudar tudo de uma vez',
        'short': 'Como recomeçar com clareza',
        'description': 'Um roteiro para encerrar ciclos, escolher prioridades e reconstruir movimento com passos pequenos quando você sente necessidade de recomeçar.',
        'kicker': 'Recomeços e escolhas',
        'image': CANON + '/assets/covers/capa-recomecos-sao-escolhas.webp',
        'books': [('recomecos-sao-escolhas', 'Recomeços São Escolhas'), ('a-vida-que-voce-adiou', 'A Vida Que Você Adiou')],
        'keywords': ['recomeçar', 'mudança', 'clareza', 'escolhas', 'próximos passos'],
        'body': '''
<p>Recomeçar costuma parecer uma grande decisão, mas quase sempre é uma sequência de decisões menores. Quando você tenta mudar tudo ao mesmo tempo, aumenta o número de variáveis e diminui a chance de entender o que realmente está funcionando.</p>
<p>Um recomeço mais claro começa definindo o que precisa terminar, o que merece permanecer e qual é o primeiro movimento que pode ser testado agora.</p>
<h2>1. Dê nome ao que você quer deixar para trás</h2>
<p>Evite frases amplas como “quero uma vida nova”. Escreva exatamente o que está pesado: uma rotina, um compromisso, um padrão de adiamento, uma relação com o trabalho ou uma meta que já perdeu sentido. Nomear reduz a névoa.</p>
<h2>2. Preserve o que ainda funciona</h2>
<p>Recomeço não exige destruir tudo. Liste recursos que continuam úteis: pessoas, habilidades, horários, hábitos, estabilidade financeira, conhecimento, espaço físico. O que já funciona pode ser a base do próximo ciclo.</p>
<h2>3. Escolha uma mudança que produza efeito em cadeia</h2>
<p>Algumas mudanças simplificam outras. Organizar o horário de dormir pode liberar manhãs melhores; reduzir um compromisso pode abrir espaço para estudo; definir uma prioridade pode eliminar várias tarefas concorrentes. Procure a alteração com maior efeito sobre o restante.</p>
<h2>4. Crie um experimento, não uma promessa eterna</h2>
<p>Teste uma nova configuração por sete ou quatorze dias. Defina o que observará e o que faria você manter, ajustar ou abandonar o experimento. Isso diminui o medo de escolher errado e aumenta a qualidade do aprendizado.</p>
<div class="guide-callout"><strong>Uma boa pergunta:</strong> “qual mudança pequena me daria informação nova sobre a direção que quero seguir?”</div>
<h2>5. Feche pendências que continuam puxando você para trás</h2>
<p>Alguns recomeços travam porque o ciclo anterior ainda exige atenção. Faça uma lista curta de pendências que precisam de encerramento: comunicar uma decisão, cancelar algo, devolver um objeto, organizar um documento ou concluir uma tarefa pequena.</p>
<h2>6. Defina um primeiro marco</h2>
<p>Um marco transforma intenção em referência concreta. Pode ser completar uma semana da nova rotina, enviar uma proposta, iniciar um curso, terminar uma etapa ou ter uma conversa importante. Escolha algo que possa ser reconhecido como concluído.</p>
<h2>Roteiro de recomeço</h2>
<ol class="guide-steps"><li>Nomeie o que precisa mudar.</li><li>Liste o que vale preservar.</li><li>Escolha uma mudança de alto efeito.</li><li>Transforme-a em experimento de curto prazo.</li><li>Feche uma pendência do ciclo anterior.</li><li>Defina o primeiro marco observável.</li></ol>
<p>Recomeçar com clareza não significa ter certeza. Significa criar movimento suficiente para que a próxima decisão seja tomada com mais informação do que a anterior.</p>
'''
    },
    {
        'slug': 'como-simplificar-uma-rotina-que-ficou-pesada',
        'title': 'Como simplificar uma rotina que ficou pesada demais',
        'short': 'Como simplificar uma rotina pesada',
        'description': 'Um método de revisão de responsabilidades, compromissos e prioridades para reduzir excesso e recuperar margem no cotidiano.',
        'kicker': 'Rotina e limites',
        'image': CANON + '/assets/covers/capa-o-metodo-da-vida-mais-leve.webp',
        'books': [('o-metodo-da-vida-mais-leve', 'O Método da Vida Mais Leve'), ('quando-sua-vida-virou-sobrevivencia', 'Quando Sua Vida Virou Sobrevivência'), ('o-peso-de-ser-forte-o-tempo-todo', 'O Peso de Ser Forte o Tempo Todo')],
        'keywords': ['rotina', 'sobrecarga', 'prioridades', 'limites', 'simplificar'],
        'body': '''
<p>Uma rotina pesada nem sempre precisa de mais produtividade. Às vezes precisa de menos coisas competindo pelo mesmo tempo. Antes de adicionar aplicativos, métodos ou metas, vale descobrir onde sua agenda está acumulando obrigações que já não têm o mesmo valor.</p>
<h2>1. Faça um inventário sem tentar resolver</h2>
<p>Durante alguns minutos, liste compromissos recorrentes, responsabilidades, tarefas domésticas, trabalho, deslocamentos e obrigações informais. Não organize ainda. O objetivo é enxergar o volume total que normalmente fica espalhado pela memória.</p>
<h2>2. Classifique por importância e consequência</h2>
<p>Marque cada item como essencial, importante, negociável ou dispensável. Depois observe as consequências reais de reduzir, delegar ou eliminar cada compromisso. Essa etapa ajuda a diferenciar urgência percebida de necessidade concreta.</p>
<h2>3. Identifique tarefas que existem por hábito</h2>
<p>Algumas atividades continuam na agenda porque sempre estiveram lá. Pergunte: se eu estivesse montando minha rotina hoje, escolheria incluir isso novamente? Se a resposta for não, existe um candidato à simplificação.</p>
<h2>4. Proteja margem</h2>
<p>Uma agenda ocupada até o limite transforma qualquer imprevisto em crise. Deixe espaços sem tarefa definida. Margem não é desperdício; é capacidade de absorver atrasos, descanso, decisões e acontecimentos que não cabem no planejamento.</p>
<div class="guide-callout"><strong>Sinal de alerta prático:</strong> se toda semana depende de nenhum imprevisto acontecer, o problema pode estar na quantidade de compromissos, não na sua capacidade de organização.</div>
<h2>5. Renegocie antes de abandonar</h2>
<p>Nem toda responsabilidade pode ser eliminada, mas algumas podem mudar de frequência, prazo, formato ou divisão. Uma conversa objetiva pode reduzir mais peso do que tentar executar tudo com maior velocidade.</p>
<h2>6. Escolha um critério para novos compromissos</h2>
<p>Uma rotina volta a ficar pesada quando todo espaço liberado é preenchido novamente. Defina uma pergunta antes de aceitar algo novo: isso apoia uma prioridade atual? O custo cabe na minha semana real? O que precisará sair para isso entrar?</p>
<h2>Revisão semanal de 15 minutos</h2>
<ol class="guide-steps"><li>Veja o que ocupou mais tempo do que deveria.</li><li>Escolha uma tarefa para eliminar, reduzir ou delegar.</li><li>Reserve pelo menos um bloco de margem.</li><li>Defina as três prioridades da próxima semana.</li><li>Recuse ou adie o que não cabe sem sacrificar essas prioridades.</li></ol>
<p>Se o cansaço ou a sensação de sobrecarga forem persistentes, intensos ou acompanhados de outros sintomas, vale procurar avaliação profissional. Este guia é editorial e prático; não substitui orientação de saúde.</p>
'''
    },
    {
        'slug': 'como-organizar-a-mente-quando-ha-excesso-de-estimulos',
        'title': 'Como organizar a mente quando há excesso de estímulos e pendências',
        'short': 'Como organizar a mente',
        'description': 'Um roteiro prático para tirar pendências da cabeça, reduzir entradas desnecessárias e recuperar clareza quando tudo parece pedir atenção ao mesmo tempo.',
        'kicker': 'Clareza mental',
        'image': CANON + '/assets/covers/capa-mente-forte-vida-leve.webp',
        'books': [('mente-forte-vida-leve', 'Mente Forte Vida Leve'), ('o-cansaco-invisivel', 'O Cansaço Invisível')],
        'keywords': ['clareza mental', 'estímulos', 'pendências', 'organização', 'atenção'],
        'body': '''
<p>Quando muitas coisas pedem atenção ao mesmo tempo, tentar “pensar melhor” pode não ser suficiente. Uma estratégia mais concreta é diminuir o volume que precisa ser mantido na memória e reduzir novas entradas enquanto você organiza o que já chegou.</p>
<h2>1. Tire as pendências da cabeça</h2>
<p>Abra uma folha ou nota e registre tudo que está competindo por atenção: tarefas, conversas, decisões, compras, ideias, preocupações práticas e coisas que você teme esquecer. Não resolva enquanto escreve. Primeiro capture.</p>
<h2>2. Separe ação de preocupação</h2>
<p>Para cada item, pergunte se existe uma ação concreta possível. “Resolver minha carreira” não é ação; “listar três opções e conversar com uma pessoa da área” é. Quando não houver ação possível agora, registre como assunto a revisar em uma data específica.</p>
<h2>3. Reduza entradas por um período</h2>
<p>Se você continua adicionando informação enquanto tenta organizar a mente, a fila nunca diminui. Reserve períodos sem redes sociais, notícias ou notificações não essenciais. A ideia não é se isolar, mas criar uma janela em que o volume pare de crescer.</p>
<h2>4. Escolha três frentes ativas</h2>
<p>Nem tudo precisa estar em andamento ao mesmo tempo. Defina até três frentes principais para a semana. Os demais itens podem ficar em espera consciente. Essa escolha reduz a sensação de que todas as pendências têm a mesma prioridade.</p>
<div class="guide-callout"><strong>Critério simples:</strong> se tudo é prioridade, você ainda não priorizou. Escolher também significa permitir que algumas coisas aguardem.</div>
<h2>5. Crie um ritual de fechamento do dia</h2>
<p>Antes de encerrar, registre o que ficou aberto, escolha a primeira tarefa do dia seguinte e feche os materiais que não serão usados. Isso diminui a necessidade de continuar “segurando” mentalmente o trabalho depois que ele terminou.</p>
<h2>6. Preserve períodos sem objetivo produtivo</h2>
<p>Clareza não nasce apenas de organizar tarefas. Também precisa de espaços em que você não esteja consumindo ou produzindo constantemente. Caminhar, conversar, ficar em silêncio ou fazer uma atividade simples pode funcionar como transição entre blocos intensos do dia.</p>
<h2>Protocolo de 25 minutos</h2>
<ol class="guide-steps"><li>Capture todas as pendências em uma lista.</li><li>Transforme itens vagos em próximas ações.</li><li>Escolha três frentes para a semana.</li><li>Agende ou arquive o restante.</li><li>Desative entradas não essenciais por uma hora.</li><li>Comece apenas a primeira ação da prioridade número um.</li></ol>
<p>Se confusão, exaustão ou sofrimento forem persistentes ou intensos, procure apoio profissional apropriado. O objetivo deste texto é oferecer organização prática, não fazer diagnóstico ou tratamento.</p>
'''
    },
]

GUIDE_BY_BOOK = {}
for g in GUIDES:
    for slug, title in g['books']:
        GUIDE_BY_BOOK.setdefault(slug, g)

GUIDE_CSS_TEXT = r'''/* Freedom Book editorial guides v1 — topical authority without search-engine-first pages */
.guide-hero{padding:42px 0 24px}.guide-hero .hero-panel{padding:clamp(24px,5vw,52px)}.guide-hero h1{font-size:clamp(2.2rem,5.4vw,4.55rem);max-width:930px}.guide-meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}.guide-meta span{border:1px solid var(--line);border-radius:999px;padding:6px 10px;color:#d6ccba;font-size:.8rem}.article-shell{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:30px;align-items:start}.article-body{min-width:0}.article-body>p,.article-body>ol,.article-body>ul{max-width:780px}.article-body p{color:#d7cfc1;font-size:1.02rem;line-height:1.78;margin:0 0 18px}.article-body h2{font-size:clamp(1.55rem,3vw,2.2rem);line-height:1.15;margin:40px 0 14px;scroll-margin-top:94px}.article-body ol,.article-body ul{color:#d7cfc1;line-height:1.72;padding-left:1.35rem}.article-body li{margin:8px 0}.guide-callout{max-width:780px;margin:24px 0;padding:18px 20px;border:1px solid var(--line2);border-radius:18px;background:rgba(240,199,104,.065);color:#efe4cf}.guide-steps{padding:18px 20px 18px 42px!important;border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.018)}.guide-aside{position:sticky;top:94px;display:grid;gap:14px}.guide-aside .card{padding:18px}.guide-aside h2,.guide-aside h3{font-family:Inter,sans-serif;letter-spacing:-.02em;margin:0 0 10px}.guide-aside p{color:var(--muted);font-size:.9rem;margin:0 0 12px}.guide-aside a:not(.btn){display:block;padding:8px 0;border-top:1px solid rgba(240,199,104,.08);font-size:.9rem;color:#e5dac7}.guide-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.guide-card{padding:22px;display:flex;flex-direction:column;min-height:250px}.guide-card h2,.guide-card h3{font-size:1.3rem;line-height:1.15;margin:12px 0 9px}.guide-card p{color:var(--muted);margin:0 0 16px}.guide-card .btn{margin-top:auto}.guide-related{padding:22px}.guide-related h2{font-size:clamp(1.45rem,2.8vw,2rem);margin:10px 0}.guide-related p{color:var(--muted)}.guide-note{font-size:.88rem;color:#aaa195}.guide-breadcrumbs{padding-top:20px}.guide-breadcrumbs a{color:#d7c99f}.guide-index-intro{max-width:820px}.guide-book-links{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.guide-book-links a{border:1px solid var(--line);border-radius:999px;padding:7px 11px;color:#eadcae;font-size:.82rem;font-weight:750}
@media(max-width:900px){.article-shell{grid-template-columns:1fr}.guide-aside{position:static;grid-template-columns:1fr 1fr}.guide-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:620px){.guide-hero{padding-top:24px}.guide-hero .hero-panel{border-radius:22px}.guide-hero h1{font-size:clamp(2rem,11vw,3.2rem)}.article-body p{font-size:.98rem}.guide-aside{grid-template-columns:1fr}.guide-grid{grid-template-columns:1fr}.guide-card{min-height:0}}
'''


def write(path: str | Path, text: str) -> None:
    p = ROOT / path if isinstance(path, str) else path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def compact_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def replace_jsonld(text: str, payload: dict) -> str:
    repl = '<script type="application/ld+json">' + compact_json(payload) + '</script>'
    out, count = re.subn(r'<script\s+type="application/ld\+json">.*?</script>', repl, text, count=1, flags=re.S | re.I)
    if count != 1:
        raise SystemExit('expected exactly one JSON-LD block')
    return out


def add_nav_guides(text: str) -> str:
    if 'href="/guias">Guias</a>' not in text:
        text = text.replace('<a href="/#manifesto">Manifesto</a>', '<a href="/guias">Guias</a><a href="/#manifesto">Manifesto</a>')
    if '<a href="/guias">Guias</a>' not in text.split('<footer', 1)[-1]:
        text = text.replace('<a href="/#catalogo">E-books</a>', '<a href="/#catalogo">E-books</a><a href="/guias">Guias</a>')
    return text


def meta_replace(text: str, tag: str, value: str, *, attr: str = 'name') -> str:
    pattern = rf'(<meta\s+[^>]*{attr}="{re.escape(tag)}"[^>]*content=")[^"]*("[^>]*>)'
    out, count = re.subn(pattern, lambda m: m.group(1) + html.escape(value, quote=True) + m.group(2), text, count=1, flags=re.I)
    if count == 0:
        pattern = rf'(<meta\s+content=")[^"]*("\s+{attr}="{re.escape(tag)}"[^>]*>)'
        out, count = re.subn(pattern, lambda m: m.group(1) + html.escape(value, quote=True) + m.group(2), text, count=1, flags=re.I)
    return out


def page_base() -> str:
    return (ROOT / 'autor-arthur-magnus.html').read_text(encoding='utf-8')


def common_head(base: str, title: str, description: str, canonical: str, image: str, og_type: str) -> str:
    text = re.sub(r'<title>.*?</title>', f'<title>{html.escape(title)}</title>', base, count=1, flags=re.S)
    text = meta_replace(text, 'description', description)
    text = meta_replace(text, 'robots', 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1')
    text = re.sub(r'<link\s+rel="canonical"\s+href="[^"]+"\s*/?>|<link\s+href="[^"]+"\s+rel="canonical"\s*/?>', f'<link rel="canonical" href="{canonical}"/>', text, count=1, flags=re.I)
    text = meta_replace(text, 'og:type', og_type, attr='property')
    text = meta_replace(text, 'og:title', title, attr='property')
    text = meta_replace(text, 'og:description', description, attr='property')
    text = meta_replace(text, 'og:url', canonical, attr='property')
    text = meta_replace(text, 'og:image', image, attr='property')
    text = meta_replace(text, 'og:image:alt', title, attr='property')
    text = meta_replace(text, 'twitter:title', title)
    text = meta_replace(text, 'twitter:description', description)
    text = meta_replace(text, 'twitter:image', image)
    if GUIDE_CSS not in text:
        text = text.replace('<link href="/assets/cover-integrity.v1.css" rel="stylesheet"/>', '<link href="/assets/cover-integrity.v1.css" rel="stylesheet"/><link href="' + GUIDE_CSS + '" rel="stylesheet"/>')
    text = add_nav_guides(text)
    return text


def org_nodes() -> list[dict]:
    return [
        {'@type': 'Organization', '@id': CANON + '/#organization', 'name': 'Freedom Book', 'url': CANON + '/', 'logo': {'@type': 'ImageObject', 'url': CANON + '/assets/covers/logo-freedom-book-redonda.webp'}},
        {'@type': 'WebSite', '@id': CANON + '/#website', 'name': 'Freedom Book', 'url': CANON + '/', 'publisher': {'@id': CANON + '/#organization'}, 'inLanguage': 'pt-BR'},
    ]


def guide_graph(g: dict) -> dict:
    url = CANON + '/guias/' + g['slug']
    crumbs = {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Freedom Book', 'item': CANON + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Guias', 'item': CANON + '/guias'},
        {'@type': 'ListItem', 'position': 3, 'name': g['short'], 'item': url},
    ]}
    article = {'@type': 'Article', '@id': url + '#article', 'url': url, 'headline': g['title'], 'description': g['description'], 'image': [g['image']], 'datePublished': DATE, 'dateModified': DATE, 'inLanguage': 'pt-BR', 'author': {'@id': CANON + '/#organization'}, 'publisher': {'@id': CANON + '/#organization'}, 'isPartOf': {'@id': CANON + '/#website'}, 'mainEntityOfPage': {'@id': url + '#webpage'}, 'keywords': ', '.join(g['keywords'])}
    webpage = {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': g['title'], 'description': g['description'], 'dateModified': DATE, 'inLanguage': 'pt-BR', 'isPartOf': {'@id': CANON + '/#website'}, 'breadcrumb': {'@id': url + '#breadcrumb'}, 'mainEntity': {'@id': url + '#article'}}
    return {'@context': 'https://schema.org', '@graph': org_nodes() + [crumbs, webpage, article]}


def guide_main(g: dict) -> str:
    toc = ''.join(f'<a href="#sec-{i}">{html.escape(m.group(1))}</a>' for i, m in enumerate(re.finditer(r'<h2>(.*?)</h2>', g['body']), start=1))
    body = g['body']
    n = 0
    def add_id(m):
        nonlocal n
        n += 1
        return f'<h2 id="sec-{n}">{m.group(1)}</h2>'
    body = re.sub(r'<h2>(.*?)</h2>', add_id, body)
    book_links = ''.join(f'<a href="/{slug}">{html.escape(title)}</a>' for slug, title in g['books'])
    related_cards = ''.join(f'<a class="btn secondary" href="/{slug}">Conhecer {html.escape(title)}</a>' for slug, title in g['books'])
    return f'''<main id="conteudo"><div class="container crumbs guide-breadcrumbs"><a href="/">Freedom Book</a> / <a href="/guias">Guias</a> / {html.escape(g['short'])}</div>
<section class="guide-hero"><div class="container"><div class="hero-panel"><div class="hero-copy"><span class="kicker">{html.escape(g['kicker'])}</span><h1>{html.escape(g['title'])}</h1><p class="lead">{html.escape(g['description'])}</p><div class="guide-meta"><span>Guia editorial da Freedom Book</span><span>Atualizado em 9 de setembro de 2026</span><span>Leitura prática</span></div></div></div></div></section>
<section class="section"><div class="container article-shell"><article class="article-body">{body}
<section class="card guide-related"><span class="kicker">Leitura complementar</span><h2>Continue aprofundando este tema</h2><p>Os e-books abaixo fazem parte do catálogo gratuito da Freedom Book e se conectam diretamente ao assunto deste guia.</p><div class="hero-actions">{related_cards}</div></section>
<p class="guide-note">Conteúdo editorial e educativo. Quando um tema envolver saúde, sofrimento persistente ou decisões profissionais específicas, procure orientação qualificada apropriada ao seu caso.</p></article>
<aside class="guide-aside" aria-label="Navegação e leituras relacionadas"><div class="card"><h2>Neste guia</h2>{toc}</div><div class="card"><h3>E-books relacionados</h3><p>Leituras gratuitas em PDF conectadas a este tema.</p><div class="guide-book-links">{book_links}</div></div><div class="card"><h3>Explore outros temas</h3><p>Use a biblioteca de guias para continuar por foco, propósito, disciplina, recomeços e vida prática.</p><a class="btn secondary" href="/guias">Ver todos os guias</a></div></aside></div></section></main>'''


def build_guide_page(g: dict) -> str:
    title = g['title'] + ' | Freedom Book'
    canonical = CANON + '/guias/' + g['slug']
    text = common_head(page_base(), title, g['description'], canonical, g['image'], 'article')
    text = replace_jsonld(text, guide_graph(g))
    text = re.sub(r'<body\s+data-page-type="author">', '<body data-page-type="guide">', text, count=1)
    text, count = re.subn(r'<main id="conteudo">.*?</main>', guide_main(g), text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit('could not replace author main for guide')
    return text


def hub_graph() -> dict:
    url = CANON + '/guias'
    items = [{'@type': 'ListItem', 'position': i, 'url': CANON + '/guias/' + g['slug'], 'name': g['title']} for i, g in enumerate(GUIDES, 1)]
    return {'@context': 'https://schema.org', '@graph': org_nodes() + [
        {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Freedom Book', 'item': CANON + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Guias', 'item': url},
        ]},
        {'@type': ['WebPage', 'CollectionPage'], '@id': url + '#webpage', 'url': url, 'name': 'Guias práticos da Freedom Book', 'description': 'Guias editoriais sobre propósito, foco, disciplina, recomeços, clareza mental e vida prática.', 'dateModified': DATE, 'inLanguage': 'pt-BR', 'isPartOf': {'@id': CANON + '/#website'}, 'breadcrumb': {'@id': url + '#breadcrumb'}},
        {'@type': 'ItemList', '@id': url + '#lista', 'name': 'Guias práticos da Freedom Book', 'numberOfItems': len(items), 'itemListElement': items},
    ]}


def hub_main() -> str:
    cards = []
    for g in GUIDES:
        links = ''.join(f'<a href="/{slug}">{html.escape(title)}</a>' for slug, title in g['books'])
        cards.append(f'''<article class="card guide-card"><span class="kicker">{html.escape(g['kicker'])}</span><h2><a href="/guias/{g['slug']}">{html.escape(g['short'])}</a></h2><p>{html.escape(g['description'])}</p><div class="guide-book-links">{links}</div><a class="btn secondary" href="/guias/{g['slug']}">Ler guia</a></article>''')
    return f'''<main id="conteudo"><div class="container crumbs guide-breadcrumbs"><a href="/">Freedom Book</a> / Guias</div><section class="guide-hero"><div class="container"><div class="hero-panel"><div class="hero-copy guide-index-intro"><span class="kicker">Biblioteca de guias</span><h1>Guias práticos para foco, propósito, disciplina e recomeços</h1><p class="lead">Conteúdo editorial para transformar temas dos e-books da Freedom Book em perguntas, exercícios e próximos passos que você pode aplicar no cotidiano.</p><div class="guide-meta"><span>6 guias originais</span><span>Leitura gratuita</span><span>Sem cadastro</span></div></div></div></div></section><section class="section"><div class="container"><div class="section-head"><span class="kicker">Escolha por tema</span><h2>Comece pela pergunta que mais se parece com seu momento</h2><p>Os guias não substituem os e-books: eles funcionam como portas de entrada práticas para os mesmos temas editoriais.</p></div><div class="grid guide-grid">{''.join(cards)}</div></div></section></main>'''


def build_hub() -> str:
    title = 'Guias de propósito, foco, disciplina e recomeços | Freedom Book'
    description = 'Guias práticos e gratuitos da Freedom Book sobre propósito, foco, disciplina, recomeços, clareza mental e organização da rotina.'
    text = common_head(page_base(), title, description, CANON + '/guias', CANON + '/og/freedom-book-home.png', 'website')
    text = replace_jsonld(text, hub_graph())
    text = re.sub(r'<body\s+data-page-type="author">', '<body data-page-type="guides">', text, count=1)
    text, count = re.subn(r'<main id="conteudo">.*?</main>', hub_main(), text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit('could not replace author main for guides hub')
    return text


def home_section() -> str:
    cards = ''.join(f'<a class="card manifesto-card" href="/guias/{g["slug"]}"><span class="kicker">{html.escape(g["kicker"])}</span><h3>{html.escape(g["short"])}</h3><p>{html.escape(g["description"])}</p></a>' for g in GUIDES)
    return f'''<!-- topical-guides-v2:start --><section class="section alt" id="guias"><div class="container"><div class="section-head"><span class="kicker">Guias práticos</span><h2>Transforme uma pergunta em um próximo passo.</h2><p>Além dos e-books, a Freedom Book agora reúne guias originais para aprofundar os mesmos temas com exercícios e decisões práticas.</p></div><div class="grid manifesto-grid">{cards}</div><div class="hero-actions"><a class="btn secondary" href="/guias">Ver biblioteca de guias</a></div></div></section><!-- topical-guides-v2:end -->'''


def add_home_guides() -> None:
    path = ROOT / 'index.html'
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'<!-- topical-guides-v2:start -->.*?<!-- topical-guides-v2:end -->', '', text, flags=re.S)
    if '<section class="section" id="manifesto">' not in text:
        raise SystemExit('home manifesto insertion point missing')
    text = text.replace('<section class="section" id="manifesto">', home_section() + '<section class="section" id="manifesto">', 1)
    text = add_nav_guides(text)
    ld_match = re.search(r'<script\s+type="application/ld\+json">(.*?)</script>', text, re.S | re.I)
    payload = json.loads(ld_match.group(1))
    graph = payload.get('@graph', [])
    graph = [n for n in graph if n.get('@id') != CANON + '/#guias']
    graph.append({'@type': 'ItemList', '@id': CANON + '/#guias', 'name': 'Guias práticos Freedom Book', 'numberOfItems': len(GUIDES), 'itemListElement': [{'@type': 'ListItem', 'position': i, 'url': CANON + '/guias/' + g['slug'], 'name': g['title']} for i, g in enumerate(GUIDES, 1)]})
    payload['@graph'] = graph
    text = replace_jsonld(text, payload)
    write(path, text)


def add_author_guides() -> None:
    path = ROOT / 'autor-arthur-magnus.html'
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'<!-- topical-author-guides-v2:start -->.*?<!-- topical-author-guides-v2:end -->', '', text, flags=re.S)
    cards = ''.join(f'<a class="card manifesto-card" href="/guias/{g["slug"]}"><span class="kicker">{html.escape(g["kicker"])}</span><h3>{html.escape(g["short"])}</h3><p>{html.escape(g["description"])}</p></a>' for g in GUIDES[:4])
    sec = f'''<!-- topical-author-guides-v2:start --><section class="section"><div class="container"><div class="section-head"><span class="kicker">Guias editoriais</span><h2>Continue pelos temas da biblioteca</h2><p>Guias práticos da Freedom Book conectam perguntas do cotidiano às leituras publicadas no catálogo.</p></div><div class="grid manifesto-grid">{cards}</div><div class="hero-actions"><a class="btn secondary" href="/guias">Ver todos os guias</a></div></div></section><!-- topical-author-guides-v2:end -->'''
    text = text.replace('</main>', sec + '</main>', 1)
    text = add_nav_guides(text)
    write(path, text)


def add_book_links() -> None:
    for book_slug, g in GUIDE_BY_BOOK.items():
        path = ROOT / f'{book_slug}.html'
        text = path.read_text(encoding='utf-8')
        text = re.sub(r'<!-- topical-book-guide-v2:start -->.*?<!-- topical-book-guide-v2:end -->', '', text, flags=re.S)
        block = f'''<!-- topical-book-guide-v2:start --><section class="section"><div class="container"><div class="card channel"><div><span class="kicker">Guia complementar</span><h3>{html.escape(g['short'])}</h3><p>{html.escape(g['description'])}</p></div><a class="btn secondary" href="/guias/{g['slug']}">Ler guia prático</a></div></div></section><!-- topical-book-guide-v2:end -->'''
        text = text.replace('</main>', block + '</main>', 1)
        text = add_nav_guides(text)
        write(path, text)


def update_site_data() -> None:
    path = ROOT / 'site-data.generated.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    data['site']['modified'] = DATE
    data['guides'] = [
        {'slug': g['slug'], 'title': g['title'], 'shortTitle': g['short'], 'url': CANON + '/guias/' + g['slug'], 'description': g['description'], 'image': g['image'], 'relatedBooks': [s for s, _ in g['books']], 'keywords': g['keywords']}
        for g in GUIDES
    ]
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def update_sitemap() -> None:
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    ET.register_namespace('image', 'http://www.google.com/schemas/sitemap-image/1.1')
    path = ROOT / 'sitemap.xml'
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    for node in list(root):
        loc = node.find('s:loc', ns)
        if loc is not None and loc.text and (loc.text.strip() == CANON + '/guias' or loc.text.strip().startswith(CANON + '/guias/')):
            root.remove(node)
    S = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    I = '{http://www.google.com/schemas/sitemap-image/1.1}'
    entries = [(CANON + '/guias', CANON + '/assets/covers/logo-freedom-book-redonda.webp', 'Guias práticos Freedom Book')]
    entries += [(CANON + '/guias/' + g['slug'], g['image'], g['title']) for g in GUIDES]
    for url, image_url, image_title in entries:
        node = ET.SubElement(root, S + 'url')
        ET.SubElement(node, S + 'loc').text = url
        ET.SubElement(node, S + 'lastmod').text = DATE
        image = ET.SubElement(node, I + 'image')
        ET.SubElement(image, I + 'loc').text = image_url
        ET.SubElement(image, I + 'title').text = image_title
    tree.write(path, encoding='utf-8', xml_declaration=True)


def update_route_generator() -> None:
    path = ROOT / 'scripts/generate-route-shims.py'
    text = path.read_text(encoding='utf-8')
    for route in ['/guias'] + ['/guias/' + g['slug'] for g in GUIDES]:
        token = f"    '{route}',\n"
        if token not in text:
            anchor = "CANONICAL_PATHS = (\n"
            text = text.replace(anchor, anchor + token, 1)
    write(path, text)


def update_validate_seo() -> None:
    path = ROOT / 'scripts/validate_seo.py'
    text = path.read_text(encoding='utf-8')
    if "guides = data.get('guides', [])" not in text:
        text = text.replace("available = [b for b in data.get('books', []) if b.get('available')]\n", "available = [b for b in data.get('books', []) if b.get('available')]\nguides = data.get('guides', [])\nif len(guides) != 6:\n    fail(f'expected 6 editorial guides, got {len(guides)}')\n")
    text = re.sub(r"expected = \{CANON \+ '/', CANON \+ '/autor-arthur-magnus'\} \| \{b\['pageUrl'\] for b in available\}", "expected = {CANON + '/', CANON + '/autor-arthur-magnus', CANON + '/guias'} | {b['pageUrl'] for b in available} | {g['url'] for g in guides}", text)
    marker = "# Sitemap must contain only indexable canonical editorial pages and accurate lastmod values.\n"
    if '# Editorial guide authority.' not in text:
        guide_check = '''# Editorial guide authority.\nfor g in guides:\n    page = ROOT / 'guias' / f"{g['slug']}.html"\n    text = page.read_text(encoding='utf-8')\n    if f'<link rel="canonical" href="{g["url"]}"' not in text:\n        fail(f"{g['slug']}: guide canonical drift")\n    if 'name="robots" content="index,follow' not in text and 'content="index,follow' not in text:\n        fail(f"{g['slug']}: guide is not indexable")\n    ld = jsonld(page); nodes = ld.get('@graph', []) if isinstance(ld, dict) else []\n    article = next((n for n in nodes if n.get('@type') == 'Article'), None)\n    crumbs = next((n for n in nodes if n.get('@type') == 'BreadcrumbList'), None)\n    if not article or not crumbs:\n        fail(f"{g['slug']}: Article/BreadcrumbList missing")\n    if article.get('author', {}).get('@id') != CANON + '/#organization' or article.get('publisher', {}).get('@id') != CANON + '/#organization':\n        fail(f"{g['slug']}: guide authorship/publisher drift")\n    if article.get('datePublished') != modified or article.get('dateModified') != modified:\n        fail(f"{g['slug']}: guide dates drift")\n    for bslug in g.get('relatedBooks', []):\n        if f'href="/{bslug}"' not in text:\n            fail(f"{g['slug']}: related book link missing: {bslug}")\n\nhub = (ROOT / 'guias.html').read_text(encoding='utf-8')\nif hub.count('class="card guide-card"') != 6:\n    fail('guides hub must expose six guide cards in initial HTML')\nfor g in guides:\n    if f'href="/guias/{g["slug"]}"' not in hub or f'href="/guias/{g["slug"]}"' not in home:\n        fail(f"{g['slug']}: internal discovery link missing from hub/home")\n\n'''
        text = text.replace(marker, guide_check + marker)
    write(path, text)


def update_validate_site() -> None:
    path = ROOT / 'scripts/validate_site.py'
    text = path.read_text(encoding='utf-8')
    guide_html = ["'guias.html'"] + [f"'guias/{g['slug']}.html'" for g in GUIDES]
    if "'guias.html'" not in text:
        text = text.replace(" 'quando-sua-vida-virou-sobrevivencia.html','recomecos-sao-escolhas.html','termos.html'\n}", " 'quando-sua-vida-virou-sobrevivencia.html','recomecos-sao-escolhas.html','termos.html',\n " + ','.join(guide_html) + "\n}")
    if "guides=data.get('guides',[])" not in text:
        text = text.replace("available=[b for b in books if b.get('available')]\n", "available=[b for b in books if b.get('available')]\nguides=data.get('guides',[])\nif len(guides)!=6:fail(f'expected 6 editorial guides, got {len(guides)}')\n")
    text = re.sub(r"expected=\{CANON\+'/',CANON\+'/autor-arthur-magnus'\}\|\{b\['pageUrl'\] for b in available\}", "expected={CANON+'/',CANON+'/autor-arthur-magnus',CANON+'/guias'}|{b['pageUrl'] for b in available}|{g['url'] for g in guides}", text)
    text = text.replace("if 'href=\"/autor-arthur-magnus\"' not in home:fail('author internal discovery link missing')", "if 'href=\"/autor-arthur-magnus\"' not in home:fail('author internal discovery link missing')\nif 'href=\"/guias\"' not in home:fail('guides internal discovery link missing')")
    text = re.sub(r"expected_maintenance=\{'schema':'achadostube-maintenance-marker-v1','campaign':'[^']+','version':\d+,'source':'main','origin':CANON\+'/'\}", "expected_maintenance={'schema':'achadostube-maintenance-marker-v1','campaign':'topical-authority-v2','version':2,'source':'main','origin':CANON+'/'}", text)
    write(path, text)


def write_guide_validator() -> None:
    text = r'''#!/usr/bin/env python3
from __future__ import annotations
import json,re
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CANON='https://achadostube.com.br'
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,d):self.parts.append(d)
def fail(m):raise SystemExit(m)
data=json.loads((ROOT/'site-data.generated.json').read_text('utf-8'));guides=data.get('guides',[])
if len(guides)!=6:fail(f'guide count {len(guides)} != 6')
for g in guides:
    p=ROOT/'guias'/f"{g['slug']}.html"; t=p.read_text('utf-8'); x=Text();x.feed(t); words=re.findall(r"[A-Za-zÀ-ÿ0-9]+",' '.join(x.parts))
    if len(words)<430:fail(f"{g['slug']}: thin guide ({len(words)} visible words)")
    if t.count('<h1')!=1:fail(f"{g['slug']}: h1 contract")
    if t.count('<h2')<5:fail(f"{g['slug']}: insufficient section depth")
    if 'Guia editorial da Freedom Book' not in t:fail(f"{g['slug']}: editorial provenance missing")
    for bad in ('garantia de resultado','ranking garantido','cura garantida','diagnóstico','segredo que ninguém conta'):
        if bad in t.lower():fail(f"{g['slug']}: manipulative/unsafe claim: {bad}")
    for b in g.get('relatedBooks',[]):
        bt=(ROOT/f'{b}.html').read_text('utf-8')
        if f'href="/guias/{g["slug"]}"' not in bt:fail(f"{b}: reciprocal topical link missing")
hub=(ROOT/'guias.html').read_text('utf-8')
if hub.count('class="card guide-card"')!=6:fail('hub guide count')
if '/assets/editorial-guides.v1.css' not in hub:fail('hub guide stylesheet missing')
print('PASS: six substantial people-first guide pages, reciprocal book links and topical hub are coherent')
'''
    write('scripts/validate_guides.py', text)


def update_workflows() -> None:
    site = ROOT / '.github/workflows/site-integrity.yml'
    text = site.read_text(encoding='utf-8')
    if 'assets/editorial-guides.v1.css' not in text.split('required=(',1)[1].split(')',1)[0]:
        text = text.replace('assets/cover-integrity.v1.css', 'assets/cover-integrity.v1.css assets/editorial-guides.v1.css') if 'assets/cover-integrity.v1.css' in text.split('required=(',1)[1].split(')',1)[0] else text.replace('assets/style.v2.2.5.css', 'assets/style.v2.2.5.css assets/editorial-guides.v1.css')
    if 'scripts/validate_guides.py' not in text.split('required=(',1)[1].split(')',1)[0]:
        text = text.replace('scripts/validate_seo.py', 'scripts/validate_seo.py scripts/validate_guides.py')
    if 'Validate topical authority guides' not in text:
        text = text.replace('      - name: Validate JavaScript syntax\n', '      - name: Validate topical authority guides\n        run: python3 scripts/validate_guides.py\n\n      - name: Validate JavaScript syntax\n')
    if "Path('assets/editorial-guides.v1.css')" not in text:
        text = text.replace("Path('assets/style.v2.2.5.css'):40*1024,", "Path('assets/style.v2.2.5.css'):40*1024,\n              Path('assets/editorial-guides.v1.css'):16*1024,")
    text = text.replace("for path in Path('.').glob('*.html'):", "for path in Path('.').rglob('*.html'):")
    write(site, text)

    smoke = ROOT / '.github/workflows/production-smoke.yml'
    text = smoke.read_text(encoding='utf-8')
    text = text.replace("test \"$(grep -o '<lastmod>2026-09-09</lastmod>' /tmp/seo-sitemap.xml | wc -l)\" -eq 12", "test \"$(grep -o '<lastmod>2026-09-09</lastmod>' /tmp/seo-sitemap.xml | wc -l)\" -eq 19")
    if 'Verify topical authority guides in production' not in text:
        step = '''      - name: Verify topical authority guides in production\n        shell: bash\n        run: |\n          set -euo pipefail\n          base="https://achadostube.com.br"\n          paths=(\n            /guias\n            /guias/como-encontrar-proposito-na-vida\n            /guias/como-melhorar-o-foco-e-reduzir-distracoes\n            /guias/como-criar-disciplina-sem-depender-de-motivacao\n            /guias/como-recomecar-com-mais-clareza\n            /guias/como-simplificar-uma-rotina-que-ficou-pesada\n            /guias/como-organizar-a-mente-quando-ha-excesso-de-estimulos\n          )\n          for path in "${paths[@]}"; do\n            curl --fail --silent --show-error --location "$base$path?probe=$GITHUB_SHA" -o /tmp/guide.html\n            grep -q 'name="robots" content="index,follow' /tmp/guide.html || grep -q 'content="index,follow' /tmp/guide.html\n            grep -q 'rel="canonical"' /tmp/guide.html\n            grep -q '/assets/editorial-guides.v1.css' /tmp/guide.html\n          done\n          curl --fail --silent --show-error --location "$base/guias/como-melhorar-o-foco-e-reduzir-distracoes?probe=$GITHUB_SHA" -o /tmp/article.html\n          grep -q '\"@type\":\"Article\"' /tmp/article.html\n          grep -q '\"author\":{\"@id\":\"https://achadostube.com.br/#organization\"}' /tmp/article.html\n          grep -q 'href="/foco-que-gera-resultados"' /tmp/article.html\n\n'''
        text = text.replace('      - name: Verify hardened legacy public surfaces\n', step + '      - name: Verify hardened legacy public surfaces\n')
    write(smoke, text)


def update_readme() -> None:
    path = ROOT / 'README.md'
    text = path.read_text(encoding='utf-8')
    marker = '## Autoridade temática e guias\n'
    if marker not in text:
        text += '''\n\n## Autoridade temática e guias\n\nA Freedom Book mantém uma biblioteca editorial de guias em `/guias`, conectada aos 10 e-books publicados. A estratégia prioriza poucas páginas substanciais e navegáveis, com utilidade própria, links recíprocos com os livros, `Article`/`BreadcrumbList`, sitemap e validação anti-conteúdo-fino. O objetivo é ampliar descoberta por intenções não-branded sem criar doorway pages, keyword stuffing ou conteúdo em escala.\n'''
    write(path, text)


def update_release_surface() -> None:
    path = ROOT / 'release.json'
    release = json.loads(path.read_text(encoding='utf-8'))
    art = release.setdefault('artifacts', {})
    for rel in ['guias.html', 'assets/editorial-guides.v1.css'] + [f"guias/{g['slug']}.html" for g in GUIDES]:
        art.setdefault(rel, '')
    write(path, json.dumps(release, ensure_ascii=False, indent=2, sort_keys=True) + '\n')


def update_marker() -> None:
    marker = {'schema': 'achadostube-maintenance-marker-v1', 'campaign': 'topical-authority-v2', 'version': 2, 'source': 'main', 'origin': CANON + '/'}
    write('maintenance-marker.json', json.dumps(marker, ensure_ascii=False, indent=2) + '\n')


write('assets/editorial-guides.v1.css', GUIDE_CSS_TEXT)
for g in GUIDES:
    write(Path('guias') / f"{g['slug']}.html", build_guide_page(g))
write('guias.html', build_hub())
add_home_guides()
add_author_guides()
add_book_links()
update_site_data()
update_sitemap()
update_route_generator()
update_validate_seo()
update_validate_site()
write_guide_validator()
update_workflows()
update_readme()
update_marker()
update_release_surface()
subprocess.run(['python3', 'scripts/generate-route-shims.py'], cwd=ROOT, check=True)
subprocess.run(['python3', 'scripts/refresh_release.py'], cwd=ROOT, check=True)
subprocess.run(['python3', 'scripts/validate_site.py'], cwd=ROOT, check=True)
subprocess.run(['python3', 'scripts/validate_seo.py'], cwd=ROOT, check=True)
subprocess.run(['python3', 'scripts/validate_guides.py'], cwd=ROOT, check=True)
subprocess.run(['python3', 'scripts/generate-route-shims.py', '--check'], cwd=ROOT, check=True)
print('Topical authority v2 build complete: hub + 6 substantial guides + reciprocal clusters + hardened CI')
