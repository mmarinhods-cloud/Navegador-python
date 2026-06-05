# Matheus Browser (v2)

Seja bem-vindo ao **Matheus Browser**, um navegador web, minimalista e customizável. Este projeto nasceu logo após a finalização de uma imersão em Inteligência Artificial, usei o gemini uma IA gratuita para ver ate onde ia, foi aplicado conceitos de arquitetura de software, lógica de interface e automação para criar um ambiente de navegação fluido, seguro e com visual moderno inspirado no Firefox.

O navegador conta com uma interface *Frameless* (sem as bordas padrão do sistema operacional) para garantir máxima imersão visual, além de gerenciar cantos arredondados dinâmicos e sombras projetadas em alta definição.

---

## Funcionalidades Principais

* **Temas Dinâmicos (Light & Dark Mode):** Troca completa de interface em tempo real com suporte a *Force Dark Mode* para renderização de páginas web escuras.
* **Abas Flutuantes e Inteligentes:** Sistema de abas dinâmicas estilo Firefox que se autoredimensionam conforme o espaço disponível e ocultam textos se a janela estiver muito compacta.
* **Barra de URL Animada:** Uma barra de pesquisa inteligente que expande horizontalmente ao ganhar foco e colapsa ao perder foco, otimizando o espaço visual.
* **Bloqueador de Anúncios Integrado (AdBlock):** Interceptação nativa de requisições de rede para barrar domínios conhecidos de anúncios e rastreadores (como *DoubleClick*, *Google Ads* e *Hotjar*).
* **Detecção de Sites Maliciosos:** Tela de alerta customizada interativa ao tentar acessar sites suspeitos ou inseguros, permitindo o retorno seguro ou o desvio (*bypass*) por conta e risco do usuário.
* **Gerenciador de Favoritos com Favicons:** Barra de favoritos persistente (salva em arquivo JSON) que captura e exibe automaticamente o ícone (*favicon*) do site adicionado.
* **Custom Window Controls:** Botões de fechar, maximizar e minimizar desenhados do zero, com comportamento nativo de redimensionamento ao arrastar as bordas da tela.

---

## Tecnologias e Bibliotecas Utilizadas

O projeto foi inteiramente desenvolvido em **Python 3**, utilizando o poder do framework de interfaces gráficas **Qt** através de sua versão mais recente:

* **Python:** Linguagem base pela agilidade e integração.
* **PyQt6 (Qt Widgets):** Utilizado para construir toda a estrutura de janelas, layouts dinâmicos, diálogos, menus e animações de propriedades (`QPropertyAnimation`).
* **PyQt6 WebEngine:** O motor gráfico baseado no **Chromium** (o mesmo coração do Google Chrome e Microsoft Edge). Usado para renderizar as páginas da internet com máxima compatibilidade através do `QWebEngineView`.
* **JSON:** Armazenamento leve e local para o sistema de favoritos.
* **UUID & OS:** Gerenciamento interno de identificadores únicos para as abas abertas e manipulação de diretórios para salvar os ícones capturados.

---

## Estrutura do Código

O coração do navegador está estruturado em componentes modulares e reutilizáveis dentro do arquivo principal:

| Componente | Função |
| :--- | :--- |
| `AdBlockerInterceptor` | Filtra o tráfego de rede e bloqueia os scripts de anúncios antes mesmo de serem baixados. |
| `AnimatedUrlBar` | Cuida da animação suave de transição de tamanho da barra de endereço. |
| `MacInputDialog` | Caixa de diálogo customizada sem bordas para entrada de nomes dos favoritos. |
| `AdvancedWebPage` | Controla o fluxo de navegação e exibe a barreira de segurança contra malwares. |
| `CustomTabButton` & `CustomTabBar` | Arquitetura responsável por criar, fechar, redimensionar e estilizar as abas. |
| `AdvancedMacBrowser` | A janela principal que une todos os componentes, gerencia o estilo CSS (QSS) e os eventos do mouse. |

---

## Como Executar o Projeto

### Pré-requisitos
Certifique-se de ter o Python instalado em sua máquina. Você precisará instalar a biblioteca do PyQt6 e suas ferramentas web:

pip install PyQt6 PyQt6-WebEngine

### Inicialização

Basta clonar este repositório e executar o arquivo principal:

python navegador.py

---

## Aprendizados da Imersão & Papel da IA

Desenvolver este navegador foi um divisor de águas prático após a imersão em IA. Mais do que apenas programar, o projeto consolidou a importância de usar a Inteligência Artificial de forma estratégica:

* **Engenharia de Prompt:** Criar uma interface complexa como esta exige precisão. Aprender a estruturar o contexto para a IA, detalhando regras de escopo, limitações do framework (como gerenciamento de memória do PyQt6) e comportamentos visuais esperados foi fundamental para obter respostas limpas e assertivas.
* **Apoio no Código:** A IA atuou como um parceiro de *pair programming*. Ela ajudou a traduzir conceitos visuais complexos do FireFox para folhas de estilo (*QSS/CSS*), estruturar a lógica matemática por trás do redimensionamento dinâmico de janelas sem bordas nativas e acelerar o desenvolvimento de recursos avançados, como a interceptação de requisições de rede para o AdBlocker.
* **Resolução de Bugs em Tempo Real:** Enfrentar erros de runtime do Qt (como objetos deletados antes da hora) ficou muito mais ágil. Saber dialogar com a IA para isolar o problema permitiu debugar o código de forma didática, transformando erros de compilação em oportunidades de aprendizado de arquitetura.
* **IA Gratuita:** Apresentou algumas limitações e o programa contem alguns problemas visuais que não foi possível corrigir ainda, mas funciona para o que ele foi feito.

---
