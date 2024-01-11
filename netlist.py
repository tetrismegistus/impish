import nmap
from PIL import Image, ImageDraw, ImageFont


def get_network_image():
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.0/24', arguments='-sn')
    data = [[nm[host].hostname().split('.')[0], host] for host in nm.all_hosts()]
    image = Image.new('RGB', (600, 448), color=(255, 255, 255))
    draw_table_on_image(image, data, 0, 0, 45, 300, 25)
    return image


def draw_table_on_image(image, data, start_x, start_y, cell_height=30, cell_width=200, font_size=12):
    """
    Draw a table on an existing image based on the provided 2D array data.

    :param image: The image on which to draw the table.
    :param data: 2D array containing the data for the table.
    :param start_x: The x-coordinate of the top left corner of the table.
    :param start_y: The y-coordinate of the top left corner of the table.
    :param cell_height: Height of each cell in the table.
    :param cell_width: Width of each cell in the table.
    :param font_size: Size of the font for the text in the table.
    """
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.truetype("NotoSans-VariableFont_wdth,wght.ttf", font_size) if ImageFont.truetype else ImageFont.load_default()

    # Draw the table
    for i, row in enumerate(data):
        for j, cell in enumerate(row):
            top_left = start_x + j * cell_width, start_y + i * cell_height
            text_position = (top_left[0] + 5, top_left[1] + 5)
            draw.text(text_position, str(cell), fill=(0, 0, 0), font=font)

