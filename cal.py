import requests
import pytz

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from collections import namedtuple
from datetime import datetime, timedelta


Planet = namedtuple('Planet', ['name', 'letter', 'bg_color', 'fg_color'])
LUNAR = Planet('Moon', "R", 'violet', 'white')
MARS = Planet('Mars', "U", 'red', 'white')
MERCURY = Planet('Mercury', "S", 'orange', 'white')
JUPITER = Planet('Jupiter', "V", 'blue', 'white')
VENUS = Planet('Venus', "T", 'green', 'white')
SATURN = Planet('Saturn', "W", 'black', 'white')
SOLAR = Planet('Sun', "Q", 'yellow', 'white')
DAY_RULERS = [LUNAR, MARS, MERCURY, JUPITER, VENUS, SATURN, SOLAR]
HOUR_RULERS = [SATURN, JUPITER, MARS, SOLAR, VENUS, MERCURY, LUNAR]

width = 600
height = 448


def request_wrapper(url, params=None, request_type='json'):
    """
    A generic request wrapper that can handle different types of requests.

    :param url: The URL to send the request to.
    :param params: The parameters to be sent with the request.
    :param request_type: The type of request (e.g., 'json', 'image').
    :return: The response data or None in case of failure.
    """
    response = requests.get(url, params=params)
    if response.status_code == 200:
        if request_type == 'json':
            return response.json()
        elif request_type == 'image':
            return Image.open(BytesIO(response.content)).convert("RGBA")
    else:
        print("Error:", response.status_code)
        return None


def center_glyph(rect_x1, rect_y1, rect_x2, rect_y2, glyph, font, draw):
    bbox = draw.textbbox((0, 0), glyph, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = rect_x1 + (rect_x2 - rect_x1 - text_width) / 2
    y = rect_y1 + (rect_y2 - rect_y1 - text_height) / 2
    return x, y


def draw_glyph(ruler_box_x, ruler_box_y, quarter_width, quarter_height, glyph, draw, font_name, sz, center=None):
    if center is None:
        center = glyph
    astro_font = ImageFont.truetype(font_name, sz)
    color = 'black'  # Text color
    x, y = center_glyph(ruler_box_x, ruler_box_y,
                        ruler_box_x + quarter_width, ruler_box_y + quarter_height,
                        center, astro_font, draw)
    draw.text((x, y), glyph, font=astro_font, fill=color)


def draw_weather_icon(weather_box_x, weather_box_y, quarter_width, quarter_height, weather_icon, image):
    mask = weather_icon.split()[3]
    wwidth, wheight = weather_icon.size
    new_width, new_height = 100, 100  # Replace with the dimensions of the crop you want
    left = (wwidth - new_width) / 2
    top = (wheight - new_height) / 2
    right = (wwidth + new_width) / 2
    bottom = (wheight + new_height) / 2
    weather_icon = weather_icon.crop((int(left), int(top), int(right), int(bottom)))
    mask = mask.crop((int(left), int(top), int(right), int(bottom)))
    icon_x = weather_box_x + (quarter_width - 100) // 2
    icon_y = weather_box_y + (quarter_height - 100) // 2
    image.paste(weather_icon, (int(icon_x), int(icon_y)), mask=mask)


def find_hour_length(end, start):
    # this will return interval of planetary hours
    elapsed_time = end - start
    seconds = elapsed_time.total_seconds()
    length = int(seconds / 12)
    return timedelta(seconds=length)


def get_cal_image():
    image = Image.new("RGBA", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    params = {
        "lat": 39.84,
        "lon": -86.14,
        "exclude": "minutely,alerts",
        "units": "imperial",
        "appid": "616111e7f3d051d7d2352c9ab405861f"
    }
    data = request_wrapper("https://api.openweathermap.org/data/3.0/onecall", params)
    icon = data["current"]["weather"][0]["icon"]
    temp = data["current"]["temp"]
    now = datetime.now().strftime('%y/%m/%d')
    day_ruler = DAY_RULERS[datetime.now().weekday()]
    sunrise_utc = datetime.utcfromtimestamp(data["current"]["sunrise"]).replace(tzinfo=pytz.utc)
    sunset_utc = datetime.utcfromtimestamp(data["current"]["sunset"]).replace(tzinfo=pytz.utc)
    eastern_indiana_timezone = pytz.timezone('America/Indiana/Indianapolis')
    sunrise_eastern_indiana = sunrise_utc.astimezone(eastern_indiana_timezone)
    sunset_eastern_indiana = sunset_utc.astimezone(eastern_indiana_timezone)
    moon_phase = data["daily"][0]["moon_phase"]
    day_hour_length = find_hour_length(sunset_eastern_indiana, sunrise_eastern_indiana)
    image_url = f"https://openweathermap.org/img/wn/{icon}@4x.png"
    weather_icon = request_wrapper(image_url, request_type='image')
    text_font = "NotoSans-VariableFont_wdth,wght.ttf"
    astro_font = "Astronomicon.ttf"
    quarter_height = height * .25
    quarter_width = width * .25
    half_width = width / 2
    weather_box_x = 0
    weather_box_y = quarter_height
    day_ruler_box_x = 0
    day_ruler_box_y = quarter_height * 2
    hour_ruler_box_x = quarter_width
    hour_ruler_box_y = quarter_height * 2
    moon_index = int(moon_phase*12 % 12)
    moon_file = f'moon_icons/{moon_index}.png'
    moon_icon = Image.open(moon_file)
    mask = moon_icon.split()[1]
    image.paste(moon_icon, (int(quarter_width), int(weather_box_y)), mask=mask)

    draw_weather_icon(weather_box_x, weather_box_y, quarter_width, quarter_height, weather_icon, image)
    draw_glyph(day_ruler_box_x, day_ruler_box_y,
               quarter_width, quarter_height, day_ruler.letter, draw, astro_font, 100)
    draw_glyph(hour_ruler_box_x, hour_ruler_box_y,
               quarter_width, quarter_height, SATURN.letter, draw, astro_font, 100)
    draw_glyph(half_width - 25, 0, half_width, quarter_height, str(temp)+"°", draw, text_font, 60)
    draw_glyph(half_width - 25, weather_box_y - 15, half_width, quarter_height, now, draw, text_font, 60)
    draw_glyph(half_width - 25, hour_ruler_box_y - 25,
               half_width, quarter_height, sunrise_eastern_indiana.strftime('%H:%M'), draw, text_font, 60)
    draw_glyph(half_width - 25, quarter_height * 3 - 25,
               half_width, quarter_height, sunset_eastern_indiana.strftime('%H:%M'), draw, text_font, 60)

    return image

