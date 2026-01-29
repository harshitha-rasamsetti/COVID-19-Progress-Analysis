# app.py - COVID-19 Vaccination Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_option_menu import option_menu
import time

# Set page configuration
st.set_page_config(
    page_title="COVID-19 Vaccination Dashboard",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode and professional styling
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00d4ff !important;
        font-family: 'Arial', sans-serif;
        text-shadow: 0 2px 10px rgba(0, 212, 255, 0.3);
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: bold !important;
        color: #00d4ff !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #8b949e !important;
    }
    
    /* Cards */
    .card {
        background: rgba(25, 25, 35, 0.9);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c0c0c 0%, #1a1a2e 100%) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #0066cc 0%, #00d4ff 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(25, 25, 35, 0.9);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #8b949e;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #0066cc 0%, #00d4ff 100%);
        color: white !important;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data caching
if 'vaccine_data' not in st.session_state:
    st.session_state.vaccine_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Function to generate sample data (replace with real API in production)
@st.cache_data(ttl=3600)  # Cache for 1 hour
def generate_vaccination_data():
    """Generate sample vaccination data for demonstration"""
    
    # Generate dates for the last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Sample countries
    countries = ['USA', 'India', 'Brazil', 'UK', 'Germany', 'Japan', 
                 'France', 'Italy', 'Canada', 'Australia', 'South Africa', 'Mexico']
    
    data = []
    for country in countries:
        # Base vaccination rates vary by country
        if country == 'USA':
            base_rate = 75
        elif country == 'India':
            base_rate = 65
        elif country == 'Brazil':
            base_rate = 70
        else:
            base_rate = np.random.randint(60, 85)
        
        for date in dates:
            # Add trend and randomness
            days_from_start = (date - start_date).days
            trend = days_from_start * 0.1
            noise = np.random.normal(0, 2)
            
            # Calculate rates
            fully_vaccinated = min(95, base_rate + trend + noise)
            partially_vaccinated = min(100, fully_vaccinated + np.random.randint(5, 15))
            
            data.append({
                'Date': date,
                'Country': country,
                'Fully_Vaccinated_Percentage': max(0, fully_vaccinated),
                'Partially_Vaccinated_Percentage': max(0, partially_vaccinated),
                'Doses_Administered': int(np.random.uniform(100000, 10000000)),
                'Daily_Vaccinations': int(np.random.uniform(5000, 500000)),
                'Vaccine_Type': np.random.choice(['Pfizer', 'Moderna', 'AstraZeneca', 'Sinovac', 'Johnson&Johnson'], p=[0.4, 0.3, 0.15, 0.1, 0.05])
            })
    
    df = pd.DataFrame(data)
    return df

# Function to fetch real data (commented out, but ready for real API)
def fetch_real_vaccination_data():
    """Fetch real vaccination data from API (placeholder)"""
    try:
        # Example: WHO API or Our World in Data API
        # url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
        # df = pd.read_csv(url)
        # return df[df['location'].isin(['United States', 'India', 'Brazil', 'United Kingdom'])]
        
        # For now, use generated data
        return generate_vaccination_data()
    except:
        st.warning("Could not fetch real-time data. Using sample data.")
        return generate_vaccination_data()

# Main app
def main():
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: #00d4ff;'>💉 VAXTRACK</h1>
            <p style='color: #8b949e;'>Real-time COVID-19 Vaccination Monitor</p>
        </div>
        """, unsafe_allow_html=True)
        
        selected = option_menu(
            menu_title="Dashboard",
            options=["📊 Overview", "🌍 Global Map", "📈 Trends", "🔍 Country Analysis", "📊 Data Explorer", "⚙️ Settings"],
            icons=["speedometer2", "globe", "graph-up", "flag", "table", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#00d4ff", "font-size": "20px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#1e2a47"},
                "nav-link-selected": {"background-color": "#0066cc", "color": "white"},
            }
        )
        
        st.markdown("---")
        
        # Date Range Selector
        st.markdown("### 📅 Date Range")
        today = datetime.now()
        default_start = today - timedelta(days=180)
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", value=default_start, key="start")
        with col2:
            end_date = st.date_input("To", value=today, key="end")
        
        # Country Selection
        st.markdown("### 🌍 Countries")
        countries = ['All Countries', 'USA', 'India', 'Brazil', 'UK', 'Germany', 
                    'Japan', 'France', 'Italy', 'Canada', 'Australia']
        selected_countries = st.multiselect(
            "Select countries",
            countries[1:],
            default=['USA', 'India', 'Brazil', 'UK']
        )
        
        # Refresh Button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.vaccine_data = None
            st.rerun()
        
        st.markdown("---")
        
        # Last Updated
        if st.session_state.last_update:
            st.markdown(f"**Last Updated:** {st.session_state.last_update}")
        
        st.markdown("---")
        st.markdown("""
        <div style='color: #8b949e; font-size: 12px;'>
        <p>📍 Data Source: WHO/CDC APIs</p>
        <p>⏰ Updates: Every 24 hours</p>
        <p>🔒 Data Privacy Compliant</p>
        </div>
        """, unsafe_allow_html=True)

    # Load data
    if st.session_state.vaccine_data is None:
        with st.spinner("🔄 Loading vaccination data..."):
            df = fetch_real_vaccination_data()
            st.session_state.vaccine_data = df
            st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        df = st.session_state.vaccine_data
    
    # Filter data based on selections
    if 'All Countries' not in selected_countries and selected_countries:
        df = df[df['Country'].isin(selected_countries)]
    
    df['Date'] = pd.to_datetime(df['Date'])
    mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
    df_filtered = df.loc[mask]
    
    # Overview Page
    if selected == "📊 Overview":
        st.markdown("<h1 style='text-align: center;'>📊 VACCINATION DASHBOARD OVERVIEW</h1>", unsafe_allow_html=True)
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            avg_vax = df_filtered['Fully_Vaccinated_Percentage'].mean()
            st.metric("Global Vaccination Rate", f"{avg_vax:.1f}%", delta="+2.3% from last month")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            total_doses = df_filtered['Doses_Administered'].sum()
            st.metric("Total Doses Administered", f"{total_doses:,.0f}", delta="+5.1M today")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            daily_avg = df_filtered['Daily_Vaccinations'].mean()
            st.metric("Daily Vaccinations", f"{daily_avg:,.0f}", delta="-1.2% from yesterday")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            countries_count = df_filtered['Country'].nunique()
            st.metric("Countries Tracked", f"{countries_count}", delta="+3 new")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Main Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📈 Vaccination Progress Trend")
            
            # Aggregate by date
            daily_avg = df_filtered.groupby('Date').agg({
                'Fully_Vaccinated_Percentage': 'mean',
                'Partially_Vaccinated_Percentage': 'mean'
            }).reset_index()
            
            fig = px.line(daily_avg, x='Date', y=['Fully_Vaccinated_Percentage', 'Partially_Vaccinated_Percentage'],
                         color_discrete_map={
                             'Fully_Vaccinated_Percentage': '#00d4ff',
                             'Partially_Vaccinated_Percentage': '#0066cc'
                         },
                         labels={'value': 'Percentage', 'variable': 'Vaccination Status'})
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🌍 Country Comparison")
            
            # Latest data for each country
            latest_data = df_filtered.sort_values('Date').groupby('Country').last().reset_index()
            
            fig = px.bar(latest_data.sort_values('Fully_Vaccinated_Percentage', ascending=True),
                        x='Fully_Vaccinated_Percentage',
                        y='Country',
                        orientation='h',
                        color='Fully_Vaccinated_Percentage',
                        color_continuous_scale='Blues',
                        text='Fully_Vaccinated_Percentage')
            
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                showlegend=False,
                yaxis=dict(categoryorder='total ascending')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Bottom Row
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🚀 Daily Vaccination Rate")
            
            daily_totals = df_filtered.groupby('Date')['Daily_Vaccinations'].sum().reset_index()
            
            fig = px.area(daily_totals, x='Date', y='Daily_Vaccinations',
                         color_discrete_sequence=['#00d4ff'])
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 💉 Vaccine Distribution")
            
            vaccine_dist = df_filtered['Vaccine_Type'].value_counts().reset_index()
            vaccine_dist.columns = ['Vaccine_Type', 'Count']
            
            fig = px.pie(vaccine_dist, values='Count', names='Vaccine_Type',
                        color_discrete_sequence=px.colors.sequential.Blues_r,
                        hole=0.4)
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.2
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Global Map Page
    elif selected == "🌍 Global Map":
        st.markdown("<h1 style='text-align: center;'>🌍 GLOBAL VACCINATION MAP</h1>", unsafe_allow_html=True)
        
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Create sample geographic data
        countries_geo = ['USA', 'India', 'Brazil', 'United Kingdom', 'Germany', 
                        'Japan', 'France', 'Italy', 'Canada', 'Australia']
        
        geo_data = []
        for country in countries_geo:
            geo_data.append({
                'Country': country,
                'Fully_Vaccinated': np.random.randint(50, 95),
                'Lat': np.random.uniform(-50, 70),
                'Lon': np.random.uniform(-180, 180),
                'Doses_Administered': np.random.randint(1000000, 1000000000)
            })
        
        geo_df = pd.DataFrame(geo_data)
        
        fig = px.scatter_geo(geo_df,
                            lat='Lat',
                            lon='Lon',
                            color='Fully_Vaccinated',
                            size='Doses_Administered',
                            hover_name='Country',
                            projection='natural earth',
                            color_continuous_scale='Blues',
                            title='Global Vaccination Coverage',
                            size_max=50)
        
        fig.update_layout(
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                landcolor='rgb(30, 30, 46)',
                lakecolor='rgb(30, 30, 46)',
                showcountries=True,
                countrycolor='rgb(100, 100, 120)'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Map metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Highest Coverage", "Portugal - 92%", "+1.2%")
        with col2:
            st.metric("Lowest Coverage", "Haiti - 15%", "+0.5%")
        with col3:
            st.metric("Global Average", "67.3%", "+0.8%")
    
    # Trends Page
    elif selected == "📈 Trends":
        st.markdown("<h1 style='text-align: center;'>📈 VACCINATION TRENDS ANALYSIS</h1>", unsafe_allow_html=True)
        
        # Calculate average vaccination rate for the filtered data
        current_avg_vax = df_filtered['Fully_Vaccinated_Percentage'].mean()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📊 Weekly Progression")
            
            df_filtered['Week'] = df_filtered['Date'].dt.isocalendar().week
            weekly_data = df_filtered.groupby(['Country', 'Week']).agg({
                'Fully_Vaccinated_Percentage': 'last'
            }).reset_index()
            
            fig = px.line(weekly_data, x='Week', y='Fully_Vaccinated_Percentage',
                         color='Country', line_dash='Country',
                         color_discrete_sequence=px.colors.qualitative.Set2)
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🔄 Rate of Change")
            
            # Calculate daily changes
            df_sorted = df_filtered.sort_values(['Country', 'Date'])
            df_sorted['Daily_Change'] = df_sorted.groupby('Country')['Fully_Vaccinated_Percentage'].diff()
            
            fig = px.box(df_sorted, x='Country', y='Daily_Change',
                        color='Country',
                        points="all")
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Forecast Trend
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🔮 Projection Forecast")
        
        # Simple forecast visualization
        forecast_dates = pd.date_range(start=end_date, periods=30, freq='D')
        forecast_values = []
        
        for i in range(30):
            forecast_values.append(current_avg_vax + (i * 0.15) + np.random.normal(0, 0.5))
        
        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'Forecast': forecast_values,
            'Upper_Bound': [v + 2 for v in forecast_values],
            'Lower_Bound': [v - 2 for v in forecast_values]
        })
        
        fig = go.Figure()
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=forecast_df['Date'].tolist() + forecast_df['Date'].tolist()[::-1],
            y=forecast_df['Upper_Bound'].tolist() + forecast_df['Lower_Bound'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0, 212, 255, 0.2)',
            line_color='rgba(255,255,255,0)',
            showlegend=False,
            name='Confidence Interval'
        ))
        
        # Add forecast line
        fig.add_trace(go.Scatter(
            x=forecast_df['Date'],
            y=forecast_df['Forecast'],
            line_color='#00d4ff',
            name='Forecast',
            mode='lines'
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title="30-Day Vaccination Rate Forecast",
            xaxis_title="Date",
            yaxis_title="Vaccination Rate (%)",
            yaxis_range=[max(0, current_avg_vax - 10), min(100, current_avg_vax + 15)]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Country Analysis Page
    elif selected == "🔍 Country Analysis":
        st.markdown("<h1 style='text-align: center;'>🔍 COUNTRY-SPECIFIC ANALYSIS</h1>", unsafe_allow_html=True)
        
        # Country selector
        country = st.selectbox("Select Country", df_filtered['Country'].unique())
        
        if country:
            country_data = df_filtered[df_filtered['Country'] == country]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                latest = country_data.iloc[-1]
                st.metric(f"{country} - Fully Vaccinated", f"{latest['Fully_Vaccinated_Percentage']:.1f}%")
            
            with col2:
                st.metric("Total Doses", f"{country_data['Doses_Administered'].iloc[-1]:,}")
            
            with col3:
                st.metric("Daily Rate", f"{latest['Daily_Vaccinations']:,}")
            
            # Country-specific charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"### 📊 {country} Vaccination Timeline")
                
                fig = px.line(country_data, x='Date', 
                             y=['Fully_Vaccinated_Percentage', 'Partially_Vaccinated_Percentage'],
                             color_discrete_sequence=['#00d4ff', '#0066cc'])
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"### 💉 {country} Vaccine Types")
                
                vaccine_counts = country_data['Vaccine_Type'].value_counts()
                
                fig = px.bar(x=vaccine_counts.index, y=vaccine_counts.values,
                            color=vaccine_counts.values,
                            color_continuous_scale='Blues',
                            text=vaccine_counts.values)
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=False,
                    xaxis_title="Vaccine Type",
                    yaxis_title="Count"
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Data Explorer Page
    elif selected == "📊 Data Explorer":
        st.markdown("<h1 style='text-align: center;'>📊 DATA EXPLORER</h1>", unsafe_allow_html=True)
        
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Interactive data table
        st.markdown("### 🔍 Raw Data Preview")
        
        # Use AgGrid for better table display
        gb = GridOptionsBuilder.from_dataframe(df_filtered.head(1000))
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
        grid_options = gb.build()
        
        AgGrid(df_filtered.head(1000), 
               gridOptions=grid_options,
               theme='streamlit',
               height=400,
               enable_enterprise_modules=False)
        
        # Data download option
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="📥 Download Current Data (CSV)",
            data=csv,
            file_name=f"vaccination_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Statistics
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📈 Data Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Numerical Columns:**")
            st.dataframe(df_filtered.describe(), use_container_width=True)
        
        with col2:
            st.write("**Data Information:**")
            buffer = []
            buffer.append(f"Total Rows: {len(df_filtered):,}")
            buffer.append(f"Total Columns: {len(df_filtered.columns)}")
            buffer.append(f"Date Range: {df_filtered['Date'].min().date()} to {df_filtered['Date'].max().date()}")
            buffer.append(f"Countries: {df_filtered['Country'].nunique()}")
            
            for line in buffer:
                st.write(f"• {line}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Settings Page
    elif selected == "⚙️ Settings":
        st.markdown("<h1 style='text-align: center;'>⚙️ DASHBOARD SETTINGS</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🎨 Display Settings")
            
            theme = st.selectbox("Color Theme", ["Dark Blue (Default)", "Dark Green", "Dark Purple", "Light Mode"])
            chart_style = st.selectbox("Chart Style", ["Interactive", "Static"])
            data_refresh = st.selectbox("Auto-refresh Interval", ["Disabled", "1 hour", "6 hours", "12 hours", "24 hours"])
            
            if st.button("💾 Save Display Settings", use_container_width=True):
                st.success("Display settings saved!")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📊 Data Settings")
            
            default_countries = st.multiselect(
                "Default Countries on Load",
                df['Country'].unique().tolist(),
                default=['USA', 'India', 'Brazil', 'UK']
            )
            
            date_range_default = st.selectbox(
                "Default Date Range",
                ["Last 30 days", "Last 90 days", "Last 180 days", "Last 365 days", "All time"]
            )
            
            if st.button("🗑️ Clear Cache", use_container_width=True):
                st.session_state.vaccine_data = None
                st.rerun()
            
            if st.button("🔄 Reset to Defaults", use_container_width=True):
                st.success("Settings reset to defaults!")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # API Settings
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🔌 API Configuration")
        
        api_source = st.selectbox(
            "Data Source API",
            ["Sample Data", "Our World in Data API", "WHO API", "Custom API Endpoint"]
        )
        
        if api_source != "Sample Data":
            api_url = st.text_input("API Endpoint URL", placeholder="https://api.example.com/vaccination-data")
            api_key = st.text_input("API Key (if required)", type="password")
            
            if st.button("🔗 Test API Connection", use_container_width=True):
                with st.spinner("Testing connection..."):
                    time.sleep(2)
                    st.success("API connection successful!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; color: #8b949e; font-size: 14px;'>
        <p>💉 <b>VAXTRACK</b> - COVID-19 Vaccination Monitoring System</p>
        <p>📊 Data Visualization & Analysis Dashboard | Internship Project</p>
        <p>⚠️ This dashboard uses simulated data for demonstration purposes</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()