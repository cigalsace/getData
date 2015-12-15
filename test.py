#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint

#from geoserver.catalog import Catalog
from libs.geoserver.catalog import Catalog

#gs_url = "https://www.cigalsace.org/geoserver/rest"
gs_url = "https://dev.cigalsace.org/geoserver/rest"
gs_login = "gryckelynck"
gs_pwd = "guillaume%78"
cat = Catalog(gs_url, gs_login, gs_pwd)

"""
all_layers = cat.get_layers()
for layer in all_layers:
    pprint(vars(layer))
""" 
that_layer = cat.get_layer("CRA_aprona_invplaine_1A_reseau_SUP2009_2009")
pprint(vars(that_layer))
# pprint(vars(that_layer.catalog))
#pprint(that_layer.enabled)
#pprint(vars(that_layer.default_style))
#pprint(that_layer.alternate_styles)
pprint(vars(that_layer.attribution_object))
pprint(that_layer.attribution_object.__dict__)
pprint(that_layer.attribution_object.title)
#pprint(that_layer.attribution_object.url)
pprint(that_layer.attribution)
that_layer.attribution = { 
                            'title': 'test', 
                            'width': 80, 
                            'height': 120, 
                            'href': 'href', 
                            'url': 'url', 
                            'type': 'type' 
                        }
pprint(that_layer.attribution)
#pprint(that_layer.height)

#resource = that_layer.resource
#pprint(resource)

#resource = cat.get_resource("CRA_aprona_invplaine_1A_reseau_SUP2009_2009", workspace="CRA")
#pprint(resource.__dict__)
#pprint(resource.metadata)
"""
pprint(resource.title)
pprint(resource.abstract)
pprint(resource.keywords)
pprint(resource.enabled)
pprint(resource.native_bbox)
pprint(resource.latlon_bbox)
pprint(resource.projection)
pprint(resource.projection_policy)
pprint(vars(resource))


ws = cat.get_workspace("gryckelynck")
#if ws is None:
#   ws = cat.create_workspace('gryckelynck', 'https://www.cigalsace.org/geoserver/gryckelynck')

#ds = cat.get_store('gsconfig1', ws)
#if ds is None:
#    ds = cat.create_datastore('gsconfig1', ws)
#    cat.save(ds)
#    cat.reload()

import geoserver.util
data = geoserver.util.shapefile_and_friends("tmp/test/LIMITE_DEPARTEMENT/LIMITE_DEPARTEMENT")
# shapefile_and_friends should look on the filesystem to find a shapefile
# and related files based on the base path passed in
#
# shapefile_plus_sidecars == {
#    'shp': 'states.shp',
#    'shx': 'states.shx',
#    'prj': 'states.prj',
#    'dbf': 'states.dbf'
# }
# 'data' is required (there may be a 'schema' alternative later, for creating empty featuretypes)
# 'workspace' is optional (GeoServer's default workspace is used by... default)
# 'name' is required
ft = cat.create_featurestore('gsconfig2', data, 'gryckelynck')
"""