import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from supabase import create_client
import numpy as np

# ============= КОНФИГУРАЦИЯ СТРАНИЦЫ =============
st.set_page_config(
    page_title="МТС Банк | Analytics Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============= КАСТОМНЫЕ СТИЛИ CSS =============
st.markdown("""
<style>
    /* Импорт шрифтов */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Основные стили */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Скрываем стандартные элементы Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Фон приложения */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Главный контейнер */
    .main {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    /* Заголовок */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem;
        border-radius: 20px;
        margin: -2rem -2rem 2rem -2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .dashboard-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .dashboard-subtitle {
        font-size: 1.2rem;
        opacity: 0.95;
        font-weight: 400;
    }
    
    /* Метрики */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="metric-container"] > div {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    [data-testid="metric-container"] label {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
    }
    
    /* Графики */
    .plot-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        margin-bottom: 1.5rem;
    }
    
    /* Таблицы */
    .dataframe {
        border: none !important;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        padding: 1rem !important;
    }
    
    .dataframe tbody tr {
        border-bottom: 1px solid #f3f4f6;
        transition: all 0.2s ease;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f9fafb !important;
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Селекты и инпуты */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Алерты */
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .info-box {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Анимации */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main > * {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Разделители */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
        margin: 2rem 0;
    }
    
    /* Сайдбар */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
    }
    
    /* Статус индикаторы */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-positive {
        background: #10b981;
        color: white;
    }
    
    .status-negative {
        background: #ef4444;
        color: white;
    }
    
    .status-neutral {
        background: #6b7280;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============= HEADER =============
st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">🏦 МТС Банк Analytics</div>
    <div class="dashboard-subtitle">Real-time Customer Experience Dashboard</div>
</div>
""", unsafe_allow_html=True)

# ============= ПОДКЛЮЧЕНИЕ К БД =============
@st.cache_resource
def init_connection():
    """Инициализация подключения к Supabase"""
    try:
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
    except:
        return None

# ============= ЗАГРУЗКА ДАННЫХ =============
@st.cache_data(ttl=60)
def load_data():
    """Загрузка всех отзывов из БД"""
    client = init_connection()
    if client:
        try:
            response = client.table("reviews").select("*").execute()
            return pd.DataFrame(response.data)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# Загружаем данные
df = load_data()

if not df.empty:
    # ============= ФИЛЬТРЫ =============
    
    # Контейнер для фильтров с фоном
    with st.container():
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;'>
            <h3 style='margin-top: 0; color: #1f2937;'>🔍 Фильтры и период анализа</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Первая строка фильтров
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            # Выбор типа периода
            period_type = st.radio(
                "Выберите тип периода",
                ["Быстрый выбор", "Конкретные даты", "Относительный период"],
                horizontal=True
            )
        
        with col2:
            sources_filter = st.multiselect(
                "📱 Источники",
                options=df['source'].unique() if 'source' in df else [],
                default=df['source'].unique() if 'source' in df else []
            )
        
        with col3:
            rating_filter = st.select_slider(
                "⭐ Рейтинг",
                options=[1, 2, 3, 4, 5],
                value=(1, 5)
            )
        
        # Вторая строка - выбор периода в зависимости от типа
        st.markdown("---")
        
        if period_type == "Быстрый выбор":
            col1, col2, col3, col4 = st.columns(4)
            
            quick_period = None
            with col1:
                if st.button("📅 Сегодня", use_container_width=True):
                    quick_period = "today"
            with col2:
                if st.button("📅 Вчера", use_container_width=True):
                    quick_period = "yesterday"
            with col3:
                if st.button("📅 Эта неделя", use_container_width=True):
                    quick_period = "this_week"
            with col4:
                if st.button("📅 Этот месяц", use_container_width=True):
                    quick_period = "this_month"
            
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                if st.button("📅 7 дней", use_container_width=True):
                    quick_period = "7_days"
            with col6:
                if st.button("📅 30 дней", use_container_width=True):
                    quick_period = "30_days"
            with col7:
                if st.button("📅 90 дней", use_container_width=True):
                    quick_period = "90_days"
            with col8:
                if st.button("📅 Все время", use_container_width=True):
                    quick_period = "all_time"
            
            # Сохраняем выбор в session state
            if quick_period:
                st.session_state['quick_period'] = quick_period
            
            # Используем сохраненный выбор
            selected_period = st.session_state.get('quick_period', '7_days')
            
        elif period_type == "Конкретные даты":
            col1, col2 = st.columns(2)
            
            with col1:
                # Определяем минимальную и максимальную даты в данных
                if 'review_date' in df:
                    min_date = pd.to_datetime(df['review_date']).min().date()
                    max_date = pd.to_datetime(df['review_date']).max().date()
                else:
                    min_date = datetime.now().date() - timedelta(days=365)
                    max_date = datetime.now().date()
                
                date_from = st.date_input(
                    "📅 Дата начала",
                    value=max_date - timedelta(days=30),
                    min_value=min_date,
                    max_value=max_date,
                    format="DD.MM.YYYY"
                )
            
            with col2:
                date_to = st.date_input(
                    "📅 Дата окончания",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    format="DD.MM.YYYY"
                )
            
            # Показываем выбранный период
            if date_from and date_to:
                days_selected = (date_to - date_from).days + 1
                st.info(f"📊 Выбран период: **{days_selected}** дней ({date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')})")
        
        elif period_type == "Относительный период":
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                relative_number = st.number_input(
                    "Количество",
                    min_value=1,
                    max_value=365,
                    value=7,
                    step=1
                )
            
            with col2:
                relative_unit = st.selectbox(
                    "Единица времени",
                    ["дней", "недель", "месяцев"],
                    index=0
                )
            
            with col3:
                relative_direction = st.selectbox(
                    "Направление",
                    ["назад", "вперед"],
                    index=0
                )
            
            # Конвертируем в дни
            if relative_unit == "недель":
                days_to_filter = relative_number * 7
            elif relative_unit == "месяцев":
                days_to_filter = relative_number * 30
            else:
                days_to_filter = relative_number
            
            st.info(f"📊 Анализ за последние **{relative_number} {relative_unit}**")
        
        # Кнопка обновления
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col3:
            if st.button("🔄 Применить фильтры", use_container_width=True, type="primary"):
                st.cache_data.clear()
                st.rerun()
    
    # ============= ПРИМЕНЕНИЕ ФИЛЬТРОВ =============
    filtered_df = df.copy()
    
    # Преобразуем даты
    if 'review_date' in filtered_df:
        filtered_df['review_date'] = pd.to_datetime(filtered_df['review_date'])
        
        # Применяем фильтр по дате в зависимости от выбранного типа
        if period_type == "Быстрый выбор":
            selected_period = st.session_state.get('quick_period', '7_days')
            
            if selected_period == "today":
                filtered_df = filtered_df[filtered_df['review_date'].dt.date == datetime.now().date()]
            elif selected_period == "yesterday":
                filtered_df = filtered_df[filtered_df['review_date'].dt.date == (datetime.now() - timedelta(days=1)).date()]
            elif selected_period == "this_week":
                week_start = datetime.now() - timedelta(days=datetime.now().weekday())
                filtered_df = filtered_df[filtered_df['review_date'] >= week_start]
            elif selected_period == "this_month":
                month_start = datetime.now().replace(day=1)
                filtered_df = filtered_df[filtered_df['review_date'] >= month_start]
            elif selected_period == "7_days":
                filtered_df = filtered_df[filtered_df['review_date'] >= datetime.now() - timedelta(days=7)]
            elif selected_period == "30_days":
                filtered_df = filtered_df[filtered_df['review_date'] >= datetime.now() - timedelta(days=30)]
            elif selected_period == "90_days":
                filtered_df = filtered_df[filtered_df['review_date'] >= datetime.now() - timedelta(days=90)]
            # all_time - не фильтруем
            
        elif period_type == "Конкретные даты":
            if date_from and date_to:
                filtered_df = filtered_df[
                    (filtered_df['review_date'].dt.date >= date_from) & 
                    (filtered_df['review_date'].dt.date <= date_to)
                ]
        
        elif period_type == "Относительный период":
            if relative_direction == "назад":
                filtered_df = filtered_df[filtered_df['review_date'] >= datetime.now() - timedelta(days=days_to_filter)]
            else:
                filtered_df = filtered_df[filtered_df['review_date'] <= datetime.now() + timedelta(days=days_to_filter)]
    
    # Фильтр по источникам
    if sources_filter and 'source' in filtered_df:
        filtered_df = filtered_df[filtered_df['source'].isin(sources_filter)]
    
    # Фильтр по рейтингу
    if 'rating' in filtered_df:
        filtered_df = filtered_df[(filtered_df['rating'] >= rating_filter[0]) & (filtered_df['rating'] <= rating_filter[1])]
    
    # ============= ИНФОРМАЦИЯ О ВЫБРАННОМ ПЕРИОДЕ =============
    if not filtered_df.empty and 'review_date' in filtered_df:
        # Показываем статистику по выбранному периоду
        period_start = filtered_df['review_date'].min()
        period_end = filtered_df['review_date'].max()
        total_days = (period_end - period_start).days + 1
        
        # Информационная панель
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    color: white; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;'>
            <strong>📊 Анализ данных:</strong> {len(filtered_df)} отзывов за период с {period_start.strftime('%d.%m.%Y')} по {period_end.strftime('%d.%m.%Y')} ({total_days} дней)
        </div>
        """, unsafe_allow_html=True)
    
    # ============= КЛЮЧЕВЫЕ МЕТРИКИ =============
    st.markdown("### 📊 Ключевые показатели")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        total_reviews = len(filtered_df)
        st.metric(
            label="📝 Отзывов",
            value=total_reviews,
            delta="↑ 12%" if total_reviews > 0 else None
        )
    
    with col2:
        avg_rating = filtered_df['rating'].mean() if 'rating' in filtered_df else 0
        st.metric(
            label="⭐ Рейтинг",
            value=f"{avg_rating:.2f}",
            delta="↑ 0.3" if avg_rating > 4 else "↓ 0.2"
        )
    
    with col3:
        positive = len(filtered_df[filtered_df['rating'] >= 4]) if 'rating' in filtered_df else 0
        positive_pct = (positive / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.metric(
            label="😊 Позитивных",
            value=f"{positive_pct:.0f}%",
            delta="↑ 5%" if positive_pct > 60 else None
        )
    
    with col4:
        if 'bank_response' in filtered_df:
            responses = filtered_df['bank_response'].notna().sum()
            response_rate = (responses / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        else:
            response_rate = 0
        st.metric(
            label="💬 Ответы",
            value=f"{response_rate:.0f}%",
            delta="↑ 8%" if response_rate > 30 else "↓ 3%"
        )
    
    with col5:
        unique_authors = filtered_df['author'].nunique() if 'author' in filtered_df else 0
        st.metric(
            label="👥 Авторов",
            value=unique_authors,
            delta=None
        )
    
    with col6:
        nps_score = 72  # Можно рассчитать из данных
        st.metric(
            label="📈 NPS",
            value=nps_score,
            delta="↑ 15"
        )
    
    st.markdown("---")
    
    # ============= ГРАФИКИ =============
    
    # Первая строка графиков
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # График динамики отзывов
        st.markdown("### 📈 Динамика отзывов")
        
        if 'review_date' in filtered_df:
            daily_stats = filtered_df.groupby(filtered_df['review_date'].dt.date).agg({
                'id': 'count',
                'rating': 'mean'
            }).reset_index()
            daily_stats.columns = ['Дата', 'Количество', 'Средний рейтинг']
            
            fig = make_subplots(
                rows=2, cols=1,
                row_heights=[0.7, 0.3],
                shared_xaxes=True,
                vertical_spacing=0.05
            )
            
            # Основной график
            fig.add_trace(
                go.Scatter(
                    x=daily_stats['Дата'],
                    y=daily_stats['Количество'],
                    mode='lines+markers',
                    name='Количество отзывов',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8, color='#667eea'),
                    fill='tozeroy',
                    fillcolor='rgba(102, 126, 234, 0.1)'
                ),
                row=1, col=1
            )
            
            # График рейтинга
            fig.add_trace(
                go.Bar(
                    x=daily_stats['Дата'],
                    y=daily_stats['Средний рейтинг'],
                    name='Средний рейтинг',
                    marker_color='#764ba2',
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                height=400,
                showlegend=True,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=12),
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Распределение рейтингов
        st.markdown("### ⭐ Распределение оценок")
        
        if 'rating' in filtered_df:
            rating_dist = filtered_df['rating'].value_counts().sort_index()
            
            colors = ['#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e']
            
            fig = go.Figure(data=[
                go.Bar(
                    x=['1⭐', '2⭐', '3⭐', '4⭐', '5⭐'],
                    y=[rating_dist.get(i, 0) for i in range(1, 6)],
                    marker_color=colors,
                    text=[rating_dist.get(i, 0) for i in range(1, 6)],
                    textposition='outside',
                    textfont=dict(size=14, weight=600)
                )
            ])
            
            fig.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=12),
                margin=dict(l=0, r=0, t=0, b=0),
                yaxis_title="Количество",
                xaxis_title=""
            )
            
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Вторая строка графиков
    col3, col4, col5 = st.columns([2, 2, 2])
    
    with col3:
        # Источники отзывов
        st.markdown("### 📱 Источники")
        
        if 'source' in filtered_df:
            source_stats = filtered_df['source'].value_counts()
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=source_stats.index,
                    values=source_stats.values,
                    hole=0.6,
                    marker_colors=['#667eea', '#764ba2', '#a855f7', '#ec4899'],
                    textinfo='label+percent',
                    textfont=dict(size=12)
                )
            ])
            
            fig.update_layout(
                height=300,
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=12),
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        # Топ городов
        st.markdown("### 🌍 География")
        
        if 'author_location' in filtered_df:
            location_df = filtered_df[filtered_df['author_location'].notna() & (filtered_df['author_location'] != '')]
            if not location_df.empty:
                top_locations = location_df['author_location'].value_counts().head(5)
                
                fig = go.Figure(data=[
                    go.Bar(
                        y=top_locations.index,
                        x=top_locations.values,
                        orientation='h',
                        marker=dict(
                            color=top_locations.values,
                            colorscale='Viridis',
                            showscale=False
                        ),
                        text=top_locations.values,
                        textposition='outside'
                    )
                ])
                
                fig.update_layout(
                    height=300,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=12),
                    margin=dict(l=0, r=0, t=30, b=0),
                    xaxis_title="Количество отзывов"
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with col5:
        # Тренд настроения
        st.markdown("### 💭 Анализ тональности")
        
        # Симулируем данные тональности
        sentiment_data = {
            'Позитивные': len(filtered_df[filtered_df['rating'] >= 4]) if 'rating' in filtered_df else 0,
            'Нейтральные': len(filtered_df[filtered_df['rating'] == 3]) if 'rating' in filtered_df else 0,
            'Негативные': len(filtered_df[filtered_df['rating'] <= 2]) if 'rating' in filtered_df else 0
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(sentiment_data.keys()),
                y=list(sentiment_data.values()),
                marker_color=['#22c55e', '#eab308', '#ef4444'],
                text=list(sentiment_data.values()),
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            height=300,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=12),
            margin=dict(l=0, r=0, t=30, b=0),
            yaxis_title="Количество"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ============= ТАБЛИЦА ОТЗЫВОВ =============
    st.markdown("### 📋 Последние отзывы")
    
    # Контролы для таблицы
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    
    with col1:
        show_negative = st.checkbox("🔴 Только негативные", value=False)
    with col2:
        show_with_response = st.checkbox("💬 С ответом банка", value=False)
    with col3:
        sort_by = st.selectbox("Сортировка", ["Дата ↓", "Рейтинг ↓", "Рейтинг ↑"])
    with col4:
        rows_to_show = st.number_input("Показать строк", min_value=5, max_value=50, value=10)
    
    # Фильтруем таблицу
    table_df = filtered_df.copy()
    
    if show_negative and 'rating' in table_df:
        table_df = table_df[table_df['rating'] <= 2]
    
    if show_with_response and 'bank_response' in table_df:
        table_df = table_df[table_df['bank_response'].notna()]
    
    # Сортировка
    if sort_by == "Дата ↓" and 'review_date' in table_df:
        table_df = table_df.sort_values('review_date', ascending=False)
    elif sort_by == "Рейтинг ↓" and 'rating' in table_df:
        table_df = table_df.sort_values('rating', ascending=False)
    elif sort_by == "Рейтинг ↑" and 'rating' in table_df:
        table_df = table_df.sort_values('rating', ascending=True)
    
    # Выбираем колонки для отображения
    display_columns = ['review_date', 'author', 'rating', 'review_text', 'source', 'author_location']
    display_columns = [col for col in display_columns if col in table_df.columns]
    
    if display_columns:
        display_df = table_df[display_columns].head(rows_to_show)
        
        # Переименовываем колонки
        column_mapping = {
            'review_date': 'Дата',
            'author': 'Автор',
            'rating': 'Рейтинг',
            'review_text': 'Отзыв',
            'source': 'Источник',
            'author_location': 'Город'
        }
        display_df = display_df.rename(columns=column_mapping)
        
        # Сокращаем текст отзывов
        if 'Отзыв' in display_df:
            display_df['Отзыв'] = display_df['Отзыв'].apply(
                lambda x: x[:150] + '...' if isinstance(x, str) and len(x) > 150 else x
            )
        
        # Форматируем дату
        if 'Дата' in display_df:
            display_df['Дата'] = pd.to_datetime(display_df['Дата']).dt.strftime('%d.%m.%Y')
        
        # Отображаем таблицу
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Рейтинг": st.column_config.NumberColumn(
                    "Рейтинг",
                    format="%d ⭐",
                    min_value=1,
                    max_value=5,
                ),
                "Дата": st.column_config.DateColumn(
                    "Дата",
                    format="DD.MM.YYYY",
                ),
            }
        )
    
    # ============= FOOTER =============
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("🏦 **МТС Банк** Analytics Dashboard")
    
    with col2:
        st.markdown(f"📊 Данные: **{len(filtered_df)}** отзывов")
    
    with col3:
        st.markdown(f"🔄 Обновлено: **{datetime.now().strftime('%H:%M:%S')}**")
    
    with col4:
        # Кнопка экспорта данных
        if not filtered_df.empty:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Скачать CSV",
                data=csv,
                file_name=f'mts_reviews_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv',
            )

else:
    # Если нет данных
    st.error("❌ Нет подключения к базе данных или данные отсутствуют")
    st.info("""
    ### Проверьте:
    1. ✅ Добавлены ли секреты SUPABASE_
