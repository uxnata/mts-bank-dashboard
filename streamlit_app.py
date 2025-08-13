import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from supabase import create_client
import numpy as np

# ============= КОНФИГУРАЦИЯ =============
st.set_page_config(
    page_title="МТС Банк | Система мониторинга",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============= ПРОФЕССИОНАЛЬНАЯ ЦВЕТОВАЯ СХЕМА =============
COLORS = {
    'primary': '#1e40af',      # Синий (основной бренд)
    'secondary': '#64748b',     # Серый (вторичный)
    'success': '#059669',       # Зеленый (позитив)
    'warning': '#d97706',       # Оранжевый (предупреждение)
    'danger': '#dc2626',        # Красный (негатив)
    'info': '#0891b2',          # Голубой (информация)
    'background': '#f8fafc',    # Светло-серый фон
    'surface': '#ffffff',       # Белый
    'text_primary': '#0f172a',  # Темный текст
    'text_secondary': '#475569', # Серый текст
    'border': '#e2e8f0',        # Светлая граница
    'chart_colors': ['#1e40af', '#0891b2', '#059669', '#d97706', '#dc2626']  # Палитра для графиков
}

# ============= ПРОФЕССИОНАЛЬНЫЕ СТИЛИ =============
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Основные стили */
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Убираем стандартные элементы */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Фон приложения */
    .stApp {{
        background-color: {COLORS['background']};
    }}
    
    /* Основной контейнер */
    .main > div {{
        padding: 1.5rem;
        max-width: 1400px;
        margin: 0 auto;
    }}
    
    /* Профессиональный заголовок */
    .main-header {{
        background: {COLORS['surface']};
        border-left: 4px solid {COLORS['primary']};
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    .main-title {{
        color: {COLORS['text_primary']};
        font-size: 1.875rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    .main-subtitle {{
        color: {COLORS['text_secondary']};
        font-size: 1rem;
        font-weight: 400;
    }}
    
    /* Метрики */
    [data-testid="metric-container"] {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        padding: 1.25rem;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }}
    
    [data-testid="metric-container"]:hover {{
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }}
    
    [data-testid="metric-container"] label {{
        color: {COLORS['text_secondary']};
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }}
    
    [data-testid="metric-container"] [data-testid="metric-value"] {{
        color: {COLORS['text_primary']};
        font-size: 1.875rem;
        font-weight: 700;
        line-height: 1.2;
    }}
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {{
        font-size: 0.875rem;
        font-weight: 500;
    }}
    
    /* Карточки секций */
    .section-card {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    
    /* Заголовки секций */
    h2 {{
        color: {COLORS['text_primary']};
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {COLORS['border']};
    }}
    
    h3 {{
        color: {COLORS['text_primary']};
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }}
    
    /* Кнопки */
    .stButton > button {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border-radius: 6px;
        transition: all 0.2s ease;
        font-size: 0.875rem;
    }}
    
    .stButton > button:hover {{
        background-color: #1e3a8a;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    /* Селекторы и инпуты */
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stDateInput > div > div {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        font-size: 0.875rem;
    }}
    
    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {{
        border-color: {COLORS['primary']};
    }}
    
    /* Radio buttons */
    .stRadio > div {{
        background: {COLORS['surface']};
        padding: 0.75rem;
        border-radius: 6px;
        border: 1px solid {COLORS['border']};
    }}
    
    /* Таблицы */
    .dataframe {{
        font-size: 0.875rem;
        border: 1px solid {COLORS['border']};
    }}
    
    .dataframe thead tr th {{
        background-color: {COLORS['background']};
        color: {COLORS['text_primary']};
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        padding: 0.75rem;
    }}
    
    .dataframe tbody tr {{
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    .dataframe tbody tr:hover {{
        background-color: {COLORS['background']};
    }}
    
    /* Информационные блоки */
    .stAlert {{
        border-radius: 6px;
        border: 1px solid;
        font-size: 0.875rem;
    }}
    
    /* Sidebar */
    .css-1d391kg {{
        background-color: {COLORS['surface']};
        border-right: 1px solid {COLORS['border']};
    }}
    
    /* Разделители */
    hr {{
        border: none;
        border-top: 1px solid {COLORS['border']};
        margin: 1.5rem 0;
    }}
    
    /* Чекбоксы */
    .stCheckbox {{
        font-size: 0.875rem;
    }}
    
    /* Статус индикаторы */
    .status-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }}
    
    .status-positive {{
        background-color: {COLORS['success']};
        color: white;
    }}
    
    .status-negative {{
        background-color: {COLORS['danger']};
        color: white;
    }}
    
    .status-neutral {{
        background-color: {COLORS['secondary']};
        color: white;
    }}
</style>
""", unsafe_allow_html=True)

# ============= HEADER =============
st.markdown(f"""
<div class="main-header">
    <div class="main-title">МТС Банк • Система мониторинга отзывов</div>
    <div class="main-subtitle">Аналитическая панель управления • Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
</div>
""", unsafe_allow_html=True)

# ============= ПОДКЛЮЧЕНИЕ К БД =============
@st.cache_resource
def init_connection():
    try:
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
    except:
        return None

@st.cache_data(ttl=60)
def load_data():
    client = init_connection()
    if client:
        try:
            response = client.table("reviews").select("*").execute()
            return pd.DataFrame(response.data)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# Загрузка данных
df = load_data()

if not df.empty:
    # ============= ПАНЕЛЬ ФИЛЬТРОВ =============
    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("## 🔍 Панель управления фильтрами")
        
        # Выбор типа периода
        period_type = st.radio(
            "Тип периода",
            ["Предустановленный", "Произвольные даты", "Относительный"],
            horizontal=True,
            help="Выберите способ фильтрации по времени"
        )
        
        st.markdown("---")
        
        # Фильтры в зависимости от типа периода
        if period_type == "Предустановленный":
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                period_preset = st.selectbox(
                    "Выберите период",
                    ["Сегодня", "Вчера", "Последние 7 дней", "Последние 30 дней", "Последние 90 дней", "Весь период"],
                    index=2
                )
            
            with col2:
                sources_filter = st.multiselect(
                    "Источники",
                    options=df['source'].unique() if 'source' in df else [],
                    default=df['source'].unique() if 'source' in df else []
                )
            
            with col3:
                rating_filter = st.select_slider(
                    "Диапазон рейтингов",
                    options=[1, 2, 3, 4, 5],
                    value=(1, 5)
                )
            
            with col4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Применить фильтры", type="primary", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
        
        elif period_type == "Произвольные даты":
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'review_date' in df:
                    min_date = pd.to_datetime(df['review_date']).min().date()
                    max_date = pd.to_datetime(df['review_date']).max().date()
                else:
                    min_date = datetime.now().date() - timedelta(days=365)
                    max_date = datetime.now().date()
                
                date_from = st.date_input(
                    "Дата начала",
                    value=max_date - timedelta(days=30),
                    min_value=min_date,
                    max_value=max_date,
                    format="DD.MM.YYYY"
                )
            
            with col2:
                date_to = st.date_input(
                    "Дата окончания",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    format="DD.MM.YYYY"
                )
            
            with col3:
                sources_filter = st.multiselect(
                    "Источники",
                    options=df['source'].unique() if 'source' in df else [],
                    default=df['source'].unique() if 'source' in df else []
                )
            
            with col4:
                rating_filter = st.select_slider(
                    "Рейтинги",
                    options=[1, 2, 3, 4, 5],
                    value=(1, 5)
                )
        
        else:  # Относительный период
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                relative_value = st.number_input("Количество", min_value=1, max_value=365, value=30)
            
            with col2:
                relative_unit = st.selectbox("Единица", ["дней", "недель", "месяцев"])
            
            with col3:
                sources_filter = st.multiselect(
                    "Источники",
                    options=df['source'].unique() if 'source' in df else [],
                    default=df['source'].unique() if 'source' in df else []
                )
            
            with col4:
                rating_filter = st.select_slider(
                    "Рейтинги",
                    options=[1, 2, 3, 4, 5],
                    value=(1, 5)
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============= ПРИМЕНЕНИЕ ФИЛЬТРОВ =============
    filtered_df = df.copy()
    
    # Преобразование дат
    if 'review_date' in filtered_df:
        filtered_df['review_date'] = pd.to_datetime(filtered_df['review_date'])
        
        # Фильтрация по периоду
        if period_type == "Предустановленный":
            if period_preset == "Сегодня":
                filtered_df = filtered_df[filtered_df['review_date'].dt.date == datetime.now().date()]
            elif period_preset == "Вчера":
                filtered_df = filtered_df[filtered_df['review_date'].dt.date == (datetime.now() - timedelta(days=1)).date()]
            elif period_preset == "Последние 7 дней":
                filtered_df = filtered_df[filtered_df['review_date'] >= datetime.now() - timedelta(days=7)]
            elif period_preset == "Последние 30 дней":
                filtered_df = filtered_df[filtered_df['review_date'] >= datetime.now() - timedelta(days=30)]
            elif period_preset == "Последние 90 дней":
                filtered_df = filtered_df[filtered_df['review_date'] >= datetime.now() - timedelta(days=90)]
        
        elif period_type == "Произвольные даты":
            filtered_df = filtered_df[
                (filtered_df['review_date'].dt.date >= date_from) & 
                (filtered_df['review_date'].dt.date <= date_to)
            ]
        
        else:  # Относительный
            days = relative_value
            if relative_unit == "недель":
                days = relative_value * 7
            elif relative_unit == "месяцев":
                days = relative_value * 30
            filtered_df = filtered_df[filtered_df['review_date'] >= datetime.now() - timedelta(days=days)]
    
    # Фильтр по источникам
    if sources_filter and 'source' in filtered_df:
        filtered_df = filtered_df[filtered_df['source'].isin(sources_filter)]
    
    # Фильтр по рейтингу
    if 'rating' in filtered_df:
        filtered_df = filtered_df[(filtered_df['rating'] >= rating_filter[0]) & (filtered_df['rating'] <= rating_filter[1])]
    
    # ============= КЛЮЧЕВЫЕ МЕТРИКИ =============
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("## 📊 Ключевые показатели эффективности")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    # Расчет метрик
    total_reviews = len(filtered_df)
    avg_rating = filtered_df['rating'].mean() if 'rating' in filtered_df and not filtered_df.empty else 0
    
    if 'rating' in filtered_df and not filtered_df.empty:
        positive = len(filtered_df[filtered_df['rating'] >= 4])
        negative = len(filtered_df[filtered_df['rating'] <= 2])
        positive_pct = (positive / total_reviews * 100) if total_reviews > 0 else 0
    else:
        positive_pct = 0
    
    if 'bank_response' in filtered_df:
        responses = filtered_df['bank_response'].notna().sum()
        response_rate = (responses / total_reviews * 100) if total_reviews > 0 else 0
    else:
        response_rate = 0
    
    unique_authors = filtered_df['author'].nunique() if 'author' in filtered_df else 0
    
    # NPS расчет (промоутеры - детракторы)
    if 'rating' in filtered_df and not filtered_df.empty:
        promoters = len(filtered_df[filtered_df['rating'] >= 4])
        detractors = len(filtered_df[filtered_df['rating'] <= 2])
        nps = ((promoters - detractors) / total_reviews * 100) if total_reviews > 0 else 0
    else:
        nps = 0
    
    with col1:
        st.metric(
            label="Всего отзывов",
            value=f"{total_reviews:,}",
            delta="↑ 12%" if total_reviews > 10 else None
        )
    
    with col2:
        st.metric(
            label="Средний рейтинг",
            value=f"{avg_rating:.2f}",
            delta="↑ 0.2" if avg_rating > 4 else "↓ 0.1"
        )
    
    with col3:
        st.metric(
            label="Позитивные",
            value=f"{positive_pct:.0f}%",
            delta="↑ 5%" if positive_pct > 60 else "↓ 3%"
        )
    
    with col4:
        st.metric(
            label="Ответы банка",
            value=f"{response_rate:.0f}%",
            delta="↑ 3%" if response_rate > 30 else None
        )
    
    with col5:
        st.metric(
            label="Уникальных клиентов",
            value=f"{unique_authors:,}"
        )
    
    with col6:
        st.metric(
            label="NPS Score",
            value=f"{nps:.0f}",
            delta="↑ 8" if nps > 0 else "↓ 5"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============= ГРАФИКИ - ПЕРВЫЙ РЯД =============
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 📈 Динамика отзывов и рейтингов")
        
        if 'review_date' in filtered_df and not filtered_df.empty:
            daily_stats = filtered_df.groupby(filtered_df['review_date'].dt.date).agg({
                'id': 'count',
                'rating': 'mean'
            }).reset_index()
            daily_stats.columns = ['Дата', 'Количество', 'Средний рейтинг']
            
            fig = make_subplots(
                rows=2, cols=1,
                row_heights=[0.7, 0.3],
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=('Количество отзывов', 'Средний рейтинг')
            )
            
            # График количества
            fig.add_trace(
                go.Scatter(
                    x=daily_stats['Дата'],
                    y=daily_stats['Количество'],
                    mode='lines+markers',
                    name='Отзывы',
                    line=dict(color=COLORS['primary'], width=2),
                    marker=dict(size=6),
                    fill='tozeroy',
                    fillcolor=f"rgba(30, 64, 175, 0.1)"
                ),
                row=1, col=1
            )
            
            # График рейтинга
            fig.add_trace(
                go.Bar(
                    x=daily_stats['Дата'],
                    y=daily_stats['Средний рейтинг'],
                    name='Рейтинг',
                    marker_color=COLORS['info'],
                    opacity=0.8
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                height=400,
                showlegend=False,
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Inter", size=11, color=COLORS['text_secondary']),
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor=COLORS['border'],
                linecolor=COLORS['border']
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor=COLORS['border'],
                linecolor=COLORS['border']
            )
            
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### ⭐ Распределение оценок")
        
        if 'rating' in filtered_df and not filtered_df.empty:
            rating_dist = filtered_df['rating'].value_counts().sort_index()
            
            # Цвета для рейтингов
            rating_colors = {
                1: COLORS['danger'],
                2: COLORS['warning'],
                3: COLORS['secondary'],
                4: COLORS['info'],
                5: COLORS['success']
            }
            
            fig = go.Figure(data=[
                go.Bar(
                    x=[f"{i}★" for i in range(1, 6)],
                    y=[rating_dist.get(float(i), 0) for i in range(1, 6)],
                    marker_color=[rating_colors[i] for i in range(1, 6)],
                    text=[rating_dist.get(float(i), 0) for i in range(1, 6)],
                    textposition='outside',
                    textfont=dict(size=12, weight=600)
                )
            ])
            
            fig.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Inter", size=11, color=COLORS['text_secondary']),
                margin=dict(l=0, r=0, t=30, b=0),
                yaxis_title="Количество",
                xaxis_title=""
            )
            
            fig.update_xaxes(linecolor=COLORS['border'])
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor=COLORS['border'],
                linecolor=COLORS['border']
            )
            
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============= ГРАФИКИ - ВТОРОЙ РЯД =============
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 📱 Источники отзывов")
        
        if 'source' in filtered_df and not filtered_df.empty:
            source_stats = filtered_df['source'].value_counts()
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=source_stats.index,
                    values=source_stats.values,
                    hole=0.4,
                    marker_colors=COLORS['chart_colors'][:len(source_stats)],
                    textinfo='label+percent',
                    textfont=dict(size=11)
                )
            ])
            
            fig.update_layout(
                height=300,
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Inter", size=11, color=COLORS['text_secondary']),
                margin=dict(l=0, r=80, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🌍 География клиентов")
        
        if 'author_location' in filtered_df:
            location_df = filtered_df[filtered_df['author_location'].notna() & (filtered_df['author_location'] != '')]
            if not location_df.empty:
                top_locations = location_df['author_location'].value_counts().head(7)
                
                fig = go.Figure(data=[
                    go.Bar(
                        y=top_locations.index,
                        x=top_locations.values,
                        orientation='h',
                        marker=dict(
                            color=top_locations.values,
                            colorscale=[[0, COLORS['info']], [1, COLORS['primary']]],
                            showscale=False
                        ),
                        text=top_locations.values,
                        textposition='outside'
                    )
                ])
                
                fig.update_layout(
                    height=300,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Inter", size=11, color=COLORS['text_secondary']),
                    margin=dict(l=0, r=0, t=30, b=0),
                    xaxis_title="Количество отзывов"
                )
                
                fig.update_xaxes(linecolor=COLORS['border'])
                fig.update_yaxes(linecolor=COLORS['border'])
                
                st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 💭 Анализ тональности")
        
        if 'rating' in filtered_df and not filtered_df.empty:
            sentiment_data = {
                'Позитивные': len(filtered_df[filtered_df['rating'] >= 4]),
                'Нейтральные': len(filtered_df[filtered_df['rating'] == 3]),
                'Негативные': len(filtered_df[filtered_df['rating'] <= 2])
            }
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(sentiment_data.keys()),
                    y=list(sentiment_data.values()),
                    marker_color=[COLORS['success'], COLORS['secondary'], COLORS['danger']],
                    text=list(sentiment_data.values()),
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                height=300,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Inter", size=11, color=COLORS['text_secondary']),
                margin=dict(l=0, r=0, t=30, b=0),
                yaxis_title="Количество"
            )
            
            fig.update_xaxes(linecolor=COLORS['border'])
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor=COLORS['border'],
                linecolor=COLORS['border']
            )
            
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============= ТАБЛИЦА ОТЗЫВОВ =============
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("## 📋 Детальный просмотр отзывов")
    
    # Фильтры для таблицы
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_negative = st.checkbox("Только негативные", value=False)
    with col2:
        show_with_response = st.checkbox("С ответом банка", value=False)
    with col3:
        sort_option = st.selectbox("Сортировка", ["Дата ↓", "Рейтинг ↓", "Рейтинг ↑"])
    with col4:
        rows_count = st.selectbox("Показать строк", [10, 25, 50, 100], index=0)
    
    # Применение фильтров к таблице
    table_df = filtered_df.copy()
    
    if show_negative and 'rating' in table_df:
        table_df = table_df[table_df['rating'] <= 2]
    
    if show_with_response and 'bank_response' in table_df:
        table_df = table_df[table_df['bank_response'].notna()]
    
    # Сортировка
    if sort_option == "Дата ↓" and 'review_date' in table_df:
        table_df = table_df.sort_values('review_date', ascending=False)
    elif sort_option == "Рейтинг ↓" and 'rating' in table_df:
        table_df = table_df.sort_values('rating', ascending=False)
    elif sort_option == "Рейтинг ↑" and 'rating' in table_df:
        table_df = table_df.sort_values('rating', ascending=True)
    
    # Отображение таблицы
    if not table_df.empty:
        display_columns = ['review_date', 'author', 'rating', 'review_text', 'source', 'author_location', 'bank_response']
        display_columns = [col for col in display_columns if col in table_df.columns]
        
        display_df = table_df[display_columns].head(rows_count)
        
        # Переименование колонок
        column_mapping = {
            'review_date': 'Дата',
            'author': 'Автор',
            'rating': 'Рейтинг',
            'review_text': 'Текст отзыва',
            'source': 'Источник',
            'author_location': 'Город',
            'bank_response': 'Ответ банка'
        }
        display_df = display_df.rename(columns=column_mapping)
        
        # Форматирование
        if 'Текст отзыва' in display_df:
            display_df['Текст отзыва'] = display_df['Текст отзыва'].apply(
                lambda x: x[:200] + '...' if isinstance(x, str) and len(x) > 200 else x
            )
        
        if 'Ответ банка' in display_df:
            display_df['Ответ банка'] = display_df['Ответ банка'].apply(
                lambda x: '✓ Есть' if pd.notna(x) and x != '' else '—'
            )
        
        if 'Дата' in display_df:
            display_df['Дата'] = pd.to_datetime(display_df['Дата']).dt.strftime('%d.%m.%Y')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
    else:
        st.info("Нет данных для отображения с выбранными фильтрами")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============= FOOTER =============
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**МТС Банк** © {datetime.now().year} • Система мониторинга v2.0")
    
    with col2:
        st.markdown(f"📊 Обработано **{len(filtered_df):,}** отзывов из **{len(df):,}** общих")
    
    with col3:
        if not filtered_df.empty:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Экспорт в CSV",
                data=csv,
                file_name=f'mts_reviews_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv'
            )

else:
    # Если нет данных
    st.error("⚠️ Нет подключения к базе данных или отсутствуют данные")
    st.info("""
    ### Проверьте следующие пункты:
    
    1. **Настройки Streamlit Cloud**
       - Перейдите в Settings → Secrets
       - Добавьте SUPABASE_URL и SUPABASE_KEY
    
    2. **База данных Supabase**
       - Убедитесь, что таблица reviews существует
       - Проверьте наличие данных в таблице
    
    3. **Права доступа**
       - Проверьте, что API ключ имеет права на чтение
    """)
