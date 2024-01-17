# BYOD OS202 : programmation parallèle
ENSTA Paris - édition 2023/24

## Installation des outils nécessaires aux TDs

### Linux/Debian 

    sudo apt install build-essential make libopenmpi-dev python3-mpi4py python3-pygame

### Mac

Le mieux est d'utiliser Anaconda :  https://www.anaconda.com/products/individual
   * C'est lourd (~500Mo) mais tout est inclus (python, packages scientiques) et ça marche sur linux, mac ou windows
   * Il y a plein de tutoriel pour lancer l'environnement, par exemple: https://openclassrooms.com/fr/courses/6204541-initiez-vous-a-python-pour-lanalyse-de-donnees/6204548-installez-python-et-anaconda
   * Installer mpi4py et pygame sous votre environnement Anaconda

### Windows 10/11

   * Installer msmpi : https://learn.microsoft.com/fr-fr/message-passing-interface/microsoft-mpi (Attention, ne pas oublier d'installer les deux paquets proposés !)
   * Installer python à partir du Windows Store
   * Utiliser pip pour installer mpi4py et pygame (à partir d'un terminal du style powershell):
      - ```pip install mpi4py```
      - ```pip install pygame```

## Vérification de l'installation

Dans le répertoire ```Transparents/examples/MPI``` vous trouverez des examples MPI en Python. Testez si votre installation marche en tapant dans un terminal :
```sh
mpiexec -np 2 python parallel_hello_world.py
```
