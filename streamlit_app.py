
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="МТС Банк Dashboard", page_icon="🏦", layout="wide")

st.title("🏦 МТС Банк - Мониторинг отзывов")
st.markdown("---")

# Проверка подключения
try:
    from supabase import create_client
    
    # Получаем credentials из secrets
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    
    # Создаем клиент
    supabase = create_client(url, key)
    
    # Запрос данных
    from_date = (datetime.now() - timedelta(days=7)).isoformat()
    response = supabase.table("reviews").select("*").limit(100).execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        
        # Метрики
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Всего отзывов", len(df))
        
        with col2:
            if "rating" in df.columns:
                avg_rating = df["rating"].mean()
                st.metric("⭐ Рейтинг", f"{avg_rating:.1f}")
            else:
                st.metric("⭐ Рейтинг", "N/A")
        
        with col3:
            if "source" in df.columns:
                sources = df["source"].nunique()
                st.metric("📱 Источников", sources)
            else:
                st.metric("📱 Источников", "N/A")
        
        with col4:
            if "author" in df.columns:
                authors = df["author"].nunique()
                st.metric("👥 Авторов", authors)
            else:
                st.metric("👥 Авторов", "N/A")
        
        # График
        st.markdown("---")
        st.subheader("📊 Данные")
        
        # Показываем первые 10 записей
        display_cols = ["review_date", "author", "rating", "source"]
        display_cols = [col for col in display_cols if col in df.columns]
        
        if display_cols:
            st.dataframe(df[display_cols].head(10), use_container_width=True)
        else:
            st.dataframe(df.head(10), use_container_width=True)
            
        # Статистика
        st.markdown("---")
        st.subheader("📈 Статистика")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "source" in df.columns:
                st.write("**По источникам:**")
                source_stats = df["source"].value_counts()
                st.write(source_stats)
        
        with col2:
            if "rating" in df.columns:
                st.write("**По рейтингам:**")
                rating_stats = df["rating"].value_counts().sort_index()
                st.write(rating_stats)
    else:
        st.warning("📭 Нет данных в базе")
        
except Exception as e:
    st.error(f"❌ Ошибка подключения")
    st.code(str(e))
    st.info("""
    Проверьте:
    1. Добавлены ли секреты в Settings → Secrets
    2. Правильные ли ключи SUPABASE_URL и SUPABASE_KEY
    3. Есть ли таблица reviews в Supabase
    """)

# Футер
st.markdown("---")
st.caption(f"Обновлено: {datetime.now().strftime('%H:%M:%S')}")
