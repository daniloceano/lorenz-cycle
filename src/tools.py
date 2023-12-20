# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    tools.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: daniloceano <danilo.oceano@gmail.com>      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/12/19 17:33:03 by daniloceano       #+#    #+#              #
#    Updated: 2023/12/19 23:25:48 by daniloceano      ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import dask
import logging
import xarray as xr
import pandas as pd
import numpy as np
from metpy.units import units
from select_area import slice_domain

def initialize_logging():
    """
    Initializes the logging configuration for the application.
    """
    log_file = 'error_log.txt'
    logging.basicConfig(filename=log_file, filemode='w', level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Remove the log file if it exists and is empty
    if os.path.exists(log_file) and os.path.getsize(log_file) == 0:
        os.remove(log_file)

initialize_logging()

def convert_longitude_range(df: xr.Dataset, lon_indexer: str) -> xr.Dataset:
    """
    Convert longitude range from 0-360 degrees to -180 to 180 degrees.

    This function modifies the longitude coordinates of the provided xarray Dataset 
    and sorts the data based on these updated longitudes.

    Args:
        df (xr.Dataset): The dataset containing longitude coordinates.
        lon_indexer (str): The name of the longitude coordinate in the dataset.

    Returns:
        xr.Dataset: The dataset with updated longitude coordinates.
    """
    df.coords[lon_indexer] = (df.coords[lon_indexer] + 180) % 360 - 180
    df = df.sortby(df[lon_indexer])
    return df

def get_data(infile: str, varlist: str) -> xr.Dataset:
    """
    Opens a NetCDF file and extracts variables specified in a CSV file.

    Args:
        infile (str): Path to the NetCDF file.
        varlist (str): Path to the CSV file listing variables to extract.

    Returns:
        xr.Dataset: Dataset containing extracted variables.

    Raises:
        FileNotFoundError: If CSV file or NetCDF file is not found.
        Exception: For other errors occurring during file opening.
    """
    logging.info(f"Variables specified by the user in: {varlist}")
    logging.info(f"Attempting to read {varlist} file...")

    try:
        variable_list_df = pd.read_csv(varlist, sep=';', index_col=0, header=0)
    except FileNotFoundError:
        logging.error("The 'fvar' text file could not be found.")
        raise
    except pd.errors.EmptyDataError:
        logging.error("The 'fvar' text file is empty.")
        raise

    logging.info("List of variables found:\n" + str(variable_list_df))

    LonIndexer = variable_list_df.loc["Longitude"]["Variable"]
    LatIndexer = variable_list_df.loc["Latitude"]["Variable"]
    LevelIndexer = variable_list_df.loc["Vertical Level"]["Variable"]

    logging.info("Opening input data...")
    try:
        with dask.config.set(array={'slicing': {'split_large_chunks': True}}):
            data = convert_longitude_range(
                xr.open_dataset(infile),
                variable_list_df.loc['Longitude']['Variable']
            )
    except FileNotFoundError:
        logging.error("Could not open file. Check if path, fvars file, and file format (.nc) are correct.")
        raise
    except Exception as e:
        logging.exception("An exception occurred: {}".format(e))
        raise

    logging.info("Assigning geospatial coordinates in radians...")
    data = data.assign_coords({"rlats": np.deg2rad(data[LatIndexer])})
    data = data.assign_coords({"coslats": np.cos(np.deg2rad(data[LatIndexer]))})
    data = data.assign_coords({"rlons": np.deg2rad(data[LonIndexer])})

    levels_Pa = (data[LevelIndexer] * units(str(data[LevelIndexer].units))).metpy.convert_units("Pa")
    data = data.assign_coords({LevelIndexer: levels_Pa})
    
    data = data.sortby(LonIndexer).sortby(LevelIndexer, ascending=True).sortby(LatIndexer, ascending=True)

    lowest_level = float(data[LevelIndexer].max())
    data = data.sel({LevelIndexer: slice(1000, lowest_level)})

    logging.info("Data opened successfully.")
    return data

def find_extremum_coordinates(data: xr.DataArray, lat: xr.DataArray, lon: xr.DataArray, variable: str) -> tuple:
    """
    Finds the indices of extremum values for a given variable in a dataset.

    Args:
        data (xr.DataArray): DataArray containing the data for calculation.
        lat (xr.DataArray): DataArray containing the latitudes.
        lon (xr.DataArray): DataArray containing the longitudes.
        variable (str): Name of the variable to find extremum indices.

    Returns:
        tuple: Tuple containing latitude and longitude of the extremum value.
    """
    lat_values = lat.values
    lon_values = lon.values
    min_lat = lat_values.min()

    if variable == 'min_max_zeta':
        index = np.unravel_index(data.argmin() if min_lat < 0 else data.argmax(), data.shape)
    elif variable in ['min_hgt', 'max_wind']:
        index = np.unravel_index(data.argmin() if variable == 'min_hgt' else data.argmax(), data.shape)
    else:
        logging.error(f"Invalid variable specified: {variable}")
        raise ValueError(f"Invalid variable specified: {variable}")

    return lat_values[index[0]], lon_values[index[1]]

def prepare_data(args, fvars: str = '../inputs/fvars') -> xr.Dataset:
    """
    Prepare the data for further analysis.

    Parameters:
        args (object): The arguments for the function.
        fvars (str): The file path to the fvars.

    Returns:
        method (str): The method used for the analysis: fixed, track or choose.
        xr.Dataset: The prepared dataset for analysis.
    """
    data = get_data(args.infile, fvars)
    if args.mpas:
        data = data.drop_dims('standard_height')
    
    return slice_domain(data, args, fvars)