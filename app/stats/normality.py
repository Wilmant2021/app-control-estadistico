"""
Normality testing module.
Provides functions to test data normality using various statistical tests.
"""

import streamlit as st
import pandas as pd


def shapiro_wilk_test(data: pd.DataFrame, column: str) -> tuple:
    """
    Performs Shapiro-Wilk test for normality.
    
    Args:
        data (pd.DataFrame): DataFrame containing measurement data
        column (str): Name of the column to test
        
    Returns:
        tuple: (statistic, p_value) test results
    """
    pass


def anderson_darling_test(data: pd.DataFrame, column: str) -> dict:
    """
    Performs Anderson-Darling test for normality.
    
    Args:
        data (pd.DataFrame): DataFrame containing measurement data
        column (str): Name of the column to test
        
    Returns:
        dict: Test results including statistic and critical values
    """
    pass


def plot_qq_plot(data: pd.DataFrame, column: str):
    """
    Generates a Q-Q plot to visually assess normality.
    
    Args:
        data (pd.DataFrame): DataFrame containing measurement data
        column (str): Name of the column to plot
    """
    pass


def plot_histogram(data: pd.DataFrame, column: str):
    """
    Generates a histogram with normal distribution overlay.
    
    Args:
        data (pd.DataFrame): DataFrame containing measurement data
        column (str): Name of the column to plot
    """
    pass
