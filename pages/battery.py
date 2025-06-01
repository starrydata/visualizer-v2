import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from src.domain.material_type import MaterialType
import streamlit as st
import src.presentation.material_page as material_page

def main():
    material_page.main(MaterialType.BATTERY)

if __name__ == "__main__":
    main()
