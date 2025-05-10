from PIL import Image, ImageDraw

# rgb(248, 30, 38)
# rgb(27, 114, 221)
SIZE = 32
SIZES = [256, 128, 64, 32]
SSAA = 4  # super sampling anti aliasing

TRANSPARENT = (0, 0, 0, 0)
RED = (248, 30, 38, 255)
YELLOW = (255, 200, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (27, 114, 255, 255)
GRAY = (156, 156, 156, 255)
ORANGE = (255, 165, 0, 255)


def calculate_circle_diameters(size: int):
    """
    Calculate the four circle diameters needed for icon generation based on the given size.
    These diameters control the outer ring, inner cutout, inner fill, and center cutout.

    Args:
        size: The target icon size

    Returns:
        A list of four diameter values scaled appropriately for the icon size
    """
    magic_ratios = [285, 235, 176, 73]
    ratio = 256 / size
    factor = 256 / 285
    magic_ratios = [int((size / ratio) * factor) for size in magic_ratios]
    return magic_ratios


def icon_generator(size: int, outer_color: tuple, inner_color: tuple = None):
    """Generates an icon using the cicle diameters from calculate_circle_diameters"""
    if inner_color is None:
        inner_color = outer_color

    size = size * SSAA
    image = Image.new("RGBA", size=(size, size), color=TRANSPARENT)
    draw = ImageDraw.Draw(image)
    d1, d2, d3, d4 = calculate_circle_diameters(size)
    # draw a circle with diameter d1
    delta = (size - d1) / 2
    draw.ellipse((delta, delta, size - delta - 1, size - delta - 1), fill=outer_color)
    # cut out a circle with diameter d2 from the center aka make it transparent
    r1 = d1 / 2
    r2 = d2 / 2
    draw.ellipse((r1 - r2, r1 - r2, r1 + r2, r1 + r2), fill=TRANSPARENT)
    # fill with a circle with diameter d3
    r3 = d3 / 2
    draw.ellipse((r1 - r3, r1 - r3, r1 + r3, r1 + r3), fill=inner_color)
    # cut out a circle with diameter d4 from the center aka make it transparent
    r4 = d4 / 2
    draw.ellipse((r1 - r4, r1 - r4, r1 + r4, r1 + r4), fill=TRANSPARENT)

    # downsample the image
    image = image.resize((size // SSAA, size // SSAA), resample=Image.LANCZOS)
    return image


class ICONS:
    auto_recording = icon_generator(SIZE, RED)
    manual_recording = icon_generator(SIZE, GREEN, RED)
    paused = icon_generator(SIZE, YELLOW)
    standby = icon_generator(SIZE, GREEN, GRAY)
    inactive = icon_generator(SIZE, GRAY)
    rendering = icon_generator(SIZE, BLUE)


if __name__ == "__main__":
    # When running this file as a script, it will generate an icon containing the folloring resolutions:
    muli_res = [icon_generator(size, BLUE) for size in SIZES]
    ico_image = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
    ico_image.save("icon.ico", format="ICO", transparency=0, append_images=muli_res)
