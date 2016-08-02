# getData

## Objectif de l'application getData

A partir d'information stockées dans un fichier CSV:

- Télécharger les fichiers ZIP contenant des fichiers de données SHP (shapefile) et les publier automatiquement sur Geoserver.
- Télécharger les fichiers de métadonnées au format XML (pour les placer dans un dossier local ou distant - via SFTP - pour un moissonnage Geonetwok par exemple).


## Fonctionnalités

**Principales fonctionnalités:**

- Téléchargement des fichiers XML de métadonnées distants dans un répertoire local
- Téléchargement et décompression des fichiers ZIP/7Z de données distants
- Copie des fichiers XML locaux vers un serveur distant (via SFTP)
- Publication des fichiers Shapefile dans Geoserver

**Eléments paramétrables:**

- Activation du téléchargement des fichiers XML de métadonnées
- Activation du téléchargement des fichiers ZIP/7Z de données
- Noeuds de moissonnage (URL de téléchargement, dossiers de destination, connexion au serveur SFTP, etc.)
- URL de Geonetwork pour la génération des liens vers les fiches de métadonnées
- Nom des colonnes des fichiers CSV
- Activation de l'enregistrement des actions réalisées dans un fichier de log (chemin paramétrable)


## Utilisation

Prérequis: disposer de python 2 et des modules nécessaires (cf. le paragraphe "Installation" ci dessous).

- Placer vos données dans un répertoire sur un serveur distant public (ex.: http://remote.dom/my/data/)
- Configurer le fichier CSV pour pointer vers les fichiers ZIP ditants
- Placer le fichier remote/example.csv sur le serveur distant dans un dossier public (ex.: http://remote.dom/my/csv/example.csv)
- Configurer l'application via le fichier _./config.cfg_
- Configurer le noeud de moissonnage pour qu'il pointe sur le fichier CSV
- Lancer le moissonnage: `python run.py`


## Principes techniques de fonctionnement

A partir des informations du fichier JSON, le script télécharge le fichier CSV.

S'il n'y a pas d'ancien fichier CSV, c'est la première consultation du noeud de téléchargement: pour chaque layer (ligne) du fichier CSV, un entrepôt et un layer Geoserver est créé.

S'il existe un ancien fichier CSV:
- Si le champ DATE est inchangé, pas de modification.
- Si le champ DATE du layer est différent, le layer est mis à jour (données + informations).
- S'il n'y a pas de correspondance entre le nom du layer dans le nouveau CSV et l'ancien, le layer est créé.
- Si le nom du layer est présent dans l'ancien fichier CSV mais pas le nouveau, le layer est supprimé.


## Limites identifiées

- Les extensions des fichiers (shp, shx, dbf, prj et sld) doivent être en minuscule.
- Les fichiers de données doivent être directement placés dans l'archive (sans arborescence).
- Le fichier ZIP ou 7Z doit avoir le même nom que le fichier SHP.
- Le nom de la couche (layer name) doit être unique dans l'ensemble de l'instance Geoserver (contournable par des règles de nommage du type "WORKSPACENAME_MY_LAYER_NAME").


## Installation

### Prérequis

getData fonctionne uniquement sous python 2 (testé sous Python 2.7.10).

Modules Python utilisés (cf. _requirements.txt_):

- requests
- gsconfig (>=1.0.4)
- pylzma
- pysftp

### Mise en place de getData

Le plus simple est d'utiliser un environnement virtuel python.
La procédure ci-dessous est valable pour Windows. Pour plus de détail sur la procédure Linux, merci de vous référer à la documentation correspondante.

```
cd .\getdata

# Create a new python virtualenv
py -2 -m virtualenv --no-site-packages venv

# Activate virtualenv venv
.\venv\Scripts\activate

# Update pip and install requirements
pip install pip --upgrade
pip install -r requirements.txt

# Run application
python run.py
```


## Configuration

La configuration de getData se fait à 2 niveaux:

- Le fichier de configuration générale _./config.cfg_
- Les fichiers de noeud dans la dossier _./nodes_ (le nom est paramétrable paramétrable)

### Le fichier de configuration principal _./config.cfg_

La configuration générale se paramètre dans le fichier _./config.cfg_:

```
{
    "MAIN": {
        "data_active": true,                                            # Indique si le traitement des données est actif
        "metadata_active": true,                                        # Indique si le traitement des médonnées est actif
        "nodes_dir": "nodes",                                           # Nom du doccier contenant les fichiers de configuration des noeuds
        "xml_tmp_dir": "xml",                                           # Nom du répertoire pour stocker temporairement les fichiers XML sur le serveur local lors de l'utilisation du SFTP
        "geonetwork_html_url": "https://test.org/gn/?uuid=",            # URL de consultation d'une fiche Geonetwork au format HTML
        "geonetwork_xml_url": "https://test.org/gn/xml_iso19139?uuid=", # URL de consultation d'une fiche Geonetwork au format XML
        "verbose": true,                                                # Si vrai, affichage des messages à l'écran et enregistrement dans le fichier de log
        "log_file": "log.txt",                                          # Fichier de log
        "always_sync": "always"                                         # Valeur du paramètre date pour forcer la synchronisation des données
    },
    "COLUMNS": {
        "id": "ID",                                                     # ID of row
        "md_file": "MD_FILE",                                           # Path/URL to XML metadata file
        "md_fileid": "MD_FILEID",                                       # Metadata XML file ID (ISO fileIdentifier field)
        "data_filezip": "DATA_FILEZIP",                                 # Path/URL to data ZIP file
        "layer_name": "LAYER_NAME",                                     # Layer name in Geoserver
        "ressource_title": "RESSOURCE_TITLE",                           # Resource title in Geoserver
        "ressource_abstract": "RESSOURCE_ABSTRACT",                     # Resource abstract in Geoserver
        "ressource_keywords": "RESSOURCE_KEYWORDS",                     # Resource keywords in Geoserver
        "attribution_title": "ATTRIBUTION_TITLE",                       # Attribution title of responsible for layer in Geoserver
        "attribution_href": "ATTRIBUTION_HREF",                         # Attribution URL of resposible for layer in Geoserver
        "attribution_logo_url": "ATTRIBUTION_LOGO_URL",                 # Attribution URL of logo in Geoserver
        "attribution_logo_type": "ATTRIBUTION_LOGO_TYPE",               # Attribution logo type in Geoserver
        "attribution_logo_height": "ATTRIBUTION_LOGO_HEIGHT",           # Attribution logo height in Geoserver
        "attribution_logo_width": "ATTRIBUTION_LOGO_WIDTH",             # Attribution logo width in Geoserver
        "style_name": "STYLE_NAME",                                     # Style name in Geoserver
        "sld_file": "SLD_FILE",                                         # Style SLD file in Geoserver
        "date": "DATE"                                                  # Date of modification of row
    }
}
```

### Les fichiers de noeud

Les points de téléchargement ou "noeuds" de téléchargement sont configurés dans des fichiers JSON stockés dans le dossier _./nodes_.
Chaque fichier peut contenir plusieurs noeuds.
Pour désactiver un fichier, faire débuter son nom par un underscore "_".
Pour désactiver un noeud, mettre l'attribut "active" à la valeur "0".

L'organisation recommandée est la suivante: un fichier par organisme et un noeud de moissonnage par fichier CSV.

Modèle de fichier JSON (avec commentaires).

```
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
            "gs_login": "login",                                # Identifiant de connexion à Geoserver
            "gs_pwd": "password",                               # Mot de passe de connexion à Geoserver
            "gs_workspace": "gryckelynck",                      # Workspace de travail sous Geoserver
            "gs_disable_certificate_validation": false,         # Désactiviation de la vérification du certificat de l'URL Geoserver
            "sftp": "1",                                        # Activation du SFTP
            "sftp_hostname": "test.org",                        # Serveur SFTP distant
            "sftp_port": 22,                                    # Port de connexion
            "sftp_username": "test",                            # Identifiant de connexion
            "sftp_private_key": "keys/test_rsa",                # Clé privée de connexion
            "sftp_private_key_pass": "test"                     # Mot de passe de la clé privée
        },
        {                                                       # Deuxième noeud
            "description": "Point de moissonnage vide",
            "active": "0",
            ...
        }
    ]
}
```

### Structure d'un fichier CSV

Les informations relatives à chaque couche (layer) à créer, mettre à jour ou supprimer sont stockées dans un fichier CSV qui a la structure suivante.
Les noms indiqués ci-dessous sont ceux par défaut. Il peuvent être paralmétrés dans _./config.cfg_.

Le champ ``DATE`` permet de gérer la mise à jour des données. S'il est modifié entre 2 utilisations de getData, la couche (layer) est mise à jour.
Il est possible de forcer la mise à jour de certaines couches en mettant le champ ``DATE`` à la valeur ``always`` (par défaut, paramétrable dans _./config.cfg_).

```
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
```
