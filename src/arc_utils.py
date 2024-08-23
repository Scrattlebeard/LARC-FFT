from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io
import json
import os
import re

def int_to_colour(i):
    color_map = {
        0: "url(#0-black)",
        1: "url(#1-blue)",
        2: "url(#2-red)",
        3: "url(#3-green)",
        4: "url(#4-yellow)",
        5: "url(#5-grey)",
        6: "url(#6-pink)",
        7: "url(#7-orange)",
        8: "url(#8-teal)",
        9: "url(#9-brown)"
    }
    return color_map.get(i, "#111")

def colour_to_int(colour):
    color_map = {
        "url(#0-black)": 0,
        "url(#1-blue)": 1,
        "url(#2-red)": 2,
        "url(#3-green)": 3,
        "url(#4-yellow)": 4,
        "url(#5-grey)": 5,
        "url(#6-pink)": 6,
        "url(#7-orange)": 7,
        "url(#8-teal)": 8,
        "url(#9-brown)": 9
    }
    return color_map.get(colour, -1)

def grid_to_svg(grid):
    num_rows = len(grid)
    num_cols = len(grid[0])
    svg_width = num_cols * 50
    svg_height = num_rows * 50
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">\n'
    svg_content += '<defs>\n'
    svg_content += '    <!-- Define the overall grid which we represent our shapes in -->\n'
    svg_content += '    <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">\n'
    svg_content += '        <path d="M 50 0 L 0 0 0 50" fill="none" stroke="gray" stroke-width="8"/>\n'
    svg_content += '    </pattern>\n'
    svg_content += '\n'
    svg_content += '    <!-- Define a mapping from int used in the json to colors -->\n'
    svg_content += '    <linearGradient id="0-black">\n'
    svg_content += '        <stop offset="100%" stop-color="#000000"/>\n'
    svg_content += '    </linearGradient>\n'
    svg_content += '    <linearGradient id="1-blue">\n'
    svg_content += '        <stop offset="100%" stop-color="#0074D9"/>\n'
    svg_content += '    </linearGradient>\n'
    svg_content += '    <linearGradient id="2-red">\n'
    svg_content += '        <stop offset="100%" stop-color="#FF4136"/>\n'
    svg_content += '    </linearGradient>\n'
    svg_content += '    <linearGradient id="3-green">\n'
    svg_content += '        <stop offset="100%" stop-color="#2ECC40"/>\n'
    svg_content += '    </linearGradient>\n'
    svg_content += '    <linearGradient id="4-yellow">\n'
    svg_content += '        <stop offset="100%" stop-color="#FFDC00"/>\n'
    svg_content += '    </linearGradient>\n'
    svg_content += '    <linearGradient id="5-grey">\n'
    svg_content += '        <stop offset="100%" stop-color="#AAAAAA"/>\n'
    svg_content += '    </linearGradient>\n'
    svg_content += '    <linearGradient id="6-pink">\n'
    svg_content += '        <stop offset="100%" stop-color="#F012BE"/>\n'
    svg_content += '    </linearGradient>\n'
    svg_content += '    <linearGradient id="7-orange">\n'
    svg_content += '        <stop offset="100%" stop-color="#FF851B"/>\n'
    svg_content += '    </linearGradient>\n'
    svg_content += '    <linearGradient id="8-teal">\n'
    svg_content += '        <stop offset="100%" stop-color="#7FDBFF"/>\n'
    svg_content += '    </linearGradient>\n'
    svg_content += '    <linearGradient id="9-brown">\n'
    svg_content += '        <stop offset="100%" stop-color="#870C25"/>\n'
    svg_content += '    </linearGradient>\n'
    svg_content += '</defs>\n'    
    svg_content += '\n'
    svg_content += '<!-- Now we add in each cell from the json -->\n'
    for row in range(num_rows):
        for col in range(num_cols):
            svg_content += f'<rect id="coord({row},{col})" x="{col * 50}" y="{row * 50}" width="50" height="50" fill="{int_to_colour(grid[row][col])}"/> '
        svg_content += '\n'
    svg_content += '\n'
    svg_content += '<!-- Now we add in the grid pattern -->\n'
    svg_content += '<rect width="100%" height="100%" fill="url(#grid)" />\n'
    svg_content += '</svg>'
    return svg_content

def svg_to_grid(svg):
    content = svg.split('\n')[42:-4]
    grid = []
    for row in content:
        grid.append([convert_cell(cell) for cell in row.strip().split('/> ')])
    return grid

def convert_cell(cell):
    val = cell.split('fill=')[1].split('"')[1]
    return colour_to_int(val)

_cached_driver = None

def get_chrome_driver(width, height):
    global _cached_driver
    if _cached_driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={width},{height}")
        _cached_driver = webdriver.Chrome(options=chrome_options)
    else:
        # Resize the window if necessary
        current_size = _cached_driver.get_window_size()
        if current_size['width'] != width or current_size['height'] != height:
            _cached_driver.set_window_size(width, height)
    
    return _cached_driver

def get_svg_dimensions(svg_data):  
    pattern = r'width="(\d+)" height="(\d+)">'
    match = re.search(pattern, svg_data)
    
    if match:
        width = int(match.group(1))
        height = int(match.group(2))
        return width, height
    else:
        raise ValueError("Could not find SVG dimensions in the provided data.")

def get_svg_dimensions_from_file(filename):
    with open(filename, "r") as file:
        svg_data = file.read()
    return get_svg_dimensions(svg_data)

def render_svg(filename):
    width, height = get_svg_dimensions_from_file(filename)
    driver = get_chrome_driver(width, height)

    # Load the svg file
    driver.get("file://" + os.path.abspath(filename))

    png = driver.get_screenshot_as_png()

    # Use PIL to crop the image to the SVG size
    image = Image.open(io.BytesIO(png))
    image = image.crop((0, 0, width, height))

    image.save(filename.replace(".svg", ".png"))

if __name__ == "__main__":
    with open("src/example.json", "r") as file:
        data = json.load(file)
        num_rows = len(data["input"])
        num_cols = len(data["input"][0])
        svg = grid_to_svg(data["input"])
        print(svg)
        with open("src/example.svg", "w") as file:
            file.write(svg)
        json = svg_to_grid(svg)
        print(json)
        try:
            render_svg("src/example.svg")
        finally:
            if _cached_driver:
                _cached_driver.quit()