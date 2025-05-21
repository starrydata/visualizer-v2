import streamlit as st

def main():
    st.set_page_config(page_title="Visualizer 2", page_icon="🚀")
    st.title("Welcome to the Material Data Viewer")

    st.markdown("""
    ## How to use this app

    1. Select a material type from the sidebar menu.
    2. The default graph for the selected material will be displayed.
    3. You can choose different graphs or highlight specific data by selecting dates.
    4. Explore and analyze the material data interactively.

    Enjoy your data exploration!
    """)

if __name__ == "__main__":
    main()
