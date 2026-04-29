"""
Visualization and figure generation.

Creates publication-ready plots of spatio-temporal inundation patterns,
landscape metrics, and connectivity analysis.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .config import Config


class Visualizer:
    """Generate visualizations from analysis results."""

    def __init__(
        self,
        config: Config,
        figsize: tuple = (10, 6),
        dpi: int = 300,
        show: bool = False,
    ) -> None:
        """
        Initialize visualizer.

        Parameters
        ----------
        config : Config
            Configuration object
        figsize : tuple
            Default figure size (width, height) in inches
        dpi : int
            Default DPI for saved figures
        show : bool
            Whether to display plots (default: False for testing)
        """
        self.config = config
        self.figsize = figsize
        self.dpi = dpi
        self.show = show

    def plot_habitat_time_series(
        self, habitat_data: pd.DataFrame, output_file: Path | None = None
    ) -> None:
        """
        Plot habitat inundated area time series.

        Parameters
        ----------
        habitat_data : DataFrame
            Habitat area time series with columns: date, habitat, inundated_area_ha
        output_file : Path, optional
            Path to save figure (e.g., 'habitat_timeseries.png')

        Raises
        ------
        ValueError
            If required columns are missing

        Notes
        -----
        Creates separate line for each habitat showing inundated area over time.
        Publication-ready with legend, grid, and labels.
        """
        # Check for required columns
        required_cols = ["date", "habitat", "inundated_area_ha"]
        missing = [col for col in required_cols if col not in habitat_data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Plot each habitat
        for habitat in habitat_data["habitat"].unique():
            habitat_subset = habitat_data[
                habitat_data["habitat"] == habitat
            ].sort_values("date")
            ax.plot(
                habitat_subset["date"],
                habitat_subset["inundated_area_ha"],
                label=habitat,
                linewidth=2,
                marker="o",
                markersize=4,
            )

        ax.set_xlabel("Date", fontsize=12, fontweight="bold")
        ax.set_ylabel("Inundated Area (ha)", fontsize=12, fontweight="bold")
        ax.set_title(
            "Habitat Inundated Area Time Series", fontsize=14, fontweight="bold"
        )
        ax.legend(loc="best", fontsize=10)
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate(rotation=45, ha="right")
        plt.tight_layout()

        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=self.dpi, bbox_inches="tight")

        if self.show:
            plt.show()

    def plot_percent_water(
        self, habitat_data: pd.DataFrame, output_file: Path | None = None
    ) -> None:
        """
        Plot percent water coverage by habitat.

        Parameters
        ----------
        habitat_data : DataFrame
            Habitat data with columns: habitat, percent_inundated
        output_file : Path, optional
            Path to save figure (e.g., 'percent_water.png')

        Raises
        ------
        ValueError
            If required columns are missing

        Notes
        -----
        Creates bar chart showing percent of each habitat that is inundated.
        Publication-ready with grid and labels.
        """
        # Check for required columns
        required_cols = ["habitat", "percent_inundated"]
        missing = [col for col in required_cols if col not in habitat_data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Create bar chart
        habitat_data_sorted = habitat_data.sort_values(
            "percent_inundated", ascending=False
        )
        bars = ax.bar(
            habitat_data_sorted["habitat"],
            habitat_data_sorted["percent_inundated"],
            color="steelblue",
            edgecolor="black",
            linewidth=1.5,
        )

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.1f}%",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        ax.set_xlabel("Habitat", fontsize=12, fontweight="bold")
        ax.set_ylabel("Percent Inundated (%)", fontsize=12, fontweight="bold")
        ax.set_title("Habitat Inundation Percentage", fontsize=14, fontweight="bold")
        ax.set_ylim(0, max(habitat_data_sorted["percent_inundated"]) * 1.1)
        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()

        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=self.dpi, bbox_inches="tight")

        if self.show:
            plt.show()

    def plot_lateral_connectivity(
        self, connectivity_data: pd.DataFrame, output_file: Path | None = None
    ) -> None:
        """
        Plot lateral connectivity time series with uncertainty.

        Parameters
        ----------
        connectivity_data : DataFrame
            Connectivity statistics with columns: date, mean_connectivity_m, sd_connectivity_m
        output_file : Path, optional
            Path to save figure (e.g., 'connectivity_timeseries.png')

        Raises
        ------
        ValueError
            If required columns are missing

        Notes
        -----
        Creates line plot with shaded error band (± 1 SD).
        Useful for showing connectivity trends with uncertainty.
        """
        # Check for required columns
        required_cols = ["date", "mean_connectivity_m"]
        missing = [col for col in required_cols if col not in connectivity_data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        connectivity_sorted = connectivity_data.sort_values("date")

        # Get SD if available
        has_sd = "sd_connectivity_m" in connectivity_sorted.columns

        if has_sd:
            # Plot with error band
            ax.fill_between(
                connectivity_sorted["date"].values,
                (
                    connectivity_sorted["mean_connectivity_m"]
                    - connectivity_sorted["sd_connectivity_m"]
                ).values,  # type: ignore
                (
                    connectivity_sorted["mean_connectivity_m"]
                    + connectivity_sorted["sd_connectivity_m"]
                ).values,  # type: ignore
                alpha=0.3,
                color="steelblue",
                label="±1 SD",
            )

        ax.plot(
            connectivity_sorted["date"],
            connectivity_sorted["mean_connectivity_m"],
            color="steelblue",
            linewidth=2.5,
            marker="o",
            markersize=5,
            label="Mean Connectivity",
        )

        ax.set_xlabel("Date", fontsize=12, fontweight="bold")
        ax.set_ylabel("Connectivity (m)", fontsize=12, fontweight="bold")
        ax.set_title("Lateral Connectivity Time Series", fontsize=14, fontweight="bold")
        ax.legend(loc="best", fontsize=10)
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate(rotation=45, ha="right")
        plt.tight_layout()

        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=self.dpi, bbox_inches="tight")

        if self.show:
            plt.show()

    def plot_patch_size_distribution(
        self, landscape_metrics: pd.DataFrame, output_file: Path | None = None
    ) -> None:
        """
        Plot patch size distribution over time.

        Parameters
        ----------
        landscape_metrics : DataFrame
            Landscape metrics with columns: date, mean_area_m2, p10_area_m2, p50_area_m2, p90_area_m2
        output_file : Path, optional
            Path to save figure (e.g., 'patch_size_distribution.png')

        Raises
        ------
        ValueError
            If required columns are missing

        Notes
        -----
        Creates line plot showing percentile distribution of patch sizes over time.
        Shows mean, 10th, 50th, and 90th percentiles.
        """
        # Check for required columns
        required_cols = [
            "date",
            "mean_area_m2",
            "p10_area_m2",
            "p50_area_m2",
            "p90_area_m2",
        ]
        missing = [col for col in required_cols if col not in landscape_metrics.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        metrics_sorted = landscape_metrics.sort_values("date")

        # Plot percentiles
        ax.plot(
            metrics_sorted["date"],
            metrics_sorted["p90_area_m2"],
            color="lightcoral",
            linewidth=2,
            linestyle="--",
            label="90th percentile",
        )
        ax.plot(
            metrics_sorted["date"],
            metrics_sorted["p50_area_m2"],
            color="orange",
            linewidth=2.5,
            label="Median (50th percentile)",
        )
        ax.plot(
            metrics_sorted["date"],
            metrics_sorted["p10_area_m2"],
            color="steelblue",
            linewidth=2,
            linestyle="--",
            label="10th percentile",
        )
        ax.plot(
            metrics_sorted["date"],
            metrics_sorted["mean_area_m2"],
            color="darkgreen",
            linewidth=2.5,
            marker="o",
            markersize=5,
            label="Mean",
        )

        ax.set_xlabel("Date", fontsize=12, fontweight="bold")
        ax.set_ylabel("Patch Area (m²)", fontsize=12, fontweight="bold")
        ax.set_title(
            "Patch Size Distribution Over Time", fontsize=14, fontweight="bold"
        )
        ax.legend(loc="best", fontsize=10)
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate(rotation=45, ha="right")
        plt.tight_layout()

        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=self.dpi, bbox_inches="tight")

        if self.show:
            plt.show()

    def plot_core_area_distribution(
        self, landscape_metrics: pd.DataFrame, output_file: Path | None = None
    ) -> None:
        """
        Plot core area distribution over time.

        Parameters
        ----------
        landscape_metrics : DataFrame
            Landscape metrics with columns: date, mean_core_area_m2, p10_core_area_m2, p50_core_area_m2, p90_core_area_m2
        output_file : Path, optional
            Path to save figure (e.g., 'core_area_distribution.png')

        Raises
        ------
        ValueError
            If required columns are missing

        Notes
        -----
        Creates line plot showing percentile distribution of core areas over time.
        Core area represents interior habitat excluding edge effects.
        """
        # Check for required columns
        required_cols = [
            "date",
            "mean_core_area_m2",
            "p10_core_area_m2",
            "p50_core_area_m2",
            "p90_core_area_m2",
        ]
        missing = [col for col in required_cols if col not in landscape_metrics.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        metrics_sorted = landscape_metrics.sort_values("date")

        # Plot percentiles
        ax.plot(
            metrics_sorted["date"],
            metrics_sorted["p90_core_area_m2"],
            color="lightcoral",
            linewidth=2,
            linestyle="--",
            label="90th percentile",
        )
        ax.plot(
            metrics_sorted["date"],
            metrics_sorted["p50_core_area_m2"],
            color="orange",
            linewidth=2.5,
            label="Median (50th percentile)",
        )
        ax.plot(
            metrics_sorted["date"],
            metrics_sorted["p10_core_area_m2"],
            color="steelblue",
            linewidth=2,
            linestyle="--",
            label="10th percentile",
        )
        ax.plot(
            metrics_sorted["date"],
            metrics_sorted["mean_core_area_m2"],
            color="darkgreen",
            linewidth=2.5,
            marker="o",
            markersize=5,
            label="Mean",
        )

        ax.set_xlabel("Date", fontsize=12, fontweight="bold")
        ax.set_ylabel("Core Area (m²)", fontsize=12, fontweight="bold")
        ax.set_title("Core Area Distribution Over Time", fontsize=14, fontweight="bold")
        ax.legend(loc="best", fontsize=10)
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate(rotation=45, ha="right")
        plt.tight_layout()

        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=self.dpi, bbox_inches="tight")

        if self.show:
            plt.show()

    def plot_comparative_sensors(
        self,
        s1_data: pd.DataFrame,
        s2_data: pd.DataFrame,
        output_file: Path | None = None,
    ) -> None:
        """
        Compare results between Sentinel-1 and Sentinel-2.

        Parameters
        ----------
        s1_data : DataFrame
            Sentinel-1 analysis results with columns: date, inundated_area_ha
        s2_data : DataFrame
            Sentinel-2 analysis results with columns: date, inundated_area_ha
        output_file : Path, optional
            Path to save figure (e.g., 'sentinel_comparison.png')

        Raises
        ------
        ValueError
            If required columns are missing

        Notes
        -----
        Creates dual-axis comparison plot showing Sentinel-1 and Sentinel-2 results.
        Useful for validating water classification across sensors.
        """
        # Check for required columns
        required_cols = ["date", "inundated_area_ha"]
        for data, name in [(s1_data, "s1_data"), (s2_data, "s2_data")]:
            missing = [col for col in required_cols if col not in data.columns]
            if missing:
                raise ValueError(f"{name} missing required columns: {missing}")

        fig, ax1 = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        s1_sorted = s1_data.sort_values("date")
        s2_sorted = s2_data.sort_values("date")

        # Plot Sentinel-1 on left axis
        color1 = "steelblue"
        ax1.set_xlabel("Date", fontsize=12, fontweight="bold")
        ax1.set_ylabel(
            "Sentinel-1 Area (ha)", fontsize=12, fontweight="bold", color=color1
        )
        line1 = ax1.plot(
            s1_sorted["date"],
            s1_sorted["inundated_area_ha"],
            color=color1,
            linewidth=2.5,
            marker="o",
            markersize=5,
            label="Sentinel-1",
        )
        ax1.tick_params(axis="y", labelcolor=color1)
        ax1.grid(True, alpha=0.3)

        # Plot Sentinel-2 on right axis
        ax2 = ax1.twinx()
        color2 = "coral"
        ax2.set_ylabel(
            "Sentinel-2 Area (ha)", fontsize=12, fontweight="bold", color=color2
        )
        line2 = ax2.plot(
            s2_sorted["date"],
            s2_sorted["inundated_area_ha"],
            color=color2,
            linewidth=2.5,
            marker="s",
            markersize=5,
            label="Sentinel-2",
        )
        ax2.tick_params(axis="y", labelcolor=color2)

        # Title and legend
        fig.suptitle(
            "Sentinel-1 vs Sentinel-2 Comparison", fontsize=14, fontweight="bold"
        )
        lines = line1 + line2
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc="upper left", fontsize=10)  # type: ignore

        fig.autofmt_xdate(rotation=45, ha="right")
        plt.tight_layout()

        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=self.dpi, bbox_inches="tight")

        if self.show:
            plt.show()
