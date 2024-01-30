
# TD1

`pandoc -s --toc README.md --css=./github-pandoc.css -o README.html`

## lscpu

Architecture:            x86_64
  CPU op-mode(s):        32-bit, 64-bit
  Address sizes:         39 bits physical, 48 bits virtual
  Byte Order:            Little Endian
CPU(s):                  8
  On-line CPU(s) list:   0-7
Vendor ID:               GenuineIntel
  Model name:            11th Gen Intel(R) Core(TM) i7-1165G7 @ 2.80GHz
    CPU family:          6
    Model:               140
    Thread(s) per core:  2
    Core(s) per socket:  4
    Socket(s):           1
    Stepping:            1
    CPU max MHz:         4700,0000
    CPU min MHz:         400,0000
    BogoMIPS:            5606.40
Virtualization features: 
  Virtualization:        VT-x
Caches (sum of all):     
  L1d:                   192 KiB (4 instances)
  L1i:                   128 KiB (4 instances)
  L2:                    5 MiB (4 instances)
  L3:                    12 MiB (1 instance)

## Produit matrice-matrice



### Permutation des boucles

*Expliquer comment est compilé le code (ligne de make ou de gcc) : on aura besoin de savoir l'optim, les paramètres, etc. Par exemple :*

`make TestProduct.exe && ./TestProduct.exe 1024`


  ordre           | time    | MFlops  | MFlops(n=2048) 
------------------|---------|---------|----------------
i,j,k (origine)   | 2.73764 | 782.476 | 108.26           
j,i,k             | 0.849051 | 2529.27 | 329.936
i,k,j             | 6.1705 | 348.024 | 129.109
k,i,j             | 31.421  | 62.0361  | 70.3662  
j,k,i             | 0.795297 | 2700.23 | 2828.6   
k,j,i             | 0.849051 | 2529.27 | 2191.71

*Discussion des résultats*
Lorsque les données sont stockées en colonnes, un accès continu à la mémoire sans saut améliore les performances, en tirant parti de manière efficace du cache. Les boucles j,k,i et i,k,j montrent les meilleures performances, avec une fréquence plus élevée de modification de la variable i.

L'ordre optimal des boucles pour le produit matrice-matrice demeure j,k,i, optimisant l'accès à la mémoire malgré une complexité algorithmique inchangée. La taille des données d'entrée et l'utilisation de plusieurs cœurs de processeur influent sur la performance en modifiant la quantité de cache disponible.

L'optimisation clé réside dans le stockage en mémoire, où l'accès séquentiel continu en j,k,i tire parti de la structure de stockage colonne par colonne. Cela améliore l'utilisation de la ligne de cache, rapprochant les données du processeur et accélérant l'exécution globale en réduisant le temps d'accès à la mémoire.


### OMP sur la meilleure boucle 

`make TestProduct.exe && OMP_NUM_THREADS=8 ./TestProduct.exe 1024`

  OMP_NUM         | MFlops(n=512) | MFlops(n=1024)  | MFlops(n=2048) | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
1 | 1449.7 | 1299.8 | 1300.1 | 1178.3 |
2                 | 1534.5 | 1269.5 | 1133.8 | 1316.2
3 | 1456.9 | 1041.5 | 999.1 | 1190.0
4 | 1558.3 | 1280.8 | 1154.9 | 1258.3
5 | 1489.2 | 1330.5 | 1287.5 | 1246.3
6 | 1579.1 | 1427.5 | 1290.8 | 1244.7
7 | 1535.0 | 1325.8 | 1235.5 | 1154.9
8 | 1591.0 | 1361.8 | 1210.5 | 1236.5

Il n’y a quasiment aucune amélioration, surtout pour les plus grandes dimensions.


### Produit par blocs

`make TestProduct.exe && ./TestProduct.exe 1024`

  szBlock         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
origine (=max)    |  |
32                |  |
64                |  |
128               |  |
256               |  |
512               |  | 
1024              |  |




### Bloc + OMP



  szBlock      | OMP_NUM | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)|
---------------|---------|---------|-------------------------------------------------|
A.nbCols       |  1      |         |                |                |               |
512            |  8      |         |                |                |               |
---------------|---------|---------|-------------------------------------------------|
Speed-up       |         |         |                |                |               |
---------------|---------|---------|-------------------------------------------------|



### Comparaison with BLAS


# Tips 

```
	env 
	OMP_NUM_THREADS=4 ./produitMatriceMatrice.exe
```

```
    $ for i in $(seq 1 4); do elap=$(OMP_NUM_THREADS=$i ./TestProductOmp.exe|grep "Temps CPU"|cut -d " " -f 7); echo -e "$i\t$elap"; done > timers.out
```
