# filepath: components/food_search.py
import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
import plotly.express as px

def show_food_search(food_df: pd.DataFrame):
    """
    Renders the Food Search UI component.

    Args:
        food_df (pd.DataFrame): The dataframe containing food composition data.
    """
    if food_df.empty:
        st.warning("Food data is not loaded. Go to Settings to extract it.")
        return

    st.header("🔍 Food Composition Search")
    st.write("Search the Kenyan Food Composition Tables. Use the filters in the sidebar to narrow down your results.")

    # --- Sidebar Filters ---
    with st.sidebar:
        st.header("Search & Filters")
        
        # Search Box
        search_query = st.text_input("Search by food name (English or Swahili)", "")

        # Category Filter
        categories = ["All"] + sorted(food_df['category'].unique())
        selected_category = st.selectbox("Filter by Category", categories)

        # Nutrient Filters
        st.subheader("Nutrient Range Sliders")
        
        # Selectbox to choose nutrient for sliders to avoid clutter
        available_nutrients = ['energy_kcal', 'protein_g', 'fat_g', 'carbs_g', 'fibre_g', 'calcium_mg', 'iron_mg', 'zinc_mg']
        
        primary_nutrient = st.selectbox("Primary Nutrient to Filter", available_nutrients, index=1) # Default to protein
        
        min_val = float(food_df[primary_nutrient].min())
        max_val = float(food_df[primary_nutrient].max())
        
        if min_val < max_val:
            nutrient_range = st.slider(
                f"Range for {primary_nutrient}",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val)
            )
        else:
            st.info("Not enough data to create a range slider for this nutrient.")
            nutrient_range = (min_val, max_val)
            
    # --- Filtering Logic ---
    filtered_df = food_df.copy()

    # 1. Category Filter
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]

    # 2. Nutrient Filter
    if nutrient_range and (nutrient_range[0] > min_val or nutrient_range[1] < max_val):
        filtered_df = filtered_df[
            (filtered_df[primary_nutrient] >= nutrient_range[0]) &
            (filtered_df[primary_nutrient] <= nutrient_range[1])
        ]

    # 3. Fuzzy Search
    if search_query:
        # Combine English and Swahili names for a comprehensive search
        # In a real app, 'food_name_swahili' would be populated
        searchable_series = filtered_df['food_name_english'].fillna('') # + " " + filtered_df['food_name_swahili'].fillna('')
        
        # Use rapidfuzz to find best matches
        extracted_matches = process.extract(search_query, searchable_series, scorer=fuzz.WRatio, limit=len(filtered_df))
        
        # Get indices of good matches (score > 75)
        matched_indices = [index for _, score, index in extracted_matches if score > 75]
        
        # Re-create a dataframe from the matched indices
        filtered_df = filtered_df.loc[matched_indices] if matched_indices else pd.DataFrame(columns=filtered_df.columns)

    # --- Display Results ---
    st.subheader("Search Results")

    if filtered_df.empty:
        st.info("No food items match your current search and filter criteria.")
    else:
        # Portion Size Selector
        col1, col2 = st.columns([1, 3])
        with col1:
            portion_size = st.number_input("Portion Size (in grams)", min_value=1, value=100, step=10)
        
        display_df = filtered_df.copy()
        
        # Adjust nutrients for portion size
        nutrient_cols = [col for col in available_nutrients if col in display_df.columns]
        for col in nutrient_cols:
            display_df[col] = (display_df[col] / 100) * portion_size

        # --- Data Display and Export ---
        st.dataframe(
            display_df[['food_name_english', 'category'] + nutrient_cols],
            use_container_width=True,
            hide_index=True
        )

        st.info(f"Nutrient values adjusted for a {portion_size}g portion. Displaying {len(display_df)} of {len(food_df)} total foods.")

        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df_to_csv(display_df)
        st.download_button(
            label="📥 Export Results to CSV",
            data=csv,
            file_name=f"afyaplate_search_results_{portion_size}g.csv",
            mime="text/csv",
        )

        # --- Visualization ---
        if not display_df.empty and len(display_df) > 1:
            st.subheader("Visual Comparison")
            
            graph_nutrient = st.selectbox(
                "Select nutrient to visualize:",
                options=nutrient_cols,
                index=1 # protein_g
            )
            
            # Show top 15 results to avoid clutter
            top_15_df = display_df.nlargest(15, graph_nutrient)

            fig = px.bar(
                top_15_df,
                x=graph_nutrient,
                y='food_name_english',
                orientation='h',
                title=f'Top {len(top_15_df)} Foods by {graph_nutrient} (for {portion_size}g portion)',
                labels={'food_name_english': 'Food Item'},
                color_discrete_sequence=px.colors.qualitative.Pastel1
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
```