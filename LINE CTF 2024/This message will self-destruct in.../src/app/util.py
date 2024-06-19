import base64
import io
from PIL import Image

def image_data2url(mimetype:str, image_bytes:bytes) -> str:
    return 'data:{};base64,{}'.format(mimetype, base64.b64encode(image_bytes).decode())

def mosaic(image_bytes:bytes):
    MAX_SIZE = 500
    INTENSITY = 40
    orig = Image.open(io.BytesIO(image_bytes))

    if orig.size[0] > MAX_SIZE or orig.size[1] > MAX_SIZE:
        raise Exception('image too large')

    small = orig.resize((int(round(orig.width / INTENSITY, 0)), int(round(orig.height / INTENSITY, 0))))
    mosaic = small.resize((orig.width, orig.height), resample=Image.NEAREST)
    img_bytes = io.BytesIO()
    try:
        mosaic.save(img_bytes, format='JPEG')
    except Exception:
        mosaic.save(img_bytes, format='PNG')
    return img_bytes.getvalue()