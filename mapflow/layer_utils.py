from typing import Optional


def generate_xyz_layer_definition(url, username, password, max_zoom, source_type):
    """
    It includes quadkey, tms and xyz layers, because QGIS treats them the same
    """
    if source_type == 'tms':
        # that is how QGIS understands that this is TMS basemap
        url = url.replace('{y}', '{-y}')
    url = url.replace('&', '%26').replace('=', '%3D')
    params = {
        'type': 'xyz',  # QGIS shows quadkey, tms, xyz - all as xyz layer
        'url': url,
        'zmin': 0,
        'zmax': max_zoom,
        'username': username,
        'password': password
    }
    uri = '&'.join(f'{key}={val}' for key, val in params.items())  # don't url-encode it
    return uri


def proxy_maxar_url(server, image_id):
    """
    When we process a particular image, we use SecureWatch, otherwise - Vivid.
    The name of the service is passed as CONNECTID to our proxy server
    """
    url = f'{server}/png?TileRow={{y}}&TileCol={{x}}&TileMatrix={{z}}' + '&CONNECTID='
    if image_id:
        return add_image_id(url+'securewatch')
    else:
        return url+'vivid'


def maxar_tile_url(base_url, image_id=None):
    """
    base_url is copied from maxar website and looks like
    https://securewatch.digitalglobe.com/earthservice/wmtsaccess?connectid=<UUID>
    we need to return TileUrl with TileMatrix set and so on
    """
    url = base_url + "&SERVICE=WMTS" \
                      "&VERSION=1.0.0" \
                      "&STYLE=" \
                      "&REQUEST=GetTile" \
                      "&LAYER=DigitalGlobe:ImageryTileService" \
                      "&FORMAT=image/jpeg" \
                      "&TileRow={y}" \
                      "&TileCol={x}" \
                      "&TileMatrixSet=EPSG:3857" \
                      "&TileMatrix=EPSG:3857:{z}"
    if image_id:
        url = add_image_id(url, image_id)
    return url


def add_image_id(url: str, image_id: str):
    return url + f'&CQL_FILTER=feature_id=\'{image_id}\''


def generate_maxar_layer_definition(url: str,
                                    username: str, password: str,
                                    max_zoom: int, image_id: Optional[str] = None,
                                    proxy: Optional[str] = None):
    if proxy:
        url = proxy_maxar_url(proxy, image_id)
    else:
        url = maxar_tile_url(url, image_id)
    return generate_xyz_layer_definition(url=url,
                                         username=username,
                                         password=password,
                                         max_zoom=max_zoom,
                                         source_type='xyz')
