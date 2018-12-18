import urllib.request
import traceback
import os
import mercator
import itertools
import time

class Lonlatbox(object):
    def __init__(self, x0, y0, x1, y1):
        self.west = x0
        self.north = y0
        self.east = x1
        self.south = y1
    def __str__(self):
        return str(self.__dict__).replace("{","").replace("}","").replace("\'","")


def lonrange(scale: int, bbox: Lonlatbox):
    #return [x for x in range(0, 2 ** scale) if not (bbox.east > mercator.tile_lng(scale, x+1) or bbox.west < mercator.tile_lng(scale, x))]
    return [x for x in range(0, 2 ** scale) if bbox.west < mercator.tile_lng(scale, x+1) and bbox.east > mercator.tile_lng(scale, x)]


def latrange(scale: int, bbox: Lonlatbox):
    #return [x for x in range(0, 2 ** scale) if not (bbox.south > mercator.tile_lat(scale, x) or bbox.north < mercator.tile_lat(scale,x+1))]
    return [x for x in range(0, 2 ** scale) if bbox.north > mercator.tile_lat(scale, x+1) and mercator.tile_lat(scale,x)> bbox.south]


def download_scale(scale: int, path: str, bbox: Lonlatbox, printf = print  ):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36";
    headers = {
        'User-Agent':user_agent,
		'x-client-data':'CIa2yQEIpbbJAQjEtskBCKmdygEIu53KAQioo8oBCL+nygEIzqfKAQjiqMoBGPmlygE=',
        'cookie':'GOOGLE_ABUSE_EXEMPTION=ID=4f83f3d2c3ae24cd:TM=1544689628:C=r:IP=150.109.54.248-:S=APGng0uzI4gUrZ_Bp5TMu652sksl4F6kdA'
    }
	
    proxies = {
        "http": "socks5://127.0.0.1:1080",
        "https": "socks5://127.0.0.1:1080"
    }
    proxy_handler = urllib.request.ProxyHandler(proxies);
    opener = urllib.request.build_opener(proxy_handler);

    printf("downloading scale %s to %s" % (scale, path))
    if not os.path.exists(path):
        os.makedirs(path)
    
    r = list(itertools.product(lonrange(scale, bbox), latrange(scale, bbox)))
    lr = len(r)
    printf("total tiles to download: %s" % lr)
	
    end_control = False;
    retry = False;
    while end_control == False:
        if (retry == True):
            retry = False;
            time.sleep(5);
            print("retry");
        end_control = True;
        for num ,(x, y)  in enumerate(r):
            if not os.path.exists(os.path.join(path, "%s_%s.png" % (x, y))):
                #url = 'https://c.tile.opentopomap.org/%s/%s/%s.png' % (scale, x, y);
                url = 'https://khms1.googleapis.com/kh?v=818&hl=en&x=%s&y=%s&z=%s' % (x, y, scale);
                print('%s/%s downloading from %s' % (num, lr, url))
                try:
                    request = urllib.request.Request(url, headers = headers);
                    response = opener.open(request);
                    #response = requests.get('https://khms1.googleapis.com/kh?v=818&hl=en&x=%s&y=%s&z=%s' % (x, y, scale), headers = headers);
                    #response = requests.get(url, headers = headers);
                    png = response.read();
                    #response = urllib.request.urlopen(, proxies=proxies)
                except Exception as e:
                    retry = True;
                    end_control = False;
                    traceback.print_exc()
                    break;
                open(os.path.join(path, "%s_%s.png" % (x, y)), 'wb').write(png)
    printf("\ndownloaded\n")


def calculate_tile_count(scale: int, bbox: Lonlatbox, print_func = print):
    r = list(itertools.product(lonrange(scale, bbox), latrange(scale, bbox)))
    print_func("Zoom %s: Total tiles to download: %s" % (scale ,len(r)))



g_mapbox_token = "pk.eyJ1IjoiYXNpODEiLCJhIjoiZDg1MjUxYTM2Y2RlNmU3ZGM4NjZhZmIxMTAxNDg0OWEifQ.CptV8UPpRwKkm1MM8-t4Lw"


# mapbox://styles/mapbox/streets-v9
# mapbox://styles/mapbox/outdoors-v9
# mapbox://styles/mapbox/light-v9
# mapbox://styles/mapbox/dark-v9
# mapbox://styles/mapbox/satellite-v9
# mapbox://styles/mapbox/satellite-streets-v9

def get_mapbox_tile(zoom, x, y):
    mabbox_ref = 'http://a.tiles.mapbox.com/v4/mapbox.mapbox-streets-v7/%s/%s/%s.mvt?access_token=%s' % (
        zoom, x, y, g_mapbox_token)
    return mabbox_ref


