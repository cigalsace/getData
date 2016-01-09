.. get-data documentation master file, created by
   sphinx-quickstart on Mon Jan 04 11:58:50 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to get-data's documentation!
====================================

Objectif de l'application getData
---------------------------------

A partir d'information stockées dans un fichier CSV:

* Télécharger les fichiers ZIP contenant des fichiers de données SHP (shapefile) et les publier automatiquement sur Geoserver.
* Télécharger les fichiers de métadonnées au format XML (pour les placer dans un dossier de moissonnage local pour Geonetwok par exemple). 

*Attention: le script utilise une version modifiée du module Python gsconfig pour gérer l'ensemble des champs "attribution" (cf. répertoire "./libs")*


Fonctionnalités
---------------

**Fonctionnalités:**

- Téléchargement des fichiers XML de métadonnées distants
- Téléchargement et décompression des fichiers ZIP/7Z de données distants
- Publication des fichiers Shapefile dans Geoserver


**Eléments paramétrables:**

- Activation du téléchargement des fichiers XML de métadonnées
- Activation du téléchargement des fichiers ZIP/7Z de données
- Noeuds de moissonnage (URL de téléchargement, dossiers de destination, etc.)
- URL de Geonetwork pour la génération des liens vers les fiches de métadonnées
- Nom des colonnes des fichiers CSV
- Activation de l'enregistrement des actions réalisées dans un fichier de log (chemin paramétrable)


Contents
--------

.. toctree::
   :maxdepth: 2

   Documentation <documentation>
   API <api>
   Historique de version <history>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

