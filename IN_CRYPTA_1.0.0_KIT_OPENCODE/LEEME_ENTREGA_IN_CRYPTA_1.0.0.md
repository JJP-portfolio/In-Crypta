# Kit de integración IN CRYPTA 1.0.0

Incluye:
- `PROMPT_MAESTRO_IN_CRYPTA_1.0.0.md`: instrucciones operativas para el orquestador y los subagentes de OpenCode CLI.
- `PLAN_INTEGRACION_IN_CRYPTA_1.0.0.xml`: plan estructurado XML con riesgos, agentes, fases, tareas, gates y criterios de aceptación.

## Uso sugerido

1. Clonar/localizar ambos repositorios originales en Linux.
2. Copiar estos dos archivos a la raíz del workspace o a `docs/integration/`.
3. Abrir OpenCode CLI desde la raíz del workspace.
4. Pegar el prompt maestro como instrucción inicial.
5. Pedir al orquestador que lea y siga el XML desde `P00`, sin saltar el inventario ni el baseline.
6. Revisar los gates antes de permitir cambios destructivos o publicación.

El kit no contiene los repositorios fusionados ni afirma que el juego ya haya sido modificado. Es el plan ejecutable de integración para que el agente trabaje sobre los repositorios reales.
