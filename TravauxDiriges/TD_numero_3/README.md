# Travail dirigé 3

*Ce TD peut être réalisé au choix, en C++ ou en Python*

Implémenter l'algorithme "bucket sort" tel que décrit sur les deux dernières planches du cours n°3 :

- Le process 0 génère un tableau de nombres arbitraires
- Il les dispatch aux autres process
- Tous les process participent au tri en parallèle
- Le tableau trié est rassemblé sur le process 0

## Analyse théorique

| Nombre de processeurs | Complexité optimale |
| :-------------------: | :-----------------: |
|                     1 | $\mathcal{O}(n \log n)$ |
|                     2 | $\mathcal{O}\left(\tfrac{n}{2}\right) + \mathcal{O}\left(\tfrac{n}{2} \log \tfrac{n}{2}\right)$ |
|              $\vdots$ |            $\vdots$ |
|                   $k$ | $\mathcal{O}\left(\tfrac{n}{k}\right) + \mathcal{O}\left(\tfrac{n}{k} \log \tfrac{n}{k}\right)$ |

La parallélisation du calcul du min-max fait apparaître le terme $\mathcal{O}\left(\tfrac{n}{k}\right)$.

## Temps d'exécution

***Vecteur avec 10 000 000 composantes***

| Nombre de processeurs | Temps d'exécution | Speedup |
| :-------------------: | :---------------: | :-----: |
|                     1 |          1.7217 s |    1.00 |
|                     2 |          1.1793 s |    1.46 |
|                     3 |          0.9968 s |    1.73 |
|                     4 |          0.9715 s |    1.77 |
|                     5 |          0.9440 s |    1.82 |
|                     6 |          0.9405 s |    1.83 |
|                     8 |          0.9617 s |    1.79 |
|                    10 |          1.0604 s |    1.62 |
|                    12 |          1.0739 s |    1.60 |
|                    14 |          1.0722 s |    1.61 |
|                    16 |          1.1216 s |    1.53 |

Les tests ont été effectués en utilisant un CPU avec 8 cœurs. Ainsi, l'accélération est limitée en raison de l'utilisation de cœurs virtuels.
