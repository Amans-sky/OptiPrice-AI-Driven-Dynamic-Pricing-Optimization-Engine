"""Streamlit dashboard for AI pricing recommendations."""

import streamlit as st
import sys
import os
import logging
import requests

# Setup path and imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.demand_model import predicted_demand
from config import ENVIRONMENT_CONFIG, API_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Dynamic Pricing Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title('🤖 Dynamic Pricing AI Engine')
st.markdown(
    'Intelligent pricing optimization powered by Deep Q-Learning (DQN) reinforcement learning'
)

# Sidebar with information
with st.sidebar:
    st.header('ℹ️ About')
    st.markdown("""
    **Dynamic Pricing Optimization** uses deep reinforcement learning to recommend
    optimal prices based on:
    - Market demand levels
    - Competitor pricing
    - Inventory constraints
    
    The AI agent learns to maximize revenue while respecting market conditions.
    """)
    
    st.header('⚙️ Configuration')
    st.write(f"""
    - **Price Range**: ${ENVIRONMENT_CONFIG['price_min']} - ${ENVIRONMENT_CONFIG['price_max']}
    - **Base Demand**: {ENVIRONMENT_CONFIG['base_demand']:.0f} units
    - **Price Elasticity**: {ENVIRONMENT_CONFIG['elasticity']}
    """)

# Input section
st.header('📊 Market Conditions')

col1, col2, col3 = st.columns(3)

with col1:
    demand_level = st.slider(
        'Demand Level',
        min_value=0,
        max_value=200,
        value=API_CONFIG['default_demand_level'],
        step=10,
        help="Current market demand (0-200 scale)"
    )

with col2:
    competitor_price = st.slider(
        'Competitor Price',
        min_value=float(ENVIRONMENT_CONFIG['price_min']),
        max_value=float(ENVIRONMENT_CONFIG['price_max']),
        value=API_CONFIG['default_competitor_price'],
        step=1.0,
        help="Competitor's current price"
    )

with col3:
    inventory_level = st.slider(
        'Inventory Level',
        min_value=0,
        max_value=2000,
        value=API_CONFIG['default_inventory_level'],
        step=100,
        help="Current inventory units"
    )

st.divider()

# Display market metrics
st.subheader('📈 Current Market Metrics')

col_metric1, col_metric2, col_metric3 = st.columns(3)

# Calculate metrics at a reference price ($25)
reference_price = 25.0
reference_demand = predicted_demand(reference_price, competitor_price=competitor_price)
reference_revenue = reference_price * reference_demand

with col_metric1:
    st.metric(
        "Demand at $25",
        f"{reference_demand:.0f} units",
        help="Predicted demand if price is set to $25"
    )

with col_metric2:
    st.metric(
        "Revenue at $25",
        f"${reference_revenue:,.2f}",
        help="Expected revenue at $25 price point"
    )

with col_metric3:
    price_ratio = competitor_price / reference_price if reference_price > 0 else 1.0
    st.metric(
        "Price vs Competitor",
        f"{price_ratio:.2f}x",
        help="Competitive positioning (1.0 = same price)"
    )

st.divider()

# AI Recommendation section
st.header('🧠 AI Price Recommendation')

api_url = API_CONFIG['api_url']

if st.button('Get AI-Optimized Price', use_container_width=True, key='recommend_btn'):
    with st.spinner('🔄 Querying AI pricing engine...'):
        try:
            logger.info(
                f"Requesting price recommendation: demand={demand_level}, "
                f"competitor_price={competitor_price}, inventory={inventory_level}"
            )
            
            resp = requests.get(
                f"{api_url}/recommend_price",
                params={
                    'demand_level': float(demand_level),
                    'competitor_price': float(competitor_price),
                    'inventory_level': float(inventory_level)
                },
                timeout=5.0,
            )
            
            if resp.status_code == 200:
                result = resp.json()
                rec_price = result.get('recommended_price')
                source = result.get('source', 'unknown')
                
                logger.info(f"Recommendation received: ${rec_price:.2f} (source: {source})")
                
                # Calculate expected metrics
                expected_demand = predicted_demand(rec_price, competitor_price=competitor_price)
                expected_revenue = rec_price * expected_demand
                
                # Display recommendation with metrics
                col_recom, col_source = st.columns([2, 1])
                
                with col_recom:
                    st.success(f"### 💰 Recommended Price: **${rec_price:.2f}**")
                
                with col_source:
                    if source == 'dqn_model':
                        st.info(f"🤖 Source: DQN Model")
                    else:
                        st.warning(f"📈 Source: Analytic Fallback")
                
                st.divider()
                
                # Expected outcomes
                col_exp1, col_exp2, col_exp3 = st.columns(3)
                
                with col_exp1:
                    st.metric(
                        "Expected Demand",
                        f"{expected_demand:.0f} units",
                        delta=f"{(expected_demand - reference_demand):.0f}" if expected_demand != reference_demand else None,
                        help="Demand at recommended price"
                    )
                
                with col_exp2:
                    st.metric(
                        "Expected Revenue",
                        f"${expected_revenue:,.2f}",
                        delta=f"${(expected_revenue - reference_revenue):+.2f}" if expected_revenue != reference_revenue else None,
                        help="Revenue at recommended price"
                    )
                
                with col_exp3:
                    price_diff = ((rec_price - reference_price) / reference_price) * 100
                    st.metric(
                        "Price Change",
                        f"{price_diff:+.1f}%",
                        help="Difference from $25 reference price"
                    )
                
                # Q-values visualization (if available)
                if 'q_values' in result:
                    st.divider()
                    st.subheader('🎯 AI Decision Details (Q-Values)')
                    q_vals = result['q_values']
                    import pandas as pd
                    q_df = pd.DataFrame({
                        'Price': [f"${p}" for p in sorted(q_vals.keys())],
                        'Q-Value': [q_vals[str(p)] for p in sorted(map(float, q_vals.keys()))]
                    })
                    st.bar_chart(data=q_df.set_index('Price'), use_container_width=True)
            
            else:
                st.error(f"❌ API Error: Status code {resp.status_code}")
                logger.error(f"API error: {resp.status_code}")
        
        except requests.exceptions.ConnectionError:
            st.error(
                "❌ **Cannot connect to pricing API**\n\n"
                "Make sure the API server is running:\n"
                "```bash\nuvicorn api.pricing_api:app --reload\n```"
            )
            logger.error("API connection error")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            logger.error(f"Unexpected error: {e}")

st.divider()

# Footer
col_footer1, col_footer2 = st.columns(2)
with col_footer1:
    st.caption('🚀 Powered by PyTorch Deep Q-Network (DQN)')
with col_footer2:
    st.caption('📊 Real-time dynamic pricing optimization')
