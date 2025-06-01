import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
import streamlit as st
import presentation.material_page as material_page
from domain.material_type import MaterialType

def main():
    material_page.main(MaterialType.THERMOELECTRIC)

if __name__ == "__main__":
    main()
