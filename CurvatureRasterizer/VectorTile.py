import mapbox_vector_tile
import mapnik
import re
from shapely.geometry import shape
from shapely.wkb import dumps as wkb_dumps
import urllib.request

class CurvatureVectorTile(object):
    base_path = '.'
    x = 0
    y = 0
    z = 0
    extent = 0

    def __init__(self, source_template, z, x, y):
        self.source_template = source_template
        self.x = x
        self.y = y
        self.z = z
        self.extent = 0

    def get_data(self):
        file = self.source_template.format(z=self.z, x=self.x, y=self.y)
        if re.search('^https?://', file):
            with urllib.request.urlopen(file) as f:
                return f.read()
        else:
            with open(file, 'rb') as f:
                return f.read()

    def add_features_to_datasource(self, ds):
        i = 0
        context = mapnik.Context()
        context.push('curvature')
        context.push('paved')
        tile = mapbox_vector_tile.decode(self.get_data())
        layer = tile['gte1000']
        self.extent = layer['extent']
        # print(layer['extent'])
        for v_feature in layer['features']:
            feature = mapnik.Feature(context, i)
            feature['curvature'] = v_feature['properties']['curvature']
            feature['paved'] = v_feature['properties']['paved']
            # print (v_feature['geometry'])
            feature_geom = shape(v_feature['geometry'])
            feature.geometry = mapnik.Geometry.from_wkb(wkb_dumps(feature_geom))
            ds.add_feature(feature)
            # print(feature.to_geojson())
            i = i + 1
