import logging
import argparse
import json
from colormath.color_objects import sRGBColor, HSLColor
from colormath.color_conversions import convert_color
from enum import Enum
from logging_setup import setup_logging

args = None


class Format(Enum):
    """Represents the different formats for color representation."""
    hex = 'hex'
    rgb = 'rgb'
    hsl = 'hsl'


def parse_args():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    global args
    parser = argparse.ArgumentParser(
        description="A shade generator given in different formats")
    parser.add_argument("-c", "--config-file",
                        help="The configuration file to use", type=str)
    parser.add_argument(
        "-f", "--format", help="The type of format to use for the color (hex, rgb, hsl)", type=Format)
    parser.add_argument(
        "--css", help="Outputs the contents in CSS preprocessor way for Tailwind", action="store_true")
    args = parser.parse_args()
    return args


def hex_to_hsl(hex_color):
    """
    Convert a hexadecimal color code to HSL color space.

    Args:
        hex_color (str): The hexadecimal color code to convert.

    Returns:
        HSLColor: The color in HSL color space.
    """
    rgb = sRGBColor.new_from_rgb_hex(hex_color)
    return convert_color(rgb, HSLColor)


def hsl_to_hex(hsl_color):
    rgb = convert_color(hsl_color, sRGBColor)
    return rgb.get_rgb_hex()


def open_config(file_name: str):
    """
    Opens and loads a JSON config file.

    Args:
        file_name (str): The name of the config file to open.

    Returns:
        dict: The loaded JSON data from the config file.
    """
    with open(file_name, 'r') as file:
        return json.load(file)


def generate_shades(hex, format: Format = Format.hsl):
    hsl = hex_to_hsl(hex)
    (h, s, l) = hsl.get_value_tuple()
    shades = {"default": hsl, "50": HSLColor(
        h, s, 0.95)}

    for i in range(9):
        shade_name = str((i + 1) * 100)
        lightness = 90 - (i * 10)
        shade = HSLColor(h, s, lightness / 100.0)
        if format is Format.hex:
            shades[shade_name] = hsl_to_hex(shade)

    shades["950"] = HSLColor(h, s, 0.05)

    if format is Format.hex:
        shades["default"] = hsl_to_hex(hsl)
        shades["50"] = hsl_to_hex(shades["50"])
        shades["950"] = hsl_to_hex(shades["950"])

    return shades


def main():
    setup_logging()
    logging.debug("Logging setup")
    parse_args()

    config = open_config(args.config_file)
    color_shades = {}
    for color in config['colors']:
        name = color['name']
        light = color['default']
        color_shades[name] = {}
        shades = generate_shades(light, Format.hex)
        color_shades[name]["light"] = shades
        dark = color['dark']
        shades = generate_shades(dark, Format.hex)
        color_shades[name]["dark"] = shades

    # logging.debug(color_shades)

    # Light only
    light_shades_str = {}
    for color, obj in color_shades.items():
        shades = obj["light"]
        light_shades_str[color] = []
        for shade, value in shades.items():
            if shade != "default":
                light_shades_str[color].append(f"--{color}-{shade}: {value}")
            else:
                light_shades_str[color].append(f"--{color}: {value}")

    # Dark only
    dark_shades_str = {}
    for color, obj in color_shades.items():
        shades = obj["dark"]
        dark_shades_str[color] = []
        for shade, value in shades.items():
            if shade != "default":
                dark_shades_str[color].append(f"--{color}-{shade}: {value}")
            else:
                dark_shades_str[color].append(f"--{color}: {value}")

    print("@tailwind base;")
    print("@tailwind components;")
    print("@tailwind utilities;")
    print("")
    print(":root {")
    for _, shades in light_shades_str.items():
        print("")
        for shade in shades:
            print(f"\t{shade}")

    print("}")
    print("")
    print(".dark {")
    for _, shades in dark_shades_str.items():
        print("")
        for shade in shades:
            print(f"\t{shade}")
    print("}")


if __name__ == "__main__":
    main()
