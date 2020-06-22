import os
import sys
import resource
import mercantile
import mapnik
import argparse
import time
from CurvatureRasterizer.VectorTile import CurvatureVectorTile
from CurvatureRasterizer.LineStyle import CurvatureLinesStyle

def build_raster_tile():
    parser = argparse.ArgumentParser(description='Build a raster tile from a vector tile.')
    parser.add_argument('-v', action='store_true', help='Verbose mode, showing status output.')
    parser.add_argument('-i', type=str, required=True, help='Input template path/url for vector tiles. Examples: "http://example.com/{z}/{x}/{y}.mvt", "/var/cache/tiles/vector/{z}/{x}/{y}.mvt"')
    parser.add_argument('-o', type=str, required=True, help='Output template path for raster tiles. Examples: "{z}-{x}-{y}.png", "/var/cache/tiles/raster/{z}/{x}/{y}.png"')
    parser.add_argument('-f', type=str, default='png', help='Output template path for raster tiles. Examples: "{z}-{x}-{y}.png", "/var/cache/tiles/raster/{z}/{x}/{y}.png"')
    parser.add_argument('-z', type=int, required=True, help='Which zoom to build tiles for.')
    parser.add_argument('-x', type=int, required=True, help='x-coordinate of the tile.')
    parser.add_argument('-y', type=int, required=True, help='y-coordinate of the tile.')
    parser.add_argument('-u', action='store_true', help='Update tiles in the region. Default behavior is to generate if they do not exist.')
    args = parser.parse_args()


    # Check tile already exists.
    output_file = args.o.format(z=args.z, x=args.x, y=args.y)
    output_dir = os.path.dirname(output_file)
    if os.path.exists(output_file) and not args.u:
        print("{} already exists".format(output_file))
        exit()

    # Check that the directory exists and is writable.
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError:
            print ("Creation of the directory %s failed" % output_dir)
            exit(5)
        else:
            print ("%s/ created" % output_dir)

    # Set up projections
    # spherical mercator (most common target map projection of osm data imported with osm2pgsql)
    merc = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')


    m = mapnik.Map(256,256)
    m.srs = merc.params()
    m.background = mapnik.Color('#00000000')
    m.append_style('Curvature Lines', CurvatureLinesStyle(args.z).get_style())

    vector_tile = CurvatureVectorTile(args.i, args.z, args.x, args.y)
    ds = mapnik.MemoryDatasource()
    vector_tile.add_features_to_datasource(ds)
    layer = mapnik.Layer('curvature')
    layer.srs = merc.params()
    layer.datasource = ds
    layer.styles.append('Curvature Lines')
    m.layers.append(layer)

    # Set the output bounding-box to the tile bounds.
    # merc_bbox = mercantile.bounds(args.x, args.y, args.z)
    # bbox = mapnik.Box2d(merc_bbox.west, merc_bbox.south, merc_bbox.east, merc_bbox.north)
    bbox = mapnik.Box2d(0, 0, vector_tile.extent, vector_tile.extent)
    m.zoom_to_box(bbox)

    mapnik.render_to_file(m, output_file, args.f)
    print ("%s written" % output_file)

    if args.v:
        sys.stderr.write("{mem:.1f}MB\n".format( mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))
        sys.stderr.flush()
