import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Page Title/Icon
st.set_page_config(
    page_title="World Population Dashboard",
    page_icon="🌍",
    layout="wide",
)

# Load data
def load_data():
    population_url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world_population.csv"
    geojson_url = "https://raw.githubusercontent.com/tommyscodebase/12_Days_Geospatial_Python_Bootcamp/refs/heads/main/13_final_project_data/world.geojson"

    population_data = pd.read_csv(population_url)
    geojson_data = gpd.read_file(geojson_url)

    return population_data, geojson_data


population_data, geojson_data = load_data()

# Page title and description
st.title("My First Dashboard: Global Population Explorer")
st.write("Select a country to view its population data and geographical information.")

# Dropdown for country selection
countries = sorted(population_data['Country/Territory'].unique())
selected_country = st.selectbox("Select a Country", options=[""] + countries, format_func=lambda x: "Select a Country" if x == "" else x)

# Conditional display
if not selected_country:
    st.info("Please select a country to view its data.")
else:
    # Filter data for the selected country
    country_data = population_data[population_data['Country/Territory'] == selected_country]

    # Check if `country_data` is empty
    if country_data.empty:
        st.warning(f"No data available for {selected_country}.")
    else:
        col1, col2 = st.columns([0.6, 0.4])

        with col1:
            # Population chart
            st.subheader("Population Over Selected Years")
            selected_years = st.multiselect(
                "Select Population Years",
                options=[
                    '1970 Population', '1980 Population', '1990 Population',
                    '2000 Population', '2010 Population', '2015 Population',
                    '2020 Population', '2022 Population'
                ],
                default=['1990 Population', '2000 Population', '2010 Population', '2015 Population', '2020 Population']
            )
            if selected_years:
            # Prepare data for plotting
                chart_data = country_data[selected_years].T.reset_index()
                chart_data.columns = ['Year', 'Population']
                chart_data['Year'] = chart_data['Year'].str.replace(" Population", "")
                fig = px.bar(
                    chart_data,
                    x='Year',
                    y='Population',
                    title=f"Population of {selected_country} Over Selected Years",
                    labels={'Population': 'Population'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Display statistics
            st.subheader("Country Statistics")
            area = country_data['Area (km²)'].values[0]
            density = country_data['Density (per km²)'].values[0]
            growth_rate = country_data['Growth Rate'].values[0]
            world_percentage = country_data['World Population Percentage'].values[0]

            st.write(f"**Area (km²):** {area} km²")
            st.write(f"**Density (per km²):** {density} people/km²")
            st.write(f"**Growth Rate:** {growth_rate} %")
            st.write(f"**World Population Percentage:** {world_percentage} %")

            # Map visualization
            st.subheader("Country Map")
            country_geometry = geojson_data[geojson_data['name'] == selected_country]

            if not country_geometry.empty:
                centroid = country_geometry.geometry.centroid.iloc[0]
                m = folium.Map(location=[country_geometry.geometry.centroid.y.values[0],
                                    country_geometry.geometry.centroid.x.values[0]], zoom_start=4)
                folium.GeoJson(country_geometry).add_to(m)
                st_folium(m, width=520, height=300)
            else:
                st.warning("No geographical data available for this country.")
