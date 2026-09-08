# Incident response

Se uma publicação causar regressão:

1. identificar o PR/commit responsável;
2. reverter a alteração em nova branch;
3. abrir PR de rollback;
4. exigir `Site integrity / validate` com sucesso;
5. integrar o rollback;
6. registrar a causa no histórico do PR/commit.

Para incidentes críticos de domínio, home ou downloads, priorizar restauração funcional antes de novas melhorias.
