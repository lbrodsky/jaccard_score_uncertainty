#!/usr/bin/env python3

"""
This script is developed to calcualate the Jaccrd score with
assumption of the uncertainty e.g. 0.5 * pixel size
based on two (possibly more) vectors delineation
"""

import os
import pandas as pd
import geopandas as gpd

def read_vec(vec_fn):
    """Read vector file with GPD
    """
    df_vec = gpd.read_file(vec_fn)
    return df_vec

def main(path, files):
    """Calcualte Jaccard score
    """
    jaccard_results = {}
    i = 0
    for f in files:
        print('---')
        i += 1
        fn1, fn2, ps = f
        sgl1_fn = os.path.join(path, fn1)
        sgl2_fn = os.path.join(path, fn2)
        date = os.path.basename(sgl1_fn).split('_')[1]
        print(f'Date: {date}')
        print(f'Processing: {os.path.basename(sgl1_fn)} & {os.path.basename(sgl2_fn)}')
        # uncertainty is ~equal of half size of the pixel
        pixel_uncertainty = ps / 2.0
        print(f'Pixel uncertainty: {pixel_uncertainty} m')

        # Read vectors
        df_sgl1 = read_vec(sgl1_fn)
        df_sgl2 = read_vec(sgl2_fn)

        # Uncertainty buffer
        sgl1_buf_plus = df_sgl1.buffer(pixel_uncertainty)
        sgl1_buf_minus = df_sgl1.buffer(-pixel_uncertainty)
        sgl2_buf_plus = df_sgl2.buffer(pixel_uncertainty)
        sgl2_buf_minus = df_sgl2.buffer(-pixel_uncertainty)

        # uncertainty zone polygon
        df_sgl1_buf_plus = gpd.GeoDataFrame({'geometry': sgl1_buf_plus})
        df_sgl1_buf_minus = gpd.GeoDataFrame({'geometry': sgl1_buf_minus})
        df_sgl2_buf_plus = gpd.GeoDataFrame({'geometry': sgl2_buf_plus})
        df_sgl2_buf_minus = gpd.GeoDataFrame({'geometry': sgl2_buf_minus})

        df_sgl1_uncertainty_poly = df_sgl1_buf_plus.overlay(df_sgl1_buf_minus, how='difference')
        df_sgl2_uncertainty_poly = df_sgl2_buf_plus.overlay(df_sgl2_buf_minus, how='difference')

        # Clip uncertainty areas from original data
        df_sgl1_clipped = df_sgl1.overlay(df_sgl1_uncertainty_poly, how='difference')
        df_sgl2_clipped = df_sgl2.overlay(df_sgl2_uncertainty_poly, how='difference')

        # Intersect
        df_sgl12_isect = df_sgl1_clipped.overlay(df_sgl2_clipped, how='intersection')

        # Union
        df_sgl12_union = df_sgl1_clipped.overlay(df_sgl2_clipped, how='union')
        df_sgl12_union['label'] = 1
        df_sgl12_union_dslv = df_sgl12_union.dissolve(by='label')

        # Intersection area
        df_sgl12_isect['area'] = df_sgl12_isect.area
        I_area = df_sgl12_isect['area'].sum()
        print(f'Area of intersection: {I_area:.2f} m^2')

        # Union area
        df_sgl12_union_dslv['area'] = df_sgl12_union_dslv.area
        U_area = df_sgl12_union_dslv['area'].sum()
        print(f'Area of union: {U_area:.2f} m^2')

        # Jaccard score
        Jaccard_score = I_area / U_area
        print('###')
        print(f'Jacard score {date}: {Jaccard_score:.3f}')
        print('###')
        jaccard_results[date] = round(Jaccard_score, 3)

    df_jaccard = pd.DataFrame(jaccard_results.items(), columns=['Date', 'Jaccard_score'])
    jaccard_fn = os.path.join(path, 'jaccard_score_with_uncertainty.csv')
    df_jaccard.to_csv(jaccard_fn, sep=';', header=True)

if __name__ == "__main__":
    path = '/Users/lukas/Work/prfuk/clanky/AUC_Special_issue/Belvedere_SGL_dynamics/data/Vectorisation/Jaccard_score_uncertainty_dev'
    files = [
        ['Samo_20010108_sgl_vec.gpkg', 'Lukas_20010108_sgl_vec.gpkg', 20.0],
        ['Samo_20020808_sgl_vec.gpkg', 'Lukas_20020808_sgl_vec.gpkg', 20.0],
        ['Samo_20030803_sgl_vec.gpkg', 'Lukas_20030803_sgl_vec.gpkg', 20.0],
        ['Samo_20040801_sgl_vec.gpkg', 'Lukas_20040801_sgl_vec.gpkg', 20.0],
        ['Samo_20050720_sgl_vec.gpkg', 'Lukas_20050720_sgl_vec.gpkg', 20.0],
        ['Samo_20060901_sgl_vec.gpkg', 'Lukas_20060901_sgl_vec.gpkg', 20.0],
        ['Samo_20070722_sgl_vec.gpkg', 'Lukas_20070722_sgl_vec.gpkg', 20.0],
        ['Samo_20080715_sgl_vec.gpkg', 'Lukas_20080715_sgl_vec_v2.gpkg', 20.0],
        ['Samo_20090901_sgl_vec.gpkg', 'Lukas_20090901_sgl_vec_v2.gpkg', 20.0],
        ['Samo_20100718_sgl_vec.gpkg', 'Lukas_20100718_sgl_vec.gpkg', 5.0],
        ['Samo_20110703_sgl_vec.gpkg', 'Lukas_20110703_sgl_vec_v2.gpkg', 5.0],
        ['Samo_20120703_sgl_vec.gpkg', 'Lukas_20120703_sgl_vec_v2.gpkg', 5.0],
        ['Samo_20130820_sgl_vec.gpkg', 'Lukas_20130820_sgl_vec.gpkg', 5.0],
        ['Samo_20140913_sgl_vec.gpkg', 'Lukas_20140913_sgl_vec_v2.gpkg', 5.0],
        ['Samo_20150704_sgl_vec.gpkg', 'Lukas_20150704_sgl_vec.gpkg', 5.0],
        ['Samo_20160906_sgl_vec.gpkg', 'Lukas_20160906_sgl_vec.gpkg', 3.0],
        ['Samo_20170820_sgl_vec.gpkg', 'Lukas_20170820_sgl_vec.gpkg', 3.0],
        ['Samo_20180828_sgl_vec.gpkg', 'Lukas_20180828_sgl_vec.gpkg', 3.0],
        ['Samo_20190903_sgl_vec.gpkg', 'Lukas_20190903_sgl_vec.gpkg', 3.0],
        ['Samo_20200904_sgl_vec.gpkg', 'Lukas_20200904_sgl_vec.gpkg', 3.0],
        ['Samo_20210718_sgl_vec.gpkg', 'Lukas_20210718_sgl_vec.gpkg', 3.0],
        ['Samo_20220718_sgl_vec.gpkg', 'Lukas_20220718_sgl_vec.gpkg', 3.0],
        ['Samo_20230709_sgl_vec.gpkg', 'Lukas_20230709_sgl_vec.gpkg', 3.0]
    ]

    main(path, files)

