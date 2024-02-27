# Solution du TP n°2

## Questions de cours

### Interblocage :

**Scénério n°1** : Les processus zéro et un font un envoie bloquant de leurs données. Le processus deux reçoit le message provenant du processus zéro. Le processus zéro ayant finit d'envoyer son message (reçu par deux), se met
en attente de réception d'un message de deux. Le processus deux envoit son message bloquant au processus zéro qui le reçoit. Enfin,
le processus deux reçoit le message bloquant de un et on quitte cette section du code pour les trois processus. 
En résumé, dans l'ordre chronologique du scénério 1 : (------> = envoyer, <------ = recevoir)

0 --------> 2
1 --------> 2
2 <-------- 0
0 <-------- 2
2 --------> 0
2 <-------- 1

**Scénario n°2** : 
Les processus zéro et un font un envoie bloquant de leurs données. Le processus deux reçoit le message provenant du processus un. Le processus deux envoit ensuite un message au processus zéro qui est toujours en attente de réception de son message par le processus deux. Ainsi, on se retrouve dans une situation où :
    - Le processus zéro attend que le processus deux reçoive son message
    - Le processus un   a quitté cette section de code
    - Le processus deux attend que le processus zéro reçoive son message.
On se retrouve donc dans ce scénario dans une *situation d'interblocage*. 

Les deux scénari étant équiprobables, notre code a donc en moyenne une chance sur deux de se retrouver dans une situation d'interblocage.

### Alice et la loi d'Amdhal

90% du code d'Alice en temps séquentiel peut-être paralléliser pour un jeu de donné fixé. La fraction de code qui ne peut pas être parallélisé est donc égal à f=0.1. La loi d'Amdhal nous dit que l'accélération maximale que l'on peut espérer avoir est :

S(n) = n/(1+(n-1)f) ----> 1/f
                    n -> infini

Quelque soit le nombre de noeuds de calcul que prendra Alice, elle ne pourra jamais atteindre une accélération supérieure à dix avec son jeu de donné. Alice doit prendre un nombre de noeuds de calcul inférieur à dix. Huit noeuds semble être un chiffre raisonnable.

Avec son jeu de donné initial, on sait qu'Alice n'obtient en réalité qu'une accélération maximale de quatre au lieu de dix. Soit
f = 1./4. = 0.25 d'après la loi d'Amdhal.
Donc, en utilisant la loi de Gustafson (ts=0.25, tp=0.75) (on suppose que la partie séquentielle a une complexité constante en temps et la partie parallèle a une complexié linéaire), on a :

S(n) = n + 0.25.(1-n) = 0.25 + 0.75n

D'où S(2) = 1.75

En doublant son nombre de noeuds de calcul, Alice peut espérer une accélération de 1.75.

## Produit matrice-vecteur par ligne
