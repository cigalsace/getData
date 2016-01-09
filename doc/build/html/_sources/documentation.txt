.. documentation.rst file

Documentation de l'application Get-data
=======================================

Gestion de la documentation
---------------------------

Via Sphinx.

Cf. dossiers *doc/sources* et fichiers *doc/source/conf.py*. ::

    $ cd doc
    $ make clean && make html


Requis
------

* Python 2 (testé sous Python 2.7.9 et au-delà)
* Geoserver (testé sous Geoserver 2.5.4)

Modules Python utilisés: (intégrés au code, cf. dossier *./libs*)

* requests
* gs-config

*A noter:*

Par défaut, seul le titre des attributions est récupéré et mis à jour via le module gsconfig. Une modification du fichier *layer.py* du module gsconfig (cf. dossier *./libs*) permet de récupérer également le HREL et l'URL du logo. 
Cette modification a été soumise au projet gsconfig et est en attente d'intégration.


Configuration
-------------

La configuration de getData se fait à 2 niveaux:

* fichier de configuration générale *./config.cfg*
* fichiers de noeud dans la dossier *./nodes* (nom paramétrable)


**Le fichier de configuration principal *./config.cfg*:**

Pour la configuration générale, cf. les commentaires dans le fichier *./config.cfg*.


**Les fichiers de noeud:**

Les points de téléchargement ou "noeuds" de téléchargement sont configurés dans des fichiers JSON stockés dans le dossier "nodes".

Chaque fichier peut contenir plusieurs noeuds.

Organisation recommandée: un fichier par organisme et un noeud de moissonnage par fichier CSV.

Pour désactiver un fichier, faire débuter son nom par un underscore "_".

Pour désactiver un noeud, mettre l'attribut "active" à la valeur "0".

Modèle de fichier JSON (avec commentaires). ::

    {
        "organisme": "gryckelynck - test",                          # Nom de l'organisme
        "nodes": [                                                  # Liste des noeuds
            {                                                       # Premier noeud
                "description": "Point de moissonnage de test",      # Description du point de moissonnage (texte libre)
                "active": "1",                                      # Indique si le point de moissonnage est actif (seuls les noeuds actifs sont moissonnés)
                "src_csv_path": "http://cigalsace.net/get-data/",   # Chemin de l'URL vers le fichier CSV
                "src_csv_file": "gs_data.csv",                      # Nom du fichier CSV
                "xml_dir": "data/xml/",                             # Dossier de destination pour les fichiers XML 
                "tmp_dir": "tmp/test/",                             # Fichier local de travail où sont téléchargés le fichier CSV et les fichiers ZIP, puis dézippés les fichiers shapefile avant de les envoyer sur le serveur.
                "gs_url": "https://dev.cigalsace.org/geoserver/",   # URL de Geoserver
                "gs_login": "login",                                # Login de connexion à Geoserver
                "gs_pwd": "password",                               # Mot de passe de connexion à Geoserver
                "gs_workspace": "gryckelynck"                       # Workspace de travail sous Geoserver
            },
            {                                                       # Deuxième noeud
                "description": "Point de moissonnage vide",         
                "active": "0",
                ...
            }
        ]
    }


Structure d'un fichier CSV
--------------------------

Les informations relatives à chaque couche (layer) à créer, mettre à jour ou supprimer sont stockées dans un fichier CSV qui a la structure suivante.
Les noms indiqués ci-dessous sont ceux par défaut. Il peuvent être paralmétrés dans *./config.cfg*. ::

    ID                      : Identifiant du layer. Non utilisé.
    MD_FILE                 : URL vers le fichier XML de métadonnées.
    MD_FILEID               : Identifiant de la fiche de métadonnées. Permet de générer les liens entre les données et les métadonnées publiées sous Geonetwork. Si non renseigné, pas de lien créés.
    DATA_FILEZIP            : URL vers le fichier ZIP ou 7Z contenant les données et le SLD (optionnel). Le fichier SHP des données (et fichiers associés) doivent être placés directement dans le fichier ZIP sans arborescence. les extensions de fichier doivent être en minuscule. Le fichier ZIP doit avoir le même nom que les fichiers de données (ex.: si le fichier SHP s'appelle "ORG_Fichier1_Data_Proj.shp", le fichier ZIP est "ORG_Fichier1_Data_Proj.zip").
    LAYER_NAME              : Le nom du layer sous Geoserver. Il ne doit pas comporter d'espace ou de caractères spéciaux (accentués, ponctualtion, etc.) 
    RESSOURCE_TITLE         : Le titre du layer dans Géoserver
    RESSOURCE_ABSTRACT      : Le résumé du layer dans Géoserver
    RESSOURCE_KEYWORDS      : La liste des mots clés à ajouter dans Geoserver
    ATTRIBUTION_TITLE       : Le texte des attributions
    ATTRIBUTION_HREF        : L'URL vers le site internet du repsonsable des données
    ATTRIBUTION_LOGO_URL    : L'URL du logo du responsable des données au format image
    ATTRIBUTION_LOGO_TYPE   : Le format (type MIME) du logo (ex.: "image/jpeg")
    ATTRIBUTION_HEIGHT      : La hauteur du logo.
    ATTRIBUTION_WIDTH       : La largeur du logo.
    STYLE_NAME              : Le nom du style associé par default au layer. Si le style doit être créé, le fichier SLD doit être placé dans le fichier ZIP et porter le même nom que ce dernier (comme les fichiers de données).
    SLD_FILE =              : Fichier SLD à télécharger dans Geoserver s'il n'existe pas.
    DATE                    : La date de dernière mise à jour des données. Si elle est différente de la date précédente, les données sont mises à jour.


Utilisation
-----------

* Placer vos données dans un répertoire sur un serveur distant public (ex.: http://remote.dom/my/data/)
* Configurer le fichier CSV pour pointer vers les fichiers ZIP ditants
* Placer le fichier remote/example.csv sur le serveur distant dans un dossier public (ex.: http://remote.dom/my/csv/example.csv)
* Configurer l'application via le fichier *./config.cfg*
* Configurer le noeud de moissonnage pour qu'il pointe sur le fichier CSV
* Lancer le moissonnage

::

$ python getData.py


Fonctionnement technique
------------------------

A partir des informations du fichier JSON, le script télécharge le fichier CSV.
S'il n'y a pas d'ancien fichier CSV, c'est la première consultation du noeud de téléchargement: pour chaque layer (ligne) du fichier CSV, un layer Geoserver est créé.
S'il existe un ancien fichier CSV:

- Si le champ DATE est inchangé, pas de modification.
- Si le champ DATE du layer est différent, le layer est mis à jour (données + informations).
- S'il n'y a pas de correspondance entre le nom du layer dans le nouveau CSV et l'ancien, le layer est créé.
- Si le nom du layer est présent dans l'ancien fichier CSV mais pas le nouveau, le layer est supprimé.


Limites identifiées
-------------------

- Les extensions des fichiers (shp, shx, dbf, prj et sld) doivent être en minuscule.
- Les fichiers de données doivent être directement placés dans l'archive (sans arborescence).
- Le fichier ZIP ou 7Z doit avoir le même nom que le fichier SHP.
- Le nom de la couche (layer name) doit être unique dans l'ensemble de l'instance Geoserver (contournable par des règles de nommage du type "WORKSPACENAME_MY_LAYER_NAME").






