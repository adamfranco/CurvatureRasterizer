import os
import sys
import argparse
import subprocess

def roll_up_raster_tiles():
    parser = argparse.ArgumentParser(description='Build lower-zoom raster-tiles from high-zoom tiles.')
    parser.add_argument('-v', action='store_true', help='Verbose mode, showing status output.')
    parser.add_argument('-i', type=str, required=True, help='Input template path/url for high-zoom tiles. Examples: "http://example.com/{z}/{x}/{y}.png", "/var/cache/tiles/vector/{z}/{x}/{y}.png"')
    parser.add_argument('-o', type=str, required=True, help='Output template path for low-zoom raster tiles. Examples: "{z}-{x}-{y}.png", "/var/cache/tiles/raster/{z}/{x}/{y}.png"')
    #  8 bit (paletted) PNG can be requested with 'png256'
    # JPEG quality can be controlled by adding a suffix to
    # 'jpeg' between 0 and 100 (default is 85):
    # >>> render_to_file(m,'top_quality.jpeg','jpeg100')
    # >>> render_to_file(m,'medium_quality.jpeg','jpeg50')
    parser.add_argument('-f', type=str, default='png', help='Output file-type. Examples: png, png256, jpeg, jpeg50, jpeg100')
    parser.add_argument('--input_zoom', type=int, required=True, help='Which zoom start with.')
    parser.add_argument('--start_zoom', type=int, required=True, help='The highest Zoom level to start with.')
    parser.add_argument('--stop_zoom', type=int, default=1, help='The lowest Zoom level to end on.')
    parser.add_argument('-u', action='store_true', help='Update tiles in the region. Default behavior is to generate if they do not exist.')
    parser.add_argument('--pixels', type=int, default=256, help='Pixel dimension of the output image. Default: 256.')

    result = roll_up(parser.parse_args())
    exit(result)

def roll_up(args):
    if args.input_zoom <= args.start_zoom:
        print ("--input_zoom must be greater than --output_zoom")
        return(2)
    if args.start_zoom < args.stop_zoom:
        print ("--start_zoom must be greater than or equal to --stop_zoom")
        return(2)
    for z in range(args.start_zoom, args.stop_zoom, -1):
        roll_up_level(args, z)

def roll_up_level(args, z_out):
    num_in_tiles = tiles_at_level(args.input_zoom)
    num_out_tiles = tiles_at_level(z_out)
    input_tile_width = round(num_in_tiles / num_out_tiles)
    for x_out in range(0, num_out_tiles):
        for y_out in range(0, num_out_tiles):
            output_file = args.o.format(z=z_out, x=x_out, y=y_out)
            output_dir = os.path.dirname(output_file)
            if os.path.exists(output_file) and not args.u:
                print("{} already exists".format(output_file))
                continue

            # Check that the directory exists and is writable.
            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except OSError:
                    print ("Creation of the directory %s failed" % output_dir)
                    return(5)
                else:
                    print ("%s/ created" % output_dir)

            # Build a big version of the tile.
            command = ['montage'] + input_tile_list(args.i, args.input_zoom, z_out, x_out, y_out)
            command.append('-tile')
            command.append('{}x{}'.format(input_tile_width, input_tile_width))
            command.append('-geometry')
            command.append('{}x{}'.format(input_tile_width * args.pixels, input_tile_width * args.pixels))
            command.append('-background')
            command.append('none')
            command.append(output_file)
            subprocess.call(command)

            # Resize it.
            command = ['convert', output_file, '-adaptive-resize', '{}x{}'.format(args.pixels, args.pixels), output_file]
            subprocess.call(command)
            print ("%s created" % output_file)

def tiles_at_level(zoom):
    return 2 ** zoom


def input_tile_list(input_template, z_in, z_out, x_out, y_out):
    input_tiles = []
    num_in_tiles = tiles_at_level(z_in)
    num_out_tiles = tiles_at_level(z_out)
    input_tile_width = round(num_in_tiles / num_out_tiles)
    x_in_start = x_out * input_tile_width
    x_in_end = x_in_start + input_tile_width
    y_in_start = y_out * input_tile_width
    y_in_end = y_in_start + input_tile_width
    # Tiles must be listed by filling rows from top-down.
    for y in range(y_in_start, y_in_end):
        for x in range(x_in_start, x_in_end):
            input_tiles.append(input_template.format(z=z_in, x=x, y=y))
    return input_tiles
