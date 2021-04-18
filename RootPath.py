import pathlib as pl
import os


def get_root():
    return pl.Path(__file__).parent.absolute()

