# Travail dirigé 2

## 1.1 Question du cours 1

## 1.2 Question du cours 2

1. À partir de l'énoncé, on a que $p = 0.9$ représente la proportion d'un programme qui peut être effectuée en parallèle. Ainsi, en utilisant la loi d'Amdahl, on a : $$S(n) = \dfrac{n}{p + n(1 - p)} \Rightarrow \lim_{n \to \infty} S(n) = \dfrac{1}{1 - p} = 10$$
Donc, l'accélération maximale que pourra obtenir Alice
avec son code est 10.

2. À partir du graphique de $S(n)$ et de sa dérivée, nous pouvons observer que pour $n > 15$, sa croissance est trop lente. Comme $n = 15$ donne un speedup de 6.25, équivalent à 62.5% de la valeur théorique maximale, donc avec 15 nœuds, il n'y aurait pas un grand gaspillage des ressources CPU.

3. La loi de Gustafson dit que le speedup est donnée par : $$S(n) = 1 + (n - 1) p$$
Comme le speedup était 4, alors $n = 5$. Comme les données à traiter ont doublé, alors la nouvelle proportion $\tilde{p}$ sera : $$\tilde{p} = \dfrac{2p}{2p + (1 - p)} = \dfrac{2p}{p + 1} \approx 0.95$$
Donc, l'accélération maximale que peut espérer Alice est : $$\tilde{S} = 1 + (5 - 1) \times 0.95 = 4.8$$

## 1.3 Ensemble de Mandelbrot

1. Implémenté dans le code `mandelbrot.py`. Les temps d'exécution pour différents nombre de tâches sont :

| Nombre de tâches | Temps d'exécution | Speedup |
| :--------------: | :---------------: | :-----: |
|                1 |          4.4463 s |    1.00 |
|                2 |          2.3462 s |    1.90 |
|                4 |          1.3666 s |    3.25 |
|                8 |          1.2766 s |    3.48 |

En traçant les points ci-dessus, nous pouvons estimer que environ 12% du code est strictement séquentiel, de sorte que le speedup théorique maximum soit d'environ 8.40 lorsque $n \to \infty$. Ainsi, en augmentant le nombre de processeurs, on s'attend à ce que le speedup augmente, mais pas indéfiniment.

2. Implémenté dans le code `master_slave.py`. Les temps d'exécution pour différents nombre de tâches sont :

***Paquet avec 128 lignes par tâche***

| Nombre de tâches | Temps d'exécution | Speedup |
| :--------------: | :---------------: | :-----: |
|                2 |          4.4289 s |    1.00 |
|                4 |          1.7788 s |    2.50 |
|                8 |          1.5001 s |    2.96 |

***Paquet avec 32 lignes par tâche***

| Nombre de tâches | Temps d'exécution | Speedup |
| :--------------: | :---------------: | :-----: |
|                2 |          4.4232 s |    1.01 |
|                4 |          1.7090 s |    2.60 |
|                8 |          1.2825 s |    3.47 |

***Paquet avec 1 ligne par tâche***

| Nombre de tâches | Temps d'exécution | Speedup |
| :--------------: | :---------------: | :-----: |
|                2 |          4.5809 s |    0.97 |
|                4 |          1.7579 s |    2.53 |
|                8 |          1.3644 s |    3.26 |

On remarque la même limitation asymptotique du speedup, ainsi qu'une certaine influence de la taille des paquets par tâche.

## 1.4 Produit matrice-vecteur

1. Implémenté dans le code `matvec.py`. À la ligne 49, il suffit de faire `from_columns()`.

2. Implémenté dans le code `matvec.py`. À la ligne 49, il suffit de faire `from_rows()`.
