# from functools import reduce
# from io import BytesIO
# import ssl
# from typing import Any, Callable, Iterable, TypeVar
# from urllib.request import urlopen

# import certifi
# from escpos.printer import Network
# from PIL import Image, ImageOps

# CRYFALL_IMAGE_URL: str = 'https://cards.scryfall.io/normal/front/b/d/bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd.jpg';
# MTGJSON_TYPES_FILE_URL = 'https://mtgjson.com/types/AllMTGJSONTypes.ts';

# T = TypeVar("T")

# def pipe(funcs: Iterable[Callable[[T], T]],value: T) -> T:
#     return reduce(lambda acc, f: f(acc), funcs, value)

# def fetch_image(url: str) -> Image.Image:
#     context = ssl.create_default_context(cafile=certifi.where())
#     res = urlopen(url, context=context).read();
#     return Image.open(BytesIO(res));

# def image_transformation(image: Image.Image) -> Image.Image:
#     ...
#     return pipe()

# def resize(size: tuple[int, int] | list[int] | Any): 
#     def _resize(image: Image.Image) -> Image.Image:
#         return image.resize(size)
    
#     return _resize

# if __name__ == '__main__':
#     kitchen = Network("10.100.10.100", profile="TM-T88III") #Printer IP Address
#     kitchen = 
#     img: Image.Image = fetch_image(CRYFALL_IMAGE_URL);
#     transformed_img: Image.Image = pipe(
#         [
#             ImageOps.grayscale, 
#             lambda img: img.convert("1")
#             # lambda img: img.resize((512, int(img.height * 512 / img.width))),
#     ], img)
#     kitchen.image(transformed_img);
#     kitchen.cut()



import sys
import argparse
import usb.core
import usb.util
from escpos.printer import Usb, Network

ATOMIC_CARDS_JSON = 'https://mtgjson.com/api/v5/AtomicCards.json';
CRYFALL_IMAGE_URL = 'https://cards.scryfall.io/normal/front/b/d/bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd.jpg';
VENDOR_ID = 0x154f;
PRODUCT_ID = 0x154f;

# get printer
## usb option
'''
    Due to some Operating System shit, (at least) on mac, when using usb, the OS claims the deviceresulting in me
        not able to shit, so i make the OS give it to me :)
'''
def get_usb_printer(vendor_id:str, product_id: str) -> Usb:
    print("🚀 Claiming raw hardware interface...")
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

    if dev is None:
        raise Exception("❌ Error: Printer not found.")
    
    try:
        dev.set_configuration()
        usb.util.claim_interface(dev, 0)
    except Exception as e:
        raise Exception(f"⚠️ Lock note: {e}")

    p = Usb(
        idVendor=VENDOR_ID,
        idProduct=PRODUCT_ID,
        dev=dev,           # <-- This is the magic line that prevents the library from crashing
        out_ep=0x02,
        in_ep=0x82,
        profile=None       # Bypasses the problematic default ZJ-8100 lookup
    )
    
    print("🔌 Hardware claimed by python-escpos successfully!")
    
    return p;

## network option
def get_network_printer(ip: str, port: int) -> Network:
    return Network("10.100.10.100", profile="TM-T88III")

def init_db() -> None:
    ...


if __name__ == "__main__":
    DESCRIPTION = """
        Implementation of the \'Magic The Gathering\', Momir format.
    """
    PROG = 'momir'

    parser = argparse.ArgumentParser(prog=PROG, description=DESCRIPTION)
    parser.add_argument('-m', '--mana', help='mana value', required=True)
    parser.add_argument('--init', help='initialize local db')
    # import, via file or url


    parser.add_argument('--land-price', help='maximum price of land card (overrule the card price, obviusly...).', required=False)
    parser.add_argument('--ignore', help='ignore names when checking price.', nargs='+', required=False)
    parser.add_argument('--formats', help='check legality for the formats.', nargs='+', required=False)
    parser.add_argument('--clipboard', help='copy the output to clipboard', action='store_true', required=False)

    args = parser.parse_args()

    DEFAULT_PRICE = 10
    DEFAULT_LAND_PRICE = 1
    DEFAULT_IGNORE_NAMES: list[str] = []
    DEFAULT_FORMATS: list[str] = ['commander']

    max_price = args.price or DEFAULT_PRICE
    max_land_price = args.land_price or DEFAULT_LAND_PRICE
    ignore_names = args.ignore or DEFAULT_IGNORE_NAMES
    formats = args.formats or DEFAULT_FORMATS

    output_names: list[str] = main(args.input, max_price, max_land_price, ignore_names, formats)

    output = '\n'.join(sorted(name for name in output_names))

    if args.clipboard:
        os = platform.system()
        copy_to_clip(os, str(output))
    else:
        print(output)


    try:
        p.codepage = 'cp862'
        
        # Hardware cut
        p.cut()
        print("🚀 Print job sent through the library.")

    except Exception as e:
        print(f"❌ python-escpos runtime error: {e}")
        
    finally:
        # Let the hardware finish printing before releasing the script's grip
        import time
        time.sleep(0.5)
        try:
            usb.util.release_interface(dev, 0)
            print("🔌 Interface released safely for next run.")
        except Exception as e:
            print(f"❌ python-escpos runtime error: {e}")
            sys.exit(1);
