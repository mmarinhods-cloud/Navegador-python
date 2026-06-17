# Tarefa: Refatoração Completa do Sistema de Janela do Navegador PyQt6

Analise todo o projeto e implemente as melhorias abaixo SEM quebrar funcionalidades existentes.

## Regras obrigatórias

* Não quebrar a animação da barra de pesquisa.
* Não quebrar sistema de abas.
* Não quebrar favoritos.
* Não quebrar dark mode.
* Não quebrar sistema de temas.
* Não quebrar navegação do QWebEngine.
* Preservar aparência atual.

---

# 1. Corrigir maximização inicial

Problema atual:

Ao abrir maximizado utilizando showMaximized(), a janela ainda apresenta cantos arredondados e margens invisíveis como se estivesse em modo janela.

Após restaurar e maximizar novamente o problema desaparece.

Implementar correção definitiva.

Objetivo:

* Abrir maximizado já na geometria correta.
* Sem espaços nos cantos.
* Sem margens fantasmas.
* Sem necessidade de restaurar e maximizar novamente.

Investigar conflitos entre:

* FramelessWindowHint
* WA_TranslucentBackground
* Border Radius
* Margens do Central Layout

Criar solução robusta para Windows.

---

# 2. Restaurar comportamento semelhante ao Firefox

Implementar:

Ao iniciar:

* abrir maximizado

Ao restaurar pela primeira vez:

* centralizar na tela

Após isso:

* sempre restaurar para a última posição usada pelo usuário

Igual Firefox.

Persistir:

* posição
* largura
* altura

durante a sessão.

---

# 3. Corrigir redimensionamento

Problema atual:

O resize não funciona livremente.

Criar sistema semelhante ao Firefox:

* resize pelas 4 bordas
* resize pelos 4 cantos
* resize suave
* sem travamentos

Separar corretamente:

* área de mover janela
* área de resize

Evitar conflitos entre drag e resize.

---

# 4. Sombra leve sem perda de desempenho

Problema atual:

QGraphicsDropShadowEffect gera lag.

Investigar solução profissional.

Prioridade:

1. Sombra nativa DWM do Windows.
2. Mica/Acrylic quando disponível.
3. Fallback extremamente leve.

Objetivo:

Visual semelhante a:

* Firefox
* Edge
* Safari

Sem perda perceptível de FPS.

---

# 5. Melhorar sistema de maximizar/restaurar

Garantir:

* animação suave
* geometria correta
* sem flickering
* sem reposicionamentos errados

Implementar armazenamento da geometria anterior.

---

# 6. Otimizações de performance

Analisar todo o projeto.

Identificar:

* chamadas desnecessárias
* layouts recalculados em excesso
* repaints excessivos
* operações repetidas

Implementar otimizações sem alterar comportamento.

---

# 7. Resize Event

Evitar execução excessiva de:

* recalculate_tab_sizes()
* adjust_plus_button_position()

Aplicar debounce ou estratégia equivalente.

Objetivo:

Resize extremamente fluido.

---

# 8. Código final

Entregar:

* código completo atualizado
* arquivos modificados completos
* comentários explicando alterações críticas
* nenhuma funcionalidade removida

Prioridade máxima:

Estabilidade > Performance > Aparência.
