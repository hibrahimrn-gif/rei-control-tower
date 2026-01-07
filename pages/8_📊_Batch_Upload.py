"""
REI Nationwide LLC - Batch Deal Upload & Analysis
Upload CSV file with multiple deals for batch underwriting
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add components to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.batch_processor import (
    process_batch_csv,
    get_batch_summary_stats,
    export_batch_results_to_csv,
    create_csv_template
)

# Page configuration
st.set_page_config(
    page_title="Batch Upload - REI Nationwide",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .green-row { background-color: rgba(16, 185, 129, 0.1); }
    .yellow-row { background-color: rgba(245, 158, 11, 0.1); }
    .red-row { background-color: rgba(239, 68, 68, 0.1); }
</style>
""", unsafe_allow_html=True)


def main():
    """Main batch upload page"""

    st.title("📊 Batch Deal Upload & Analysis")
    st.markdown("*Upload CSV file with multiple deals for batch underwriting*")

    st.markdown("---")

    # Instructions
    with st.expander("ℹ️ How to Use Batch Upload", expanded=False):
        st.markdown("""
        **Upload a CSV file with multiple deals to analyze them all at once.**

        **Required CSV Columns:**
        - `address` - Property address
        - `arv` - After Repair Value
        - `purchase_price` - Offer price
        - `rehab_budget` - Estimated rehab cost
        - `estimated_rent` - Monthly rent estimate

        **Optional Columns:**
        - `sqft` - Square footage
        - `bedrooms` - Number of bedrooms
        - `bathrooms` - Number of bathrooms
        - `holding_months` - Holding period (default: 2.0)
        - `notes` - Additional notes

        **Process:**
        1. Download CSV template below
        2. Fill in your deals
        3. Upload CSV
        4. Review batch results
        5. Export analyzed results
        """)

    # Download template
    st.markdown("### 📥 Download CSV Template")

    col1, col2 = st.columns(2)

    with col1:
        template_csv = create_csv_template()
        st.download_button(
            label="📄 Download CSV Template",
            data=template_csv,
            file_name="rei_batch_template.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        st.info("Download the template, fill in your deals, then upload below")

    st.markdown("---")

    # File upload
    st.markdown("### 📤 Upload CSV File")

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload CSV file with deal data"
    )

    if uploaded_file is not None:
        try:
            # Process CSV
            with st.spinner("Processing batch deals..."):
                results, summary_df = process_batch_csv(uploaded_file)
                stats = get_batch_summary_stats(results)

            # Store in session state
            st.session_state.batch_results = results
            st.session_state.batch_summary_df = summary_df
            st.session_state.batch_stats = stats

            st.success(f"✅ Processed {stats['total_deals']} deals successfully!")

            # Summary stats
            st.markdown("---")
            st.markdown("### 📈 Batch Summary")

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("Total Deals", stats['total_deals'])

            with col2:
                st.metric("🟢 Green", stats['green_deals'])

            with col3:
                st.metric("🟡 Yellow", stats['yellow_deals'])

            with col4:
                st.metric("🔴 Red", stats['red_deals'])

            with col5:
                st.metric("❌ Invalid", stats['invalid_deals'])

            # Routing breakdown
            st.markdown("---")
            st.markdown("### 🎯 Routing Breakdown")

            col_r1, col_r2, col_r3, col_r4 = st.columns(4)

            with col_r1:
                st.metric("Internal DSCR", stats['dscr_routes'])

            with col_r2:
                st.metric("Wholesale", stats['wholesale_routes'])

            with col_r3:
                st.metric("Retail Listing", stats['retail_routes'])

            with col_r4:
                st.metric("Reject", stats['reject_routes'])

            # Averages
            st.markdown("---")
            st.markdown("### 📊 Average Metrics")

            col_a1, col_a2, col_a3 = st.columns(3)

            with col_a1:
                st.metric("Avg ARV", f"${stats['avg_arv']:,.0f}")

            with col_a2:
                st.metric("Avg Purchase % ARV", f"{stats['avg_purchase_pct']*100:.1f}%")

            with col_a3:
                st.metric("Avg DSCR", f"{stats['avg_dscr']:.2f}")

            # Results table
            st.markdown("---")
            st.markdown("### 📋 Detailed Results")

            # Filter options
            col_f1, col_f2 = st.columns(2)

            with col_f1:
                score_filter = st.multiselect(
                    "Filter by Score",
                    options=['GREEN', 'YELLOW', 'RED'],
                    default=['GREEN', 'YELLOW', 'RED']
                )

            with col_f2:
                show_invalid = st.checkbox("Show Invalid Deals", value=False)

            # Apply filters
            filtered_df = summary_df.copy()

            if score_filter:
                filtered_df = filtered_df[filtered_df['Score'].isin(score_filter)]

            if not show_invalid:
                filtered_df = filtered_df[filtered_df['Valid'] == '✅']

            # Display table with color coding
            def highlight_rows(row):
                if row['Score'] == 'GREEN':
                    return ['background-color: rgba(16, 185, 129, 0.1)'] * len(row)
                elif row['Score'] == 'YELLOW':
                    return ['background-color: rgba(245, 158, 11, 0.1)'] * len(row)
                elif row['Score'] == 'RED':
                    return ['background-color: rgba(239, 68, 68, 0.1)'] * len(row)
                else:
                    return [''] * len(row)

            st.dataframe(
                filtered_df.style.apply(highlight_rows, axis=1),
                hide_index=True,
                use_container_width=True,
                height=400
            )

            # Export results
            st.markdown("---")
            st.markdown("### 💾 Export Results")

            col_e1, col_e2, col_e3 = st.columns(3)

            with col_e1:
                # Export all results to CSV
                export_csv = export_batch_results_to_csv(results)
                st.download_button(
                    label="📄 Export Full Results (CSV)",
                    data=export_csv,
                    file_name=f"rei_batch_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col_e2:
                # Export only GREEN deals
                green_results = [r for r in results if r.deal_score == 'GREEN']
                if green_results:
                    green_csv = export_batch_results_to_csv(green_results)
                    st.download_button(
                        label="🟢 Export GREEN Deals Only",
                        data=green_csv,
                        file_name=f"rei_green_deals_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("🟢 Export GREEN Deals Only", disabled=True, use_container_width=True)

            with col_e3:
                # Export only YELLOW deals
                yellow_results = [r for r in results if r.deal_score == 'YELLOW']
                if yellow_results:
                    yellow_csv = export_batch_results_to_csv(yellow_results)
                    st.download_button(
                        label="🟡 Export YELLOW Deals Only",
                        data=yellow_csv,
                        file_name=f"rei_yellow_deals_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("🟡 Export YELLOW Deals Only", disabled=True, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error processing CSV: {str(e)}")
            st.info("Make sure your CSV has the required columns: address, arv, purchase_price, rehab_budget, estimated_rent")

    else:
        st.info("👆 Upload a CSV file to get started")


if __name__ == "__main__":
    main()
