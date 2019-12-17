import requests
import argparse
import sys
import re
import json


FIGMA_FILES = "https://api.figma.com/v1/files"
ILLEGAL_CHARACTERS = r"[-–—\|\.\s]+"
GLOBAL_PX_SIZE = 1
GLOBAL_REM_SIZE = 16


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', help='Figma API key')
    parser.add_argument('-id', help='Figma ID')
    parser.add_argument('-rgba', help="Add if you want RGBA colors instead of hex", action='store_true')

    args = parser.parse_args()
    pull_tokens(args.k, args.id, args.rgba)


def pull_tokens(api_key, figma_id, use_rgba_color=False):
    r = requests.get(f"{FIGMA_FILES}/{figma_id}", headers=create_headers(api_key)).json()
    children = r["document"]["children"][0]["children"]
    tokens = {}
    if len(children):
        for child in children:
            token_name = child["name"]
            name = token_name.lower()
            if name == "color" or name == "colors":
                tokens[token_name] = setup_color_tokens(child, use_rgba_color)
            elif name == "spacing" or name == "spacings":
                tokens[token_name] = setup_spacing_tokens(child)
            elif name == "font" or name == "fonts":
                tokens[token_name] = setup_font_tokens(child)
            elif name == "lineheight" or name == "lineheights":
                tokens[token_name] = setup_line_height_tokens(child)
            else:
                print(f"Could not find expected token in sheet name {token_name} for sheet with data {child}.")
    else:
        print("No children found in document.")
        sys.exit(1)
    # print(tokens)
    print("done!")

    with open('tokens.json', 'w') as outfile:
    	json.dump(tokens, outfile, indent = 4, ensure_ascii = False)


def setup_color_tokens(color_frame, use_rgba_color=False):
    colors = {}
    for color in color_frame["children"]:
        color_data = color["fills"][0]["color"]
        r = round_color_value(color_data["r"])
        g = round_color_value(color_data["g"])
        b = round_color_value(color_data["b"])
        a = round_color_value(color_data["a"], 1)
        color_string = f"rgba({r}, {g}, {b}, {a})" if use_rgba_color else f"#{int(r):02x}{int(g):02x}{int(b):02x}"
        name = color["name"]
        colors[name] = color_string
    return colors


def setup_spacing_tokens(spacing_frame):
    spacings = {}
    for spacing in spacing_frame["children"]:
        name = spacing["name"]
        bb_width = spacing["absoluteBoundingBox"]["width"]
        spacings[name] = f'{str(int(bb_width))}px'
    return spacings


def setup_font_tokens(frame):
    fonts = []
    for child in frame["children"]:
        layer_name = child["name"]
        font_components = child["style"]["fontPostScriptName"].split("-")
        font_name = child["style"]["fontFamily"]
        font_style = font_components[1].lower() if len(font_components) > 1 else "regular"
        size = int(child["style"]["fontSize"])
        line_height = child["style"]["lineHeightPx"]
        text_align = child["style"]["textAlignHorizontal"].lower()
        font_weight = child["style"]["fontWeight"]
        fonts.append({"fontSize": f'{str(int(size))}px',
                      "lineHeight": f'{str(int(line_height))}px',
                      "textAlign": text_align,
                      "fontStyle": font_style,
                      "fontWeight": font_weight,
                      "fontFamily": font_name,
                      "name": layer_name})
    return fonts


def round_color_value(quantity, scale=255):
    return round(float(quantity) * int(scale), 0)


def create_headers(api_key):
    return {"X-Figma-Token": api_key}


if __name__ == '__main__':
    main()