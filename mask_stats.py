import os
import glob
import pandas as pd
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats

def open_boundary(limit):
    """
    Function to read a geopackage
    :param limit: To define if open municipios or subbacias
    :return: boundaries as geopandas dataframe
    """
    if limit == 'municipios':
        boundaries = gpd.read_file('./inputs/municipios.gpkg', encoding='utf-8')
    else:
        boundaries = gpd.read_file('./inputs/subbacias.gpkg', encoding='utf-8')

    return boundaries


def list_limits(limit):
    """
    Function to get a list of names limits
    :param limit: To define if open municipios or subbacias
    :return: List of unique names in field limite on geodataframe
    """
    boundary = open_boundary(limit)
    bound_list = sorted(list(set(v['limite'] for k, v in boundary.iterrows())))

    return bound_list, boundary


def calc_area_pixel(raster_path):
    """
    Function to calc area using pixel (area considering side * side). Attention with SRC!
    :param raster_path: path of raster to be used
    :return: area per pixel
    """
    raster = rasterio.open(raster_path)
    xsize = abs(raster.profile['transform'][0])
    ysize = abs(raster.profile['transform'][4])

    return xsize * ysize


def stats_landuse(limit):
    """
    Function to get landuse stats considering raster with name uso.tif on /uso_solo
    :param limit: To define if open municipios or subbacias
    :return: Stats with total area in each class calculated
    """
    bound_list, boundary = list_limits(limit)
    raster_path = 'uso_solo/uso.tif'
    area_pixel = calc_area_pixel(raster_path)
    pixels_count = []
    for i in bound_list:
        df = boundary.loc[boundary['limite'] == i]
        stats = zonal_stats(df, raster_path, categorical=True)
        pixels_count.append([i, stats])

    area_stats = []
    for i in pixels_count:
        for lista in i[1]:
            lista.update((k, round(v * area_pixel / 100000, 5)) for k, v in lista.items())
            area_stats.append([i[0], lista])

    return area_stats


def landuse_to_geopackage(limit):
    """
    Function to join result of stats and limits of polygons to export in geopackage
    :param limit: To define if open municipios or subbacias
    :return: Geopackage with stats in each polygons and with multiple columns
    """
    stats = stats_landuse(limit)
    data = []
    for i in stats:
        for k, v in i[1].items():
            data.append([i[0], k, v])

    df2 = pd.DataFrame(data, columns=['limite', 'classe', 'area_km2']).pivot_table(index='limite', columns='classe',
                                                                                   values='area_km2').reset_index()

    df2 = df2.rename(
        columns={10: 'agricultura', 20: 'floresta', 30: 'pastagem', 40: 'arbustivas', 50: 'banhado', 60: 'agua',
                 80: 'impermeavel_urbano', 90: 'solo_exposto'})

    limits = open_boundary(limit)
    merged = limits.merge(df2, on=['limite'])

    return merged.to_file(f'./outputs/landuse_{limit}.gpkg', driver='GPKG')


def paths_tiffs(variable):
    """
    Function to get a list with all paths rasters in folders considering variable precipitacao or temperatura
    :param variable: Define precipitacao or temperatura to look inside this folder
    :return: List with paths tiffs
    """
    return sorted(glob.glob(os.path.join(os.getcwd(), f'{variable}/') + "*.tif"))


def stats_prec_temp(limit, variable):
    """
    Function to calc stats of temperatura or precipitacao for each polygon
    :param limit: To define if open municipios or subbacias
    :param variable: To define which folder will be use to get stats precipatacao (mean anual) or temperatura (max anual)
    :return: Geopackage with stats merged
    """
    limits, boundaries = list_limits(limit)
    boundaries = boundaries.to_crs(4326)
    raster_paths = paths_tiffs(variable)

    if variable == 'precipitacao':
        stats = 'mean'
    else:
        stats = 'max'

    limit_stats = []
    for i in limits:
        df = boundaries.loc[boundaries['limite'] == i]
        for raster in raster_paths:
            data = raster[-8:-4]
            statistic = zonal_stats(df, raster, stats=stats)
            for result in statistic:
                if result[stats] == None:
                    value = 0
                else:
                    value = int(result[stats])
                limit_stats.append([i, data, value])

    df2 = pd.DataFrame(limit_stats, columns=['limite', 'ano', 'precipitacao']).pivot_table(index='limite', columns='ano',
                                                                                   values='precipitacao').reset_index()
    # df2 = df2.rename(
    #     columns={1977: 'ano_1977', 1978: 'ano_1978', 1979: 'ano_1979', 1980: 'ano_1980', 1981: 'ano_1981', 1982: 'ano_1982',
    #              1983: 'ano_1983', 1984: 'ano_1984', 1985: 'ano_1985', 1986: 'ano_1986', 1987: 'ano_1987', 1988: 'ano_1988',
    #              1989: 'ano_1989', 1990: 'ano_1990', 1991: 'ano_1991', 1992: 'ano_1992', 1993: 'ano_1993', 1994: 'ano_1994',
    #              1995: 'ano_1995', 1996: 'ano_1996', 1997: 'ano_1997', 1998: 'ano_1998', 1999: 'ano_1999', 2000: 'ano_2000',
    #              2001: 'ano_2001', 2002: 'ano_2002', 2003: 'ano_2003', 2004: 'ano_2004', 2005: 'ano_2005', 2006: 'ano_2006',
    #              2007: 'ano_2007', 2008: 'ano_2008', 2009: 'ano_2009', 2010: 'ano_2010', 2011: 'ano_2011', 2012: 'ano_2012',
    #              2013: 'ano_2013', 2014: 'ano_2014', 2015: 'ano_2015', 2016: 'ano_2016', 2017: 'ano_2017', 2018: 'ano_2018'
    #              })
    limits = open_boundary(limit)
    merged = limits.merge(df2, on=['limite'])

    return merged.to_file(f'./outputs/{variable}_{limit}.gpkg', driver='GPKG')


if __name__ == '__main__':
    limits = ['municipios', 'subbacias']
    for limit in limits:
        landuse_to_geopackage(limit)
        stats_prec_temp(limit, 'precipitacao')
        stats_prec_temp(limit, 'temperatura')

