# Author: John Mays | Policy & Operations Research @ OMB
# maysj at-symbol omb dot nyc dot gov | Last Updated: 06/05/24

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

def create_granular_map(x_coords:pd.Series, y_coords:pd.Series, bounds:tuple,
                        area_size:int, root:float=1, blur:bool=False,
                        sigma:float=1) -> np.ndarray:
    """
    WARNING: make sure bounds, x_coords, and y_coords all belong to the same
        coordinate ref system (CRS).
    This function plots a map of calls as as an image of the NYC area with the
    intensity of pixels reflecting the number of coordinates within their area.
    Args:
        x_coords, y_coords: two pandas series of the x & y coordinates to
            constitute the image
        bounds: a tuple containing the boundaries of the mapped area (x_min,
            y_min, x_max, y_max)
        area_size: the real-unit width of a square area represented by a pixel
        root: the n-th root which scales the intensity map (1 = no scaling)
        blur: choose whether or not to include a blur
        sigma: the width of the gaussian blur in pixels
    Returns:
        intensity_map: numpy matrix of floats [0.0, 1.0] to reflect the
            relative intensity of each square on the map
    """
    x_min, y_min, x_max, y_max = bounds
    area_height = y_max - y_min
    area_width = x_max-x_min
    map_height = int(area_width/area_size)
    map_width = int(area_height/area_size)
    print(f'Resolution of map (width by height) will be: {map_width:.0f}'
          f' by {map_height:.0f} {area_size} foot squares.')
    # create empty matrix:
    intensity_map = np.zeros((map_width, map_height), dtype=np.int64)

    # remove from both series if one coordinate them is not a number/missing:
    all_na = x_coords.isna() + y_coords.isna()
    x_coords, y_coords = x_coords[~all_na], y_coords[~all_na]

    # remove from both series if one coordinate is out-of-bounds (oob):
    all_oob = (x_coords < x_min) + (x_coords > x_max) + (y_coords < y_min)\
        + (y_coords > y_max)
    x_coords, y_coords = x_coords[~all_oob], y_coords[~all_oob]

    # perform broadcasted math & cast to int for simple binning:
    x_coords = ((x_coords-x_min)/area_size).astype(int)
    y_coords = ((y_coords-y_min)/area_size).astype(int)
    missed_count = 0
    for x, y in zip(x_coords, y_coords):
        if y <= y_max and y <= y_min and x <= x_max and x <= x_min:
            i, j = -y, x # have to mirror the placement due to matrix indexing
            try:
                intensity_map[i, j] += 1
            except IndexError:
                missed_count += 1
        else:
            missed_count += 1
    print(f'{missed_count} coords were not within bounds.')
    # convert to floats & normalize:
    intensity_map = intensity_map.astype(float)/intensity_map.max()
    # scale map:
    intensity_map = np.power(intensity_map, (1/root))
    # optional blur map:
    if blur:
        intensity_map = gaussian_filter(intensity_map, sigma=sigma)
    return intensity_map
