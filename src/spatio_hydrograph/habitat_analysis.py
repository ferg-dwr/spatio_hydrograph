"""
Habitat-specific inundation analysis.

Calculates per-habitat inundated area, percent water coverage,
and flood duration metrics.
"""

import geopandas as gpd
import pandas as pd

from .config import Config


class HabitatAnalyzer:
    """Analyze inundation per habitat unit."""

    def __init__(self, config: Config) -> None:
        """
        Initialize habitat analyzer.

        Parameters
        ----------
        config : Config
            Configuration object
        """
        self.config = config

    def calculate_habitat_areas(self, water_polygons: gpd.GeoDataFrame) -> pd.DataFrame:
        """
        Calculate inundated area per habitat.

        Parameters
        ----------
        water_polygons : GeoDataFrame
            Water polygons with habitat attributes from raster_processing.intersect_with_habitats()
            Must have 'habitat' column and 'area_m2' column

        Returns
        -------
        DataFrame
            Columns: habitat, inundated_area_ha, num_features

        Raises
        ------
        ValueError
            If required columns are missing from water_polygons

        Notes
        -----
        Groups water polygons by habitat and sums their areas.
        Converts from square meters to hectares (1 ha = 10,000 m²).
        """
        # Check for required columns
        required_cols = ["habitat", "area_m2"]
        missing_cols = [
            col for col in required_cols if col not in water_polygons.columns
        ]
        if missing_cols:
            raise ValueError(
                f"Missing required columns in water_polygons: {missing_cols}"
            )

        # Group by habitat and aggregate
        habitat_summary = (
            water_polygons.groupby("habitat")
            .agg({"area_m2": ["sum", "count"]})
            .reset_index()
        )

        # Flatten column names
        habitat_summary.columns = ["habitat", "inundated_area_m2", "num_features"]

        # Convert square meters to hectares (1 ha = 10,000 m²)
        habitat_summary["inundated_area_ha"] = (
            habitat_summary["inundated_area_m2"] / 10000
        )

        # Return only relevant columns
        return habitat_summary[["habitat", "inundated_area_ha", "num_features"]].copy()

    def calculate_percent_inundated(self, habitat_areas: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate percent of each habitat that is inundated.

        Parameters
        ----------
        habitat_areas : DataFrame
            Habitat areas from calculate_habitat_areas()
            Must have 'habitat' and 'inundated_area_ha' columns

        Returns
        -------
        DataFrame
            Columns: habitat, inundated_area_ha, percent_inundated

        Raises
        ------
        ValueError
            If required columns missing or total_habitat_area not provided

        Notes
        -----
        Percent inundated = (inundated_area_ha / total_habitat_area) * 100
        Useful for tracking inundation dynamics relative to habitat size.
        Requires habitat total areas to be provided externally via parameter.

        For calculating with known total habitat areas, use
        calculate_percent_inundated_with_totals() instead.
        """
        # Check for required columns
        required_cols = ["habitat", "inundated_area_ha"]
        missing_cols = [
            col for col in required_cols if col not in habitat_areas.columns
        ]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        result = habitat_areas.copy()

        # This method returns data with percent_inundated as NA
        # Users should call calculate_percent_inundated_with_totals() or provide total areas
        result["percent_inundated"] = pd.NA

        return result[["habitat", "inundated_area_ha", "percent_inundated"]].copy()

    def calculate_percent_inundated_with_totals(
        self, habitat_areas: pd.DataFrame, habitat_total_areas: dict
    ) -> pd.DataFrame:
        """
        Calculate percent of each habitat that is inundated using provided total areas.

        Parameters
        ----------
        habitat_areas : DataFrame
            Habitat areas from calculate_habitat_areas()
            Must have 'habitat' and 'inundated_area_ha' columns
        habitat_total_areas : dict
            Dictionary mapping habitat names to total area in hectares
            Example: {"First": 500.0, "Middle": 750.0, "Last": 625.0}

        Returns
        -------
        DataFrame
            Columns: habitat, inundated_area_ha, percent_inundated

        Raises
        ------
        ValueError
            If required columns missing or habitats not in total_areas dict

        Notes
        -----
        Percent inundated = (inundated_area_ha / total_habitat_area) * 100
        """
        # Check for required columns
        required_cols = ["habitat", "inundated_area_ha"]
        missing_cols = [
            col for col in required_cols if col not in habitat_areas.columns
        ]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        result = habitat_areas.copy()

        # Map habitat names to total areas
        result["total_habitat_area_ha"] = result["habitat"].map(habitat_total_areas)
        if result["total_habitat_area_ha"].isna().any():
            missing_habitats = result[result["total_habitat_area_ha"].isna()][
                "habitat"
            ].tolist()
            raise ValueError(
                f"Some habitats not found in habitat_total_areas: {missing_habitats}"
            )

        # Calculate percent inundated
        result["percent_inundated"] = (
            result["inundated_area_ha"] / result["total_habitat_area_ha"] * 100
        )

        # Return relevant columns
        return result[["habitat", "inundated_area_ha", "percent_inundated"]].copy()

    def identify_flood_status(self, habitat_areas: pd.DataFrame) -> dict[str, bool]:
        """
        Identify which habitats are currently flooded.

        Parameters
        ----------
        habitat_areas : DataFrame
            Habitat areas from calculate_habitat_areas()
            Must have 'habitat' and 'inundated_area_ha' columns

        Returns
        -------
        dict
            Mapping of habitat names to flood status (True=flooded, False=dry)

        Raises
        ------
        ValueError
            If required columns missing

        Notes
        -----
        A habitat is considered "flooded" if it has any inundated area.
        Uses flood_trigger_habitats from config to determine when
        flooding has begun (at least one trigger habitat is flooded).
        """
        # Check for required columns
        required_cols = ["habitat", "inundated_area_ha"]
        missing_cols = [
            col for col in required_cols if col not in habitat_areas.columns
        ]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Create flood status dictionary
        flood_status = {}

        for _, row in habitat_areas.iterrows():
            habitat_name = row["habitat"]
            inundated_area = row["inundated_area_ha"]

            # A habitat is flooded if it has any inundated area
            is_flooded = inundated_area > 0

            flood_status[habitat_name] = is_flooded

        return flood_status

    def aggregate_by_water_year(
        self, habitat_time_series: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Aggregate habitat metrics by water year.

        Parameters
        ----------
        habitat_time_series : DataFrame
            Daily habitat area time series
            Must have 'date', 'habitat', 'inundated_area_ha' columns

        Returns
        -------
        DataFrame
            Water year summary statistics with columns:
            habitat, max_inundated_area_ha, mean_inundated_area_ha,
            num_inundation_days, first_flood_date, last_flood_date

        Raises
        ------
        ValueError
            If required columns missing or invalid dates

        Notes
        -----
        Water year is defined by config.water_year parameter.
        Aggregates statistics for each habitat across the water year.
        """
        # Check for required columns
        required_cols = ["date", "habitat", "inundated_area_ha"]
        missing_cols = [
            col for col in required_cols if col not in habitat_time_series.columns
        ]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Ensure date column is datetime
        habitat_time_series = habitat_time_series.copy()
        habitat_time_series["date"] = pd.to_datetime(habitat_time_series["date"])

        # Group by habitat and calculate statistics
        stats = []

        for habitat_name, group in habitat_time_series.groupby("habitat"):
            # Calculate summary statistics
            max_area = group["inundated_area_ha"].max()
            mean_area = group["inundated_area_ha"].mean()

            # Count inundation days (days with area > 0)
            inundation_days = (group["inundated_area_ha"] > 0).sum()

            # Find first and last flood dates
            flooded_mask = group["inundated_area_ha"] > 0
            if flooded_mask.any():
                flooded_dates = group.loc[flooded_mask, "date"]
                first_flood = flooded_dates.min()
                last_flood = flooded_dates.max()
            else:
                first_flood = pd.NaT
                last_flood = pd.NaT

            stats.append(
                {
                    "habitat": habitat_name,
                    "max_inundated_area_ha": max_area,
                    "mean_inundated_area_ha": mean_area,
                    "num_inundation_days": inundation_days,
                    "first_flood_date": first_flood,
                    "last_flood_date": last_flood,
                }
            )

        result = pd.DataFrame(stats)

        return result
