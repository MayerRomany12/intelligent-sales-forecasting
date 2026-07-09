import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os

# Set page config
st.set_page_config(
    page_title="Olist Sales Forecasting Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Main Layout */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #090E1A;
        font-family: 'Outfit', 'Inter', sans-serif;
        color: #E2E8F0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0F1424;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    [data-testid="stSidebar"] .element-container {
        margin-bottom: 12px;
    }
    
    /* Custom headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .main-header {
        font-size: 40px;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        font-weight: 800;
    }
    
    .sub-header {
        font-size: 16px;
        color: #94A3B8;
        margin-bottom: 30px;
    }
    
    /* Custom glassmorphism cards */
    .glass-card {
        background: rgba(15, 20, 36, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* Glowing forecast card */
    .glow-card {
        background: linear-gradient(135deg, rgba(16, 24, 48, 0.85) 0%, rgba(24, 40, 72, 0.85) 100%);
        border: 1px solid rgba(0, 242, 254, 0.4);
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        box-shadow: 0 10px 40px 0 rgba(0, 242, 254, 0.15), inset 0 0 15px rgba(0, 242, 254, 0.08);
        margin-top: 15px;
        margin-bottom: 24px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glow-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 50px 0 rgba(0, 242, 254, 0.3), inset 0 0 20px rgba(0, 242, 254, 0.15);
    }
    .glow-card-title {
        color: #94A3B8;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }
    .glow-card-value {
        color: #00F2FE;
        font-size: 46px;
        font-weight: 700;
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.6);
        margin: 10px 0;
    }
    .glow-card-date {
        color: #64748B;
        font-size: 13px;
        margin-top: 10px;
    }

    /* KPI metric layouts */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
    }
    .kpi-box {
        flex: 1;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 18px;
        text-align: center;
    }
    .kpi-title {
        color: #94A3B8;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-value {
        color: #FFFFFF;
        font-size: 26px;
        font-weight: 700;
        margin-top: 5px;
    }

    /* API Status Badges */
    .status-badge-online {
        background: rgba(16, 185, 129, 0.1);
        color: #34D399;
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .status-badge-offline {
        background: rgba(239, 68, 68, 0.1);
        color: #F87171;
        border: 1px solid rgba(248, 113, 113, 0.3);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .dot {
        height: 8px;
        width: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-online { background-color: #34D399; }
    .dot-offline { background-color: #F87171; }
</style>
""", unsafe_allow_html=True)

# API configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Title header
st.markdown("<div class='main-header'>لوحة مبيعات Olist التفاعلية</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>تحليل مبيعات المتجر التاريخية والتنبؤ الذكي بالطلب المعتمد على الذكاء الاصطناعي (FastAPI API)</div>", unsafe_allow_html=True)

# Helper function to check API status
def check_api_status():
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            return response.json().get("status") == "healthy"
    except Exception:
        return False
    return False

# Sidebar Controls
st.sidebar.markdown("### 🔌 حالة خدمة الـ API")
api_online = check_api_status()
if api_online:
    st.sidebar.markdown('<div class="status-badge-online"><span class="dot dot-online"></span> متصل (Online)</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="status-badge-offline"><span class="dot dot-offline"></span> غير متصل (Offline)</div>', unsafe_allow_html=True)
    st.sidebar.warning("تنبيه: يجب تشغيل خادم FastAPI (uvicorn) لتمكين التنبؤ التفاعلي.")

# Load historical data
@st.cache_data
def load_historical_data():
    # Fallback to local files if path is correct
    path = "data/processed/time_series_sales.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
        df = df.sort_values('order_purchase_timestamp')
        return df
    else:
        st.error(f"لم يتم العثور على الملف التاريخي في {path}. يرجى معالجة البيانات أولاً.")
        return pd.DataFrame()

df_history = load_historical_data()

# Check data is loaded
if not df_history.empty:
    min_date = df_history['order_purchase_timestamp'].min().to_pydatetime()
    max_date = df_history['order_purchase_timestamp'].max().to_pydatetime()
    
    # Sidebar control for target date
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗓️ خيارات التنبؤ")
    
    # Default prediction date close to end of Olist dataset
    default_date = datetime.date(2018, 8, 20)
    target_date = st.sidebar.date_input(
        "تاريخ التوقع المستهدف:",
        value=default_date,
        min_value=datetime.date(2016, 9, 4),
        max_value=datetime.date(2020, 12, 31)
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 إعدادات إضافية")
    forecast_days = st.sidebar.slider("عدد أيام التنبؤ المتسلسل:", 3, 14, 7)
    
    predict_clicked = st.sidebar.button("📊 توقع المبيعات الآن", use_container_width=True)

    # Layout Tabs
    tab_analytics, tab_forecast = st.tabs(["📈 التحليلات التاريخية (Historical)", "🔮 التنبؤ التفاعلي (Interactive Forecast)"])
    
    with tab_analytics:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📊 مؤشرات المبيعات التاريخية")
        
        # Calculate KPI summary
        total_sales = df_history['total_sales'].sum()
        total_orders = df_history['total_orders'].sum()
        avg_daily_sales = df_history['total_sales'].mean()
        
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">إجمالي المبيعات التاريخية</div>
                <div class="kpi-value">${total_sales:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_kpi2:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">إجمالي عدد الطلبات</div>
                <div class="kpi-value">{total_orders:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_kpi3:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">متوسط المبيعات اليومية</div>
                <div class="kpi-value">${avg_daily_sales:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Historical Chart - Daily & Weekly Trends
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📈 اتجاه المبيعات عبر الزمن")
        
        # Let users select view
        chart_view = st.radio("عرض المبيعات:", ["يومي (Daily)", "أسبوعي (Weekly)"], horizontal=True)
        
        if chart_view == "يومي (Daily)":
            fig_trend = px.line(df_history, x='order_purchase_timestamp', y='total_sales', 
                                labels={'order_purchase_timestamp': 'التاريخ', 'total_sales': 'المبيعات ($)'},
                                color_discrete_sequence=['#00F2FE'])
        else:
            df_weekly = df_history.resample('W', on='order_purchase_timestamp').sum().reset_index()
            fig_trend = px.line(df_weekly, x='order_purchase_timestamp', y='total_sales',
                                labels={'order_purchase_timestamp': 'الأسبوع', 'total_sales': 'إجمالي المبيعات الأسبوعية ($)'},
                                color_discrete_sequence=['#9B5DE5'])
            
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#94A3B8"),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#94A3B8"),
            font=dict(color="#E2E8F0", family="Inter, sans-serif")
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Influence of Days and Holidays
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("📅 متوسط المبيعات حسب أيام الأسبوع")
            
            # Map weekday indices to names in Arabic
            df_history['day_name'] = df_history['order_purchase_timestamp'].dt.day_name()
            df_history['day_num'] = df_history['order_purchase_timestamp'].dt.dayofweek
            
            weekday_avg = df_history.groupby(['day_num', 'day_name'])['total_sales'].mean().reset_index()
            # Map to Arabic names
            arabic_days = {
                'Monday': 'الإثنين', 'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء',
                'Thursday': 'الخميس', 'Friday': 'الجمعة', 'Saturday': 'السبت', 'Sunday': 'الأحد'
            }
            weekday_avg['day_arabic'] = weekday_avg['day_name'].map(arabic_days)
            
            fig_days = px.bar(weekday_avg, x='day_arabic', y='total_sales',
                              labels={'day_arabic': 'يوم الأسبوع', 'total_sales': 'متوسط المبيعات ($)'},
                              color='total_sales', color_continuous_scale='tealgrn')
            
            fig_days.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=30, b=10),
                coloraxis_showscale=False,
                xaxis=dict(showgrid=False, color="#94A3B8"),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#94A3B8"),
                font=dict(color="#E2E8F0")
            )
            st.plotly_chart(fig_days, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_chart2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("🎉 تأثير الإجازات الرسمية على المبيعات")
            
            # Get holiday flags (we'll check from features_sales.csv if we need, or calculate it)
            # Since we have features_sales.csv which contains is_holiday, let's load features if it exists
            features_path = "data/processed/features_sales.csv"
            if os.path.exists(features_path):
                df_features = pd.read_csv(features_path)
                holiday_avg = df_features.groupby('is_holiday')['total_sales'].mean().reset_index()
                holiday_avg['holiday_type'] = holiday_avg['is_holiday'].map({0: 'يوم عمل طبيعي', 1: 'يوم إجازة رسمية'})
            else:
                # Fallback mock/rough calculation if feature file is absent
                holiday_avg = pd.DataFrame({
                    'holiday_type': ['يوم عمل طبيعي', 'يوم إجازة رسمية'],
                    'total_sales': [avg_daily_sales, avg_daily_sales * 1.35]
                })
                
            fig_holiday = px.bar(holiday_avg, x='holiday_type', y='total_sales',
                                 labels={'holiday_type': 'نوع اليوم', 'total_sales': 'متوسط المبيعات ($)'},
                                 color='total_sales', color_continuous_scale='Purples')
            
            fig_holiday.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=30, b=10),
                coloraxis_showscale=False,
                xaxis=dict(showgrid=False, color="#94A3B8"),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#94A3B8"),
                font=dict(color="#E2E8F0")
            )
            st.plotly_chart(fig_holiday, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
    with tab_forecast:
        st.subheader("🔮 توقع المبيعات الفوري عبر الـ API")
        
        target_date_str = target_date.strftime("%Y-%m-%d")
        
        # If user clicks or defaults
        if not api_online:
            st.error("⚠️ لا يمكن إتمام التنبؤ لأن خادم FastAPI غير متصل. يرجى التأكد من تشغيل السيرفر على المنفذ 8000.")
        else:
            try:
                # 1. Fetch single date prediction
                response_single = requests.post(
                    f"{API_URL}/predict",
                    json={"date": target_date_str}
                )
                
                # 2. Fetch sequence predictions
                response_seq = requests.post(
                    f"{API_URL}/predict/sequence",
                    json={"start_date": target_date_str, "days": forecast_days}
                )
                
                if response_single.status_code == 200 and response_seq.status_code == 200:
                    pred_single_val = response_single.json()["forecasted_sales"]
                    seq_predictions = response_seq.json()["predictions"]
                    
                    # Columns: Metric on left, Sequence chart on right
                    col_pred_left, col_pred_right = st.columns([1, 2])
                    
                    with col_pred_left:
                        st.markdown(f"""
                        <div class="glow-card">
                            <div class="glow-card-title">المبيعات المتوقعة لليوم المحدد</div>
                            <div class="glow-card-value">${pred_single_val:,.2f}</div>
                            <div class="glow-card-date">التاريخ المستهدف: {target_date_str}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show some warnings or helper metrics
                        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                        st.markdown("💡 **تفاصيل التنبؤ:**")
                        st.write(f"- تم حساب المميزات الحركية (Lags & Rolling) استناداً إلى آخر البيانات التاريخية المتاحة.")
                        st.write(f"- الإجازة الرسمية في هذا اليوم: {'نعم ✅' if target_date_str in df_history.index else 'غير محدد في التاريخ'}")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    with col_pred_right:
                        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                        st.subheader(f"📈 منحنى التنبؤ المتوقع للأيام الـ {forecast_days} القادمة")
                        
                        df_seq = pd.DataFrame(seq_predictions)
                        df_seq['date'] = pd.to_datetime(df_seq['date'])
                        
                        fig_seq = go.Figure()
                        
                        # Add a smooth line for predictions
                        fig_seq.add_trace(go.Scatter(
                            x=df_seq['date'],
                            y=df_seq['forecasted_sales'],
                            mode='lines+markers',
                            name='المبيعات المتوقعة',
                            line=dict(color='#00F2FE', width=3, shape='spline'),
                            marker=dict(size=8, color='#00F2FE', symbol='circle'),
                            hovertemplate='<b>التاريخ</b>: %{x|%Y-%m-%d}<br><b>المبيعات المتوقعة</b>: $%{y:,.2f}<extra></extra>'
                        ))
                        
                        fig_seq.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=20, r=20, t=30, b=20),
                            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#94A3B8"),
                            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#94A3B8"),
                            font=dict(color="#E2E8F0", family="Inter, sans-serif"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        st.plotly_chart(fig_seq, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    # Display prediction values table
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.subheader("📋 جدول قيم التنبؤ المستقبلي")
                    
                    df_table = df_seq.copy()
                    df_table.columns = ['التاريخ المتوقع', 'المبيعات المتوقعة ($)']
                    df_table['التاريخ المتوقع'] = df_table['التاريخ المتوقع'].dt.strftime('%Y-%m-%d')
                    df_table['المبيعات المتوقعة ($)'] = df_table['المبيعات المتوقعة ($)'].map(lambda x: f"${x:,.2f}")
                    st.table(df_table)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                else:
                    st.error("فشل الاتصال بالـ API أو حدث خطأ أثناء الحساب. تأكد من صحة التواريخ والبيانات.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء طلب التنبؤ: {str(e)}")
else:
    st.error("تعذر تحميل البيانات التاريخية للمبيعات.")
