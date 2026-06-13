
# from io import BytesIO
# import ssl
# from urllib.request import urlopen

# import certifi
# from escpos.printer import Network
# from PIL import Image, ImageOps

# CRYFALL_IMAGE_URL: str = 'https://cards.scryfall.io/normal/front/b/d/bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd.jpg';
# MTGJSON_TYPES_FILE_URL = 'https://mtgjson.com/types/AllMTGJSONTypes.ts';


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



import argparse
import sys
from functools import reduce
from typing import Callable, Iterable, TypeVar

import usb.core
import usb.util
from escpos.printer import Network, Usb
from escpos.escpos import Escpos

ATOMIC_CARDS_JSON = 'https://mtgjson.com/api/v5/AtomicCards.json';
CRYFALL_IMAGE_URL = 'https://cards.scryfall.io/normal/front/b/d/bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd.jpg';
VENDOR_ID = 0x154f;
PRODUCT_ID = 0x154f;
DESCRIPTION = """
    Implementation of the \'Magic The Gathering\', Momir format.
"""
PROG = 'momir'


T = TypeVar("T")

def pipe(funcs: Iterable[Callable[[T], T]],value: T) -> T:
    return reduce(lambda acc, f: f(acc), funcs, value)

# get printer
## usb option
'''
    Due to some Operating System shit, (at least) on mac, when using usb, the OS claims the deviceresulting in me
        not able to shit, so i make the OS give it to me :)
'''
def get_usb_printer(vendor_id:str, product_id: str) -> Escpos:
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
def get_network_printer(ip: str, port: int) -> Escpos:
    return Network("10.100.10.100", profile="TM-T88III")

def init_db() -> None:
    ...

import ctypes
import os
import sys


def is_admin() -> bool:
    """Returns True if the script is running with root/administrator privileges."""
    try:
        # Check for Unix/Linux/macOS root (UID 0)
        if hasattr(os, 'getuid'):
            return os.getuid() == 0
        
        # Check for Windows Administrator
        else:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
            
    except Exception:
        return False

if __name__ == "__main__":
    if not is_admin():
        print("❌ Error: This script requires root/administrator privileges to access raw USB hardware.")
        print("Please run with 'sudo python script.py' or as an Administrator.")
        sys.exit(1)

    parser = argparse.ArgumentParser(prog=PROG, description=DESCRIPTION)
    parser.add_argument('-m', '--mana', help='mana value', required=True, type=int)
    parser.add_argument('--init', help='initialize local db', required=False)
    # import, via file or url

    args = parser.parse_args()

    mana: int = args.mana
    should_initialize = args.init or False

    if should_initialize:
        init_db();
        print('db initialized successfully');
        sys.exit(0);

    try:
        p: Escpos = None
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
