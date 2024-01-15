import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import math
import concurrent.futures

# Constants
EARTH_RADIUS_KM = 6371.0
DEG_TO_RAD = math.pi / 180.0

def haversine_distance(lat1, lon1, lat2, lon2):
    dlat = lat1 - lat2
    dlon = lon1 - lon2
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return EARTH_RADIUS_KM * c

def precompute_distances(lat, lon):
    nlat, nlon = len(lat), len(lon)
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    # Initialize an array to store eastward distances
    distances = np.zeros((nlon, nlat))

    # Calculate eastward distances for each latitude
    for j in range(nlat - 1):
        for i in range(nlon - 1):  # Exclude the last longitude point
            dlon = lon_rad[i + 1] - lon_rad[i]
            lat1 = lat_rad[j]
            # Use Haversine formula for distances along a constant latitude
            a = np.sin(dlon / 2)**2 * np.cos(lat1) * np.cos(lat1)
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
            distances[i, j] = EARTH_RADIUS_KM * c

    # Handle the last column by copying the distance from the previous grid point
    distances[:, -1] = distances[:, -2]

    return distances


def smooth(LatIndexer, LonIndexer, r0, x):
    lon = x[LonIndexer].values
    lat = x[LatIndexer].values
    nlat, nlon = len(lat), len(lon)
    xm = xr.full_like(x, fill_value=np.nan)
    rr = r0**2

    # Precompute distances
    distances = precompute_distances(lat, lon)

    for j in range(nlat - 1): 
        for i in range(nlon - 1):
            weight_sum = 0.0
            for di in range(nlon - 1):
                for dj in range(nlat - 1):
                    r = distances[i, j]
                    weight = (rr - r**2) / (rr + r**2)
                    weight = max(weight, 0.0)

                    value = x.isel({LonIndexer: di, LatIndexer: dj}).values
                    xm.isel({LonIndexer: i, LatIndexer: j}).values[()] += weight * value
                    weight_sum += weight

            if weight_sum > 0:
                xm.isel({LonIndexer: i, LatIndexer: j}).values[()] /= weight_sum

    return xm

def smooth2(LatIndexer, LonIndexer, r0, num_iterations, x):
    """
    Apply a smoothing function to the given data using a distance-based weighting scheme,
    repeated for a specified number of iterations.

    Parameters:
    LatIndexer : str
        Indexer for latitude in the xarray dataset.
    LonIndexer : str
        Indexer for longitude in the xarray dataset.
    r0 : float
        Radius of influence for the smoothing in kilometers.
    num_iterations : int
        Number of times the smoothing process is repeated.
    x : xarray.DataArray
        DataArray to be smoothed.

    Returns:
    xarray.DataArray
        Smoothed DataArray after the specified number of iterations.
    """
    lon = x[LonIndexer]
    lat = x[LatIndexer]
    nlat, nlon = len(lat), len(lon)
    xm = xr.full_like(x, fill_value=np.nan)
    rr = r0**2

    dy = EARTH_RADIUS_KM * (lat.isel({LatIndexer: 1}) - lat.isel({LatIndexer: 0})) * DEG_TO_RAD
    djmax = int(r0 / dy)

    for iteration in range(num_iterations):
        for j in range(1, nlat - 1):
            lat_val = lat.isel({LatIndexer: j}).values
            dx = EARTH_RADIUS_KM * np.cos(np.radians(lat_val)) * (lon.isel({LonIndexer: 1}) - lon.isel({LonIndexer: 0})).values * DEG_TO_RAD
            dimax = int(r0 / dx)

            for i in range(1, nlon - 1):
                xm.isel({LonIndexer: i, LatIndexer: j}).values[()] = 0.0
                weight_sum = 0.0

                imin, imax = max(1, i - dimax), min(nlon - 1, i + dimax)
                jmin, jmax = max(1, j - djmax), min(nlat - 1, j + djmax)

                for jj in range(jmin, jmax + 1):
                    for ii in range(imin, imax + 1):
                        xlat1 = lat.isel({LatIndexer: j}).values
                        xlat2 = lat.isel({LatIndexer: jj}).values
                        xlon1 = lon.isel({LonIndexer: i}).values
                        xlon2 = lon.isel({LonIndexer: ii}).values
                        r = haversine_distance(xlat1, xlon1, xlat2, xlon2)
                        weight = (rr - r**2) / (rr + r**2)
                        weight = max(weight, 0.0)

                        value = x.isel({LonIndexer: ii, LatIndexer: jj}).values
                        xm.isel({LonIndexer: i, LatIndexer: j}).values[()] += weight * value
                        weight_sum += weight

                if weight_sum > 0:
                    xm.isel({LonIndexer: i, LatIndexer: j}).values[()] /= weight_sum

    return xm

if __name__ == "__main__":
    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import numpy as np

    test = "NCEP"
    
    if test == "NCEP":
        # Configuration for NCEP-R2
        sample = xr.open_dataset("samples/Reg1-Representative_NCEP-R2.nc")
        LonIndexer, LatIndexer = "lon_2", "lat_2"
        LevelIndexer, TimeIndexer = "lv_ISBL3", "initial_time0_hours"
        TemperatureIndexer = "TMP_2_ISBL"

    elif test == "ERA5":
        # Configuration for ERA5
        sample = xr.open_dataset('/home/daniloceano/Documents/Programs_and_scripts/data_etc/netCDF_files/Reg1-Representative_ERA5.nc')
        LonIndexer, LatIndexer = "longitude", "latitude"
        LevelIndexer, TimeIndexer = "level", "time"
        TemperatureIndexer = "T"
        sample = sample.sel({LatIndexer: slice(0, -60)})

    lat = sample[LatIndexer]
    dx = EARTH_RADIUS_KM * (lat.isel({LatIndexer: 1}) - lat.isel({LatIndexer: 0})) * DEG_TO_RAD
    r0 = np.abs(dx) - 1

    # Subset data for testing
    x = sample[TemperatureIndexer].isel({LevelIndexer:3}).isel({TimeIndexer:1})

    # Apply the smoothing function
    smoothed = smooth(LatIndexer, LonIndexer, r0, x)

    # Apply the second smoothing function
    smoothed2 = smooth2(LatIndexer, LonIndexer, r0, 1, x)

    # Calculate the difference between the original and filtered data
    difference = x - smoothed
    difference2 = x - smoothed2

    def plot_with_cartopy(ax, data, title, cmap='viridis', extend='both', norm=None):
        """
        Helper function to plot data on a map using Cartopy.
        """
        lon, lat = data[LonIndexer], data[LatIndexer]
        mesh = ax.contourf(lon, lat, data, transform=ccrs.PlateCarree(), cmap=cmap, 
                           extend=extend, norm=norm)
        ax.coastlines()
        ax.set_title(title)
        return mesh
    
    # Create normalization
    norm = plt.Normalize(x.min(), x.max())

    # Create the figure with 3 panels
    fig, axs = plt.subplots(2, 3, figsize=(18, 12), subplot_kw={'projection': ccrs.PlateCarree()})

    # Plot original data, filtered data, and difference
    mesh1 = plot_with_cartopy(axs[0, 0], x, "Original Data",  cmap='coolwarm',
                              norm=norm)
    mesh2 = plot_with_cartopy(axs[0, 1], smoothed, "Filtered Data",  cmap='coolwarm',
                              norm=norm)
    mesh3 = plot_with_cartopy(axs[0, 2], difference, "Original - Filtered", cmap='coolwarm',
                              extend='neither')

    # Repeat for the smooth 2
    mesh4 = plot_with_cartopy(axs[1, 0], x, "Original Data",  cmap='coolwarm',
                              norm=norm)
    mesh5 = plot_with_cartopy(axs[1, 1], smoothed2, "Filtered Data 2", cmap='coolwarm',
                              norm=norm)
    mesh6 = plot_with_cartopy(axs[1, 2], difference2, "Original - Filtered 2",
                              cmap='coolwarm', extend='neither')

    # Add colorbars
    fig.colorbar(mesh1, ax=axs[0, :2], orientation='horizontal', fraction=0.046, pad=0.04)
    fig.colorbar(mesh3, ax=axs[0, 2], orientation='horizontal', fraction=0.046, pad=0.04)
    fig.colorbar(mesh4, ax=axs[1, :2], orientation='horizontal', fraction=0.046, pad=0.04)
    fig.colorbar(mesh6, ax=axs[1, 2], orientation='horizontal', fraction=0.046, pad=0.04)

    plt.show()