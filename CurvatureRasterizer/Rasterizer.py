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
    #  8 bit (paletted) PNG can be requested with 'png256'
    # JPEG quality can be controlled by adding a suffix to
    # 'jpeg' between 0 and 100 (default is 85):
    # >>> render_to_file(m,'top_quality.jpeg','jpeg100')
    # >>> render_to_file(m,'medium_quality.jpeg','jpeg50')
    parser.add_argument('-f', type=str, default='png', help='Output file-type. Examples: png, png256, jpeg, jpeg50, jpeg100')
    parser.add_argument('-z', type=int, required=True, help='Which zoom to build tiles for.')
    parser.add_argument('-x', type=int, required=True, help='x-coordinate of the tile.')
    parser.add_argument('-y', type=int, required=True, help='y-coordinate of the tile.')
    parser.add_argument('-u', action='store_true', help='Update tiles in the region. Default behavior is to generate if they do not exist.')
    parser.add_argument('--pixels', type=int, default=256, help='Pixel dimension of the output image. Default: 256.')

    result = rasterize_tile(parser.parse_args())
    exit(result)

def build_region_rasters():
    parser = argparse.ArgumentParser(description='Build or rebuild all raster tiles for a region.')
    parser.add_argument('-v', action='store_true', help='Verbose mode, showing status output.')
    parser.add_argument('-l', action='store_true', help='List available regions.')
    parser.add_argument('-r', type=str, help='Which region to [re]build.')
    parser.add_argument('-z', type=int, help='Which zoom to build tiles for.')
    parser.add_argument('-u', action='store_true', help='Update tiles in the region. Default behavior is to generate if they do not exist.')
    parser.add_argument('--pixels', type=int, default=256, help='Pixel dimension of the output image. Default: 256.')
    parser.add_argument('-f', type=str, default='png', help='Output file-type. Examples: png, png256, jpeg, jpeg50, jpeg100')
    parser.add_argument('-i', type=str, default='https://tile.roadcurvature.com/vector/gte1000/{z}/{x}/{y}.mvt', help='Input template path/url for vector tiles. Examples: "http://example.com/{z}/{x}/{y}.mvt", "/var/cache/tiles/vector/{z}/{x}/{y}.mvt"')
    parser.add_argument('-o', type=str, default='/var/www/tilecache/raster/gte1000/{z}/{x}/{y}.png', help='Output template path for raster tiles. Examples: "{z}-{x}-{y}.png", "/var/cache/tiles/raster/{z}/{x}/{y}.png"')
    args = parser.parse_args()

    regions = {
        'world': {
            4: [
                ((0,0), (15,15))
            ],
            5: [
                ((0,0), (31,31))
            ],
            6: [
                ((0,0), (63,63))
            ],
            7: [
                ((0,0), (127,127))
            ],
            8: [
                ((0,0), (255,255))
            ],
        },
        'north-america': {
            4: [
                ((0,3),(5,6)),
                ((0,7),(4,7)),
            ],
            5: [
                ((0,5),(11,14)),

            ],
            6: [
                ((0,13),(23,28)),
            ],
            7: [
                ((0,27),(45,57)),
            ],
            8: [
                ((0,54),(90,115)),
            ]
        },
        'vermont': {
            4: [
                ((4,5), (4,5))
            ],
            5: [
                ((9,11), (9,11))
            ],
            6: [
                ((18,23), (19,23))
            ],
            7: [
                ((37,46), (38,47))
            ],
            8: [
                ((75,92), (77,92)),
                ((75,93), (76,94)),
            ],
        },
        'japan': {
            6: [
                ((56,22),(60,23)),
                ((55,24),(60,24)),
                ((54,25),(60,26)),
                ((53,27),(60,27)),
                ((56,28),(56,28)),
            ],
            7: [
                ((113,45),(120,48)),
                ((111,49),(120,49)),
                ((109,50),(120,53)),
                ((107,54),(120,55)),
                ((112,56),(112,56)),
            ]
        },
        'bhutan-myanmar-laos': {
            6: [
                ((47,26),(49,26)),
                ((47,27),(50,27)),
                ((48,28),(50,28)),
                ((48,29),(51,29)),
                ((49,30),(49,30)),
            ],
            7: [
                ((95,53),(99,54)),
                ((96,55),(101,57)),
                ((97,58),(102,58)),
                ((97,59),(99,60)),
                ((101,59),(101,59)),
            ]
        },
        'australia-oceania': {
            4: [
                ((13,7),(15,11)),
                ((0,7),(2,11)),
            ],
            5: [
                ((26,14),(31,22)),
                ((0,14),(4,22)),
            ],
            6: [
                ((52,28),(63,44)),
                ((0,28),(8,44)),
            ],
            7: [
                ((104,56),(126,88)),
                ((0,56),(16,88)),
            ]
        },
        'venezuela-brazil': {
            6: [
                ((19,29),(20,29)),
                ((18,30),(27,30)),
                ((19,31),(27,32)),
                ((18,33),(27,33)),
                ((20,34),(27,34)),
                ((21,35),(27,37)),
                ((22,38),(27,38)),
            ],
            7: [
                ((37,59),(54,60)),
                ((38,61),(54,61)),
                ((39,62),(54,62)),
                ((39,63),(54,64)),
                ((38,65),(54,65)),
                ((37,66),(54,67)),
                ((40,68),(54,68)),
                ((42,69),(54,69)),
                ((43,70),(54,75)),
                ((44,76),(54,76)),
            ]
        }
    }

    if args.l:
        print("Region      Zooms")
        for name, zooms in regions.items():
            print(name, "      ", end="")
            print(sorted(zooms), sep=", ")
        exit(2)

    if not args.r in regions:
        print("Unknown region", args.r)
        exit(3)

    if not args.z in regions[args.r]:
        print("Unknown zoom ", args.z, "in region", args.r)
        exit(4)

    command_args = AttributeDict()
    command_args.v = args.v
    command_args.i = args.i
    command_args.o = args.o
    command_args.pixels = args.pixels
    command_args.f = args.f
    command_args.u = args.u
    command_args.z = args.z

    for area in regions[args.r][args.z]:
        startx = area[0][0]
        endx = area[1][0]
        starty = area[0][1]
        endy = area[1][1]
        for x in range(startx, endx + 1):
            for y in range(starty, endy + 1):
                command_args.x = x
                command_args.y = y
                rasterize_tile(command_args)

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

def rasterize_tile(args):
    # Check tile already exists.
    output_file = args.o.format(z=args.z, x=args.x, y=args.y)
    output_dir = os.path.dirname(output_file)
    if os.path.exists(output_file) and not args.u:
        print("{} already exists".format(output_file))
        return(0)

    # Check that the directory exists and is writable.
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError:
            print ("Creation of the directory %s failed" % output_dir)
            return(5)
        else:
            print ("%s/ created" % output_dir)

    # Set up projections
    # spherical mercator (most common target map projection of osm data imported with osm2pgsql)
    merc = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')


    m = mapnik.Map(args.pixels, args.pixels)
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
    return(0)
