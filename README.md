# Agent0_minotauro

## Sobre o projeto:

O projeto Agent0_minotauro permite explorar a interação entre um agente e um ambiente.


###Ambiente
O ambiente consiste num tabuleiro retangular de casas quadradas, que podem conter obstáculos ou objetivos. Para se movimentar neste ambiente, o agente pode deslocar-se em frente ou mudar de direção.

A interação entre o agente e o ambiente é comandada através de um cliente e acontece no servidor.

Foi utilizado o Agent0 minotauro para o desenvolvimento do algoritmo A Star na etapa base.


###Algoritmo A star

O algoritmo A Star têm o propósito de chegar ao objetivo final pesquisando o caminho mais rápido possível

Isto é feito utilizando a fórmula f = g + h, em que g é o custo do movimento entre nodes e h foi a heurística criada por nós. 

Neste caso, a heurística é o número de casas que o agente teria de se deslocar para poder chegar ao objetivo final, neste caso utilizamos uma heurística de aproximação (Manhattan Distance).

Esta heuristica consiste na soma absoluta da diferença dos valores das coordenadas do objetivo final e da posição inicial. 

Tendo isto em conta, o algoritmo A star vai escolher a posição com menor “f” e assim contruir um caminho com o menor custo possível até ao objetivo final. 

Como resultado deste algoritmo um caminho com mais casas poderia ser escolhido por ter um custo menor de deslocação entre as suas casas.

###Grupo 4:
 
 Henrique Moniz 20182446
 Leonardo Branco 20182157
 Tiago Rolo 20182770
