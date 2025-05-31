import sys
import os

from src.domain.material_type import MaterialType
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
import streamlit as st
import src.presentation.material_page as material_page

def main():
    material_page.main(MaterialType.BATTERY)

if __name__ == "__main__":
    main()
