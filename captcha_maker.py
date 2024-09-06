from captcha.image import ImageCaptcha
from PIL import Image
from io import BytesIO
from pyfonts import load_font
import random as r

# load font

def randomWord() -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return ''.join(alphabet[r.randint(0, len(alphabet) - 1)] for _ in range(r.randint(8, 16)))


def main() -> None: 
    text: str = randomWord()
    font_paths: list = [r"FONTS\Merriweather-Bold.ttf", 
                  r"FONTS\Handjet-VariableFont_ELGR,ELSH,wght.ttf"] # raw string
  
    captcha: ImageCaptcha = ImageCaptcha(width = 400, 
                                         height = 220, 
                                         fonts=font_paths, 
                                         font_sizes=(90, 60, 120))
    
    data: BytesIO = captcha.generate(text)
    image: Image = Image.open(data)
    image.show('Sample captcha')


if __name__ == '__main__':
    main()

