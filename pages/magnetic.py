import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from domain.material_type import MaterialType
import streamlit as st
import presentation.material_page as material_page

def main():
    material_page.main(MaterialType.MAGNETIC)

if __name__ == "__main__":
    main()
