.. history.rst file

Historique des versions
=======================

Version 0.3.0
-------------

- Séparation du code dans différents fichiers/modules
- *config.cfg*: ajouter ``data_active`` et ``metadata_active`` dans [MAIN]
- *getData.py*: ajout de la capacité à récupérer les fichiers XML
- *getData.py*: nettoyage du code


Version 0.2.0
-------------

Version intermédiaire: non publiée

- *data.csv*: ajout de la colonne "sld_file"
- *getData.py*: ajout des paramètres ``nodes_dir``, mettre ``gn_url``, ``md_external_links`` et ``md_georchestra_links`` dans le fichier *config.cfg*
- *getData.py*: amélioration de la documentation du code (classes ``Row()``, ``Style()``
- *getData.py*: début de restructuration sous forme de classe
- *getData.py*: ajout de la gestion des logs via la classe Log()
- *getData.py*: adaptation du code pour réponde aux exigence de PEP8 (vérification avec flake 8).


Version 0.1.0
-------------

Version initiale
