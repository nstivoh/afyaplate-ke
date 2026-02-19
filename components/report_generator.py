# filepath: components/report_generator.py
import streamlit as st
from core.pdf_report import generate_report
import datetime

def show_report_generator():
    """
    Renders the UI for generating and downloading client reports.
    """
    st.header("📄 Client Report Generator")
    st.write("Create a professional PDF report for your clients, including their personalized meal plan.")

    # Check if a meal plan exists in session state
    if 'meal_plan' not in st.session_state or not st.session_state.meal_plan:
        st.warning("No active meal plan found. Please generate a plan in the 'AI Meal Planner' tab first.", icon="🍽️")
        return

    st.subheader("1. Enter Client Details")
    with st.form("client_details_form"):
        client_name = st.text_input("Client Full Name", "Jane Doe")
        client_age = st.number_input("Client Age", 1, 100, 35)
        
        # Pull condition from the last meal plan generation if available
        last_condition = st.session_state.get('last_user_inputs', {}).get('condition', "General Wellness")
        client_condition = st.text_input("Diagnosis / Health Goal", last_condition)

        submit_client_details = st.form_submit_button("Preview Report Details")

    if submit_client_details:
        st.session_state.client_info_for_report = {
            "name": client_name,
            "age": client_age,
            "condition": client_condition
        }
        st.success("Client details saved for the report.")


    if 'client_info_for_report' in st.session_state:
        st.divider()
        st.subheader("2. Review and Generate PDF")
        
        client_info = st.session_state.client_info_for_report
        meal_plan = st.session_state.meal_plan
        
        st.write("The following details will be included in the report:")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"- **Client:** {client_info['name']}, Age {client_info['age']}")
            st.markdown(f"- **Goal:** {client_info['condition']}")
        with col2:
            st.markdown(f"- **Plan Length:** {len(meal_plan['days'])} days")
            st.markdown(f"- **Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d')}")
            

        st.info("The currently active meal plan from the 'AI Meal Planner' tab will be used in this report.", icon="ℹ️")

        if st.button("Generate PDF Report", use_container_width=True, type="primary"):
            with st.spinner("Creating your PDF report..."):
                pdf_bytes = generate_report(client_info, meal_plan)

            if pdf_bytes:
                st.success("Your report has been generated!")
                
                file_name = f"AfyaPlate_Report_{client_info['name'].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=file_name,
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("Failed to generate the PDF. Please check the logs for errors.")
```