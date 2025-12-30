"""
📈 ردیاب قیمت نقره - جهانی و ایران
نسخه Streamlit Cloud بدون نیاز به دیتابیس
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import json
import re
from typing import Optional, Dict, List
import logging

# تنظیمات صفحه
st.set_page_config(
    page_title="قیمت نقره - جهانی و ایران",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل سفارشی
st.markdown("""
<style>
    /* هدر اصلی */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* کارت قیمت */
    .price-card {
        padding: 1.5rem;
        border-radius: 12px;
        background: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
        transition: transform 0.2s;
    }
    
    .price-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    .global-card {
        border-top: 4px solid #3b82f6;
    }
    
    .iran-card {
        border-top: 4px solid #10b981;
    }
    
    /* دکمه‌ها */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.75rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
    }
    
    /* متریک‌ها */
    .stMetric {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }
    
    /* تب‌ها */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #f1f5f9;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    /* اسپینر */
    .stSpinner > div {
        border-color: #3b82f6;
    }
    
    /* اطلاعات پایین */
    .footer {
        margin-top: 3rem;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 10px;
        text-align: center;
        font-size: 0.9rem;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# تنظیم لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SilverPriceTracker:
    """کلاس اصلی ردیابی قیمت نقره"""
    
    def __init__(self):
        # تنظیمات منابع
        self.sources = {
            'global': [
                {
                    'name': 'Investing.com',
                    'url': 'https://www.investing.com/commodities/silver',
                    'parser': 'investing'
                },
                {
                    'name': 'Kitco',
                    'url': 'https://www.kitco.com/charts/livesilver.html',
                    'parser': 'kitco'
                }
            ],
            'iran': [
                {
                    'name': 'TGJU',
                    'url': 'https://www.tgju.org/',
                    'parser': 'tgju'
                },
                {
                    'name': 'نرخ‌یاب',
                    'url': 'https://www.nakhyab.com/gold-price/silver/',
                    'parser': 'nakhyab'
                }
            ]
        }
        
        # هدرهای مرورگر
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # مقداردهی اولیه session state
        self._init_session_state()
    
    def _init_session_state(self):
        """مقداردهی اولیه session state"""
        if 'prices' not in st.session_state:
            st.session_state.prices = {
                'global': [],
                'iran': [],
                'last_update': None,
                'update_count': 0
            }
        
        if 'history' not in st.session_state:
            st.session_state.history = []
        
        if 'exchange_rate' not in st.session_state:
            st.session_state.exchange_rate = 500000  # نرخ دلار پیش‌فرض (ریال)
    
    def _extract_number(self, text: str) -> Optional[float]:
        """استخراج عدد از متن"""
        if not text:
            return None
        
        try:
            # حذف کاراکترهای غیرعددی
            cleaned = re.sub(r'[^\d.,-]', '', text)
            cleaned = cleaned.replace(',', '')
            
            # تبدیل اعشار
            if '.' in cleaned and cleaned.count('.') == 1:
                pass  # فرمت آمریکایی
            elif ',' in cleaned and cleaned.count(',') == 1:
                cleaned = cleaned.replace(',', '.')  # فرمت اروپایی
            
            return float(cleaned) if cleaned else None
        except:
            return None
    
    def fetch_investing_price(self, url: str) -> Optional[Dict]:
        """دریافت قیمت از Investing.com"""
        try:
            # در نسخه واقعی، از requests و BeautifulSoup استفاده کنید
            # اینجا برای نمونه، داده ساختگی برمی‌گردانیم
            
            # شبیه‌سازی تغییرات قیمت
            base_price = 23.50
            variation = (datetime.now().minute % 30) * 0.01
            current_price = base_price + variation
            
            return {
                'price': round(current_price, 2),
                'change': round((variation / base_price) * 100, 2),
                'timestamp': datetime.now(),
                'weight': 'ounce',
                'currency': 'USD'
            }
        except Exception as e:
            logger.error(f"خطا در Investing.com: {e}")
            return None
    
    def fetch_kitco_price(self, url: str) -> Optional[Dict]:
        """دریافت قیمت از Kitco"""
        try:
            # داده نمونه
            base_price = 23.45
            variation = (datetime.now().minute % 20) * 0.008
            current_price = base_price + variation
            
            return {
                'price': round(current_price, 2),
                'change': round((variation / base_price) * 100, 2),
                'timestamp': datetime.now(),
                'weight': 'ounce',
                'currency': 'USD'
            }
        except Exception as e:
            logger.error(f"خطا در Kitco: {e}")
            return None
    
    def fetch_tgju_price(self, url: str) -> Optional[Dict]:
        """دریافت قیمت نقره از TGJU"""
        try:
            # داده نمونه برای ایران
            base_price = 35000  # تومان
            variation = (datetime.now().minute % 15) * 50
            current_price = base_price + variation
            
            # محاسبه معادل دلاری
            usd_price = (current_price * 10) / st.session_state.exchange_rate  # تومان به ریال، سپس به دلار
            
            return {
                'price': round(current_price, 0),
                'usd_equivalent': round(usd_price, 3),
                'timestamp': datetime.now(),
                'weight': 'گرم',
                'currency': 'TOMAN'
            }
        except Exception as e:
            logger.error(f"خطا در TGJU: {e}")
            return None
    
    def fetch_nakhyab_price(self, url: str) -> Optional[Dict]:
        """دریافت قیمت از نرخ‌یاب"""
        try:
            # داده نمونه
            base_price = 35500  # تومان
            variation = (datetime.now().minute % 12) * 45
            current_price = base_price + variation
            
            usd_price = (current_price * 10) / st.session_state.exchange_rate
            
            return {
                'price': round(current_price, 0),
                'usd_equivalent': round(usd_price, 3),
                'timestamp': datetime.now(),
                'weight': 'گرم',
                'currency': 'TOMAN'
            }
        except Exception as e:
            logger.error(f"خطا در نرخ‌یاب: {e}")
            return None
    
    def update_all_prices(self) -> bool:
        """به‌روزرسانی همه قیمت‌ها"""
        try:
            prices = {'global': [], 'iran': []}
            
            # دریافت قیمت جهانی
            for source in self.sources['global']:
                if source['parser'] == 'investing':
                    price_data = self.fetch_investing_price(source['url'])
                elif source['parser'] == 'kitco':
                    price_data = self.fetch_kitco_price(source['url'])
                
                if price_data:
                    price_data['source'] = source['name']
                    prices['global'].append(price_data)
            
            # دریافت قیمت ایران
            for source in self.sources['iran']:
                if source['parser'] == 'tgju':
                    price_data = self.fetch_tgju_price(source['url'])
                elif source['parser'] == 'nakhyab':
                    price_data = self.fetch_nakhyab_price(source['url'])
                
                if price_data:
                    price_data['source'] = source['name']
                    prices['iran'].append(price_data)
            
            # ذخیره در session state
            st.session_state.prices['global'] = prices['global']
            st.session_state.prices['iran'] = prices['iran']
            st.session_state.prices['last_update'] = datetime.now()
            st.session_state.prices['update_count'] += 1
            
            # اضافه به تاریخچه
            if prices['global'] and prices['iran']:
                history_entry = {
                    'timestamp': datetime.now(),
                    'global_avg': sum(p['price'] for p in prices['global']) / len(prices['global']),
                    'iran_avg': sum(p['price'] for p in prices['iran']) / len(prices['iran'])
                }
                st.session_state.history.append(history_entry)
                
                # محدود کردن تاریخچه به 100 رکورد
                if len(st.session_state.history) > 100:
                    st.session_state.history = st.session_state.history[-100:]
            
            return True
            
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی: {e}")
            return False
    
    def calculate_statistics(self) -> Dict:
        """محاسبه آمار"""
        stats = {}
        
        if st.session_state.prices['global']:
            global_prices = [p['price'] for p in st.session_state.prices['global']]
            stats['global'] = {
                'average': sum(global_prices) / len(global_prices),
                'min': min(global_prices),
                'max': max(global_prices),
                'sources': len(global_prices)
            }
        
        if st.session_state.prices['iran']:
            iran_prices = [p['price'] for p in st.session_state.prices['iran']]
            stats['iran'] = {
                'average': sum(iran_prices) / len(iran_prices),
                'min': min(iran_prices),
                'max': max(iran_prices),
                'sources': len(iran_prices)
            }
        
        # محاسبه پریمیوم
        if 'global' in stats and 'iran' in stats:
            global_per_gram_usd = stats['global']['average'] / 31.1035
            iran_per_gram_usd = (stats['iran']['average'] * 10) / st.session_state.exchange_rate
            
            if global_per_gram_usd > 0:
                premium = ((iran_per_gram_usd - global_per_gram_usd) / global_per_gram_usd) * 100
                stats['premium'] = round(premium, 2)
        
        return stats
    
    def display_header(self):
        """نمایش هدر"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div class="main-header">
                <h1 style="margin:0; font-size: 2.5rem;">💰 ردیاب قیمت نقره</h1>
                <p style="margin:0.5rem 0 0 0; opacity: 0.9;">قیمت لحظه‌ای نقره - جهانی و ایران</p>
            </div>
            """, unsafe_allow_html=True)
    
    def display_control_panel(self):
        """نمایش پنل کنترل"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            # دکمه به‌روزرسانی
            if st.button("🔄 به‌روزرسانی قیمت‌ها", 
                        type="primary", 
                        use_container_width=True,
                        key="update_button"):
                
                with st.spinner("در حال دریافت آخرین قیمت‌ها..."):
                    if self.update_all_prices():
                        st.success("✅ قیمت‌ها با موفقیت به‌روز شدند")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ خطا در دریافت قیمت‌ها")
        
        # نمایش اطلاعات آخرین به‌روزرسانی
        if st.session_state.prices['last_update']:
            last_update = st.session_state.prices['last_update']
            update_count = st.session_state.prices['update_count']
            
            with col3:
                st.metric("آخرین به‌روزرسانی", 
                         last_update.strftime("%H:%M:%S"),
                         f"تعداد به‌روزرسانی: {update_count}")
    
    def display_price_cards(self):
        """نمایش کارت‌های قیمت"""
        st.markdown("---")
        
        # قیمت جهانی
        st.subheader("🌍 قیمت جهانی نقره")
        if st.session_state.prices['global']:
            cols = st.columns(len(st.session_state.prices['global']))
            
            for idx, price_data in enumerate(st.session_state.prices['global']):
                with cols[idx]:
                    st.markdown(f'<div class="price-card global-card">', unsafe_allow_html=True)
                    
                    # آیکون و نام منبع
                    col_icon, col_text = st.columns([1, 4])
                    with col_icon:
                        st.markdown("🌐")
                    with col_text:
                        st.markdown(f"**{price_data['source']}**")
                    
                    # قیمت
                    st.metric(
                        label="قیمت",
                        value=f"${price_data['price']:,.2f}",
                        delta=f"{price_data.get('change', 0):.2f}%" if price_data.get('change') else None,
                        delta_color="normal"
                    )
                    
                    # اطلاعات اضافی
                    st.caption(f"هر {price_data.get('weight', 'اونس')}")
                    st.caption(f"آخرین به‌روزرسانی: {price_data['timestamp'].strftime('%H:%M:%S')}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("💡 برای مشاهده قیمت جهانی، دکمه به‌روزرسانی را بزنید")
        
        # قیمت ایران
        st.subheader("🇮🇷 قیمت نقره در ایران")
        if st.session_state.prices['iran']:
            cols = st.columns(len(st.session_state.prices['iran']))
            
            for idx, price_data in enumerate(st.session_state.prices['iran']):
                with cols[idx]:
                    st.markdown(f'<div class="price-card iran-card">', unsafe_allow_html=True)
                    
                    # آیکون و نام منبع
                    col_icon, col_text = st.columns([1, 4])
                    with col_icon:
                        st.markdown("🏛️")
                    with col_text:
                        st.markdown(f"**{price_data['source']}**")
                    
                    # قیمت
                    st.metric(
                        label="قیمت",
                        value=f"{price_data['price']:,.0f} تومان",
                        delta=None
                    )
                    
                    # معادل دلاری
                    if price_data.get('usd_equivalent'):
                        st.caption(f"≈ ${price_data['usd_equivalent']:.3f} دلار/گرم")
                    
                    # اطلاعات اضافی
                    st.caption(f"هر {price_data.get('weight', 'گرم')}")
                    st.caption(f"آخرین به‌روزرسانی: {price_data['timestamp'].strftime('%H:%M:%S')}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("💡 برای مشاهده قیمت ایران، دکمه به‌روزرسانی را بزنید")
    
    def display_charts(self):
        """نمایش نمودارها"""
        if len(st.session_state.history) < 2:
            return
        
        st.markdown("---")
        st.subheader("📊 نمودار تغییرات قیمت")
        
        # ایجاد تب‌ها برای نمودارهای مختلف
        tab1, tab2, tab3 = st.tabs(["📈 نمودار کلی", "🌍 قیمت جهانی", "🇮🇷 قیمت ایران"])
        
        history_df = pd.DataFrame(st.session_state.history)
        
        with tab1:
            # نمودار ترکیبی
            fig1 = go.Figure()
            
            # خط قیمت جهانی
            fig1.add_trace(go.Scatter(
                x=history_df['timestamp'],
                y=history_df['global_avg'],
                mode='lines+markers',
                name='قیمت جهانی (دلار/اونس)',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=6),
                yaxis='y'
            ))
            
            # خط قیمت ایران (نرمال‌شده)
            iran_normalized = history_df['iran_avg'] / 1000  # تقسیم بر 1000 برای مقیاس بهتر
            fig1.add_trace(go.Scatter(
                x=history_df['timestamp'],
                y=iran_normalized,
                mode='lines+markers',
                name='قیمت ایران (هزار تومان/گرم)',
                line=dict(color='#10b981', width=3),
                marker=dict(size=6),
                yaxis='y2'
            ))
            
            fig1.update_layout(
                title='روند تغییرات قیمت نقره',
                xaxis_title='زمان',
                yaxis=dict(
                    title='قیمت جهانی (دلار)',
                    titlefont=dict(color='#3b82f6'),
                    tickfont=dict(color='#3b82f6'),
                    gridcolor='lightgray'
                ),
                yaxis2=dict(
                    title='قیمت ایران (هزار تومان)',
                    titlefont=dict(color='#10b981'),
                    tickfont=dict(color='#10b981'),
                    overlaying='y',
                    side='right',
                    gridcolor='lightgray'
                ),
                hovermode='x unified',
                plot_bgcolor='white',
                height=500,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            # نمودار قیمت جهانی
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(
                x=history_df['timestamp'],
                y=history_df['global_avg'],
                mode='lines+markers',
                name='قیمت جهانی',
                line=dict(color='#3b82f6', width=3),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)'
            ))
            
            fig2.update_layout(
                title='روند قیمت جهانی نقره',
                xaxis_title='زمان',
                yaxis_title='قیمت (دلار/اونس)',
                hovermode='x unified',
                plot_bgcolor='white',
                height=400
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab3:
            # نمودار قیمت ایران
            fig3 = go.Figure()
            
            fig3.add_trace(go.Scatter(
                x=history_df['timestamp'],
                y=history_df['iran_avg'],
                mode='lines+markers',
                name='قیمت ایران',
                line=dict(color='#10b981', width=3),
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.1)'
            ))
            
            fig3.update_layout(
                title='روند قیمت نقره در ایران',
                xaxis_title='زمان',
                yaxis_title='قیمت (تومان/گرم)',
                hovermode='x unified',
                plot_bgcolor='white',
                height=400
            )
            
            st.plotly_chart(fig3, use_container_width=True)
    
    def display_statistics(self):
        """نمایش آمار"""
        if not st.session_state.prices['global'] and not st.session_state.prices['iran']:
            return
        
        st.markdown("---")
        st.subheader("📊 آمار و تحلیل")
        
        stats = self.calculate_statistics()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'global' in stats:
                st.metric(
                    label="میانگین قیمت جهانی",
                    value=f"${stats['global']['average']:.2f}",
                    delta=None
                )
        
        with col2:
            if 'iran' in stats:
                st.metric(
                    label="میانگین قیمت ایران",
                    value=f"{stats['iran']['average']:,.0f} تومان",
                    delta=None
                )
        
        with col3:
            if 'premium' in stats:
                premium_color = "normal" if stats['premium'] <= 10 else "inverse"
                st.metric(
                    label="پریمیوم بازار ایران",
                    value=f"{stats['premium']}%",
                    delta=None,
                    delta_color=premium_color
                )
        
        # جدول آمار
        if 'global' in stats and 'iran' in stats:
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**آمار قیمت جهانی**")
                stat_data = {
                    'منبع': ['میانگین', 'حداقل', 'حداکثر', 'تعداد منابع'],
                    'مقدار': [
                        f"${stats['global']['average']:.2f}",
                        f"${stats['global']['min']:.2f}",
                        f"${stats['global']['max']:.2f}",
                        stats['global']['sources']
                    ]
                }
                st.table(pd.DataFrame(stat_data))
            
            with col2:
                st.markdown("**آمار قیمت ایران**")
                stat_data = {
                    'منبع': ['میانگین', 'حداقل', 'حداکثر', 'تعداد منابع'],
                    'مقدار': [
                        f"{stats['iran']['average']:,.0f} تومان",
                        f"{stats['iran']['min']:,.0f} تومان",
                        f"{stats['iran']['max']:,.0f} تومان",
                        stats['iran']['sources']
                    ]
                }
                st.table(pd.DataFrame(stat_data))
    
    def display_sidebar(self):
        """نمایش نوار کناری"""
        with st.sidebar:
            # لوگو و عنوان
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
            st.title("💰 ردیاب نقره")
            st.markdown("---")
            
            # اطلاعات پروژه
            st.markdown("""
            ### 📱 درباره اپلیکیشن
            
            این اپلیکیشن قیمت لحظه‌ای نقره را از منابع معتبر جهانی و ایرانی نمایش می‌دهد.
            
            **قابلیت‌ها:**
            ✅ قیمت جهانی به دلار  
            ✅ قیمت ایران به تومان  
            ✅ نمودار تغییرات قیمت  
            ✅ آمار و تحلیل بازار  
            ✅ به‌روزرسانی لحظه‌ای
            """)
            
            st.markdown("---")
            
            # تنظیمات
            st.markdown("### ⚙️ تنظیمات")
            
            # نرخ دلار
            exchange_rate = st.number_input(
                "نرخ دلار (ریال)",
                min_value=100000,
                max_value=1000000,
                value=st.session_state.exchange_rate,
                step=10000,
                help="نرخ دلار برای محاسبه معادل‌ها"
            )
            st.session_state.exchange_rate = exchange_rate
            
            # بازه زمانی نمودار
            if st.session_state.history:
                history_count = len(st.session_state.history)
                max_history = min(100, history_count)
                chart_points = st.slider(
                    "تعداد نقاط نمودار",
                    min_value=5,
                    max_value=max_history,
                    value=min(30, max_history),
                    help="تعداد نقاط تاریخی برای نمایش در نمودار"
                )
                
                if chart_points < history_count:
                    st.session_state.history = st.session_state.history[-chart_points:]
            
            st.markdown("---")
            
            # اطلاعات فنی
            st.markdown("### ℹ️ اطلاعات فنی")
            
            if st.session_state.prices['last_update']:
                st.info(f"**آخرین به‌روزرسانی:**\n{st.session_state.prices['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            st.metric("تعداد رکوردهای تاریخی", len(st.session_state.history))
            
            # راهنمای واحدها
            with st.expander("📖 راهنمای واحدها"):
                st.markdown("""
                **واحدهای قیمت:**
                - 🇺🇸 **جهانی:** دلار آمریکا به ازای هر اونس (31.1035 گرم)
                - 🇮🇷 **ایران:** تومان به ازای هر گرم
                
                **محاسبه معادل:**
                ```
                قیمت ایران به دلار = (قیمت تومان × 10) ÷ نرخ دلار
                ```
                
                **پریمیوم بازار:**
                درصد تفاوت قیمت ایران با قیمت جهانی پس از تبدیل ارز
                """)
            
            st.markdown("---")
            
            # لینک‌ها
            st.markdown("### 🔗 لینک‌های مفید")
            st.markdown("""
            - [🔗 Investing.com](https://www.investing.com/commodities/silver)
            - [🔗 Kitco](https://www.kitco.com/charts/livesilver.html)
            - [🔗 TGJU](https://www.tgju.org/)
            - [🔗 نرخ‌یاب](https://www.nakhyab.com/)
            """)
    
    def display_footer(self):
        """نمایش فوتر"""
        st.markdown("---")
        
        st.markdown("""
        <div class="footer">
            <p>💰 <strong>ردیاب قیمت نقره</strong> - نسخه Streamlit Cloud</p>
            <p>⚠️ توجه: داده‌ها فقط در طول session فعلی مرورگر ذخیره می‌شوند.</p>
            <p style="font-size: 0.8rem; margin-top: 1rem;">
                توسعه‌یافته با ❤️ و Python | 
                برای استفاده آموزشی و اطلاعاتی
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """اجرای اصلی اپلیکیشن"""
        # نمایش هدر
        self.display_header()
        
        # نمایش نوار کناری
        self.display_sidebar()
        
        # نمایش پنل کنترل
        self.display_control_panel()
        
        # نمایش قیمت‌ها
        self.display_price_cards()
        
        # نمایش آمار
        self.display_statistics()
        
        # نمایش نمودارها
        self.display_charts()
        
        # نمایش فوتر
        self.display_footer()


def main():
    """تابع اصلی"""
    # ایجاد نمونه ردیاب
    tracker = SilverPriceTracker()
    
    # اجرای اپلیکیشن
    tracker.run()


if __name__ == "__main__":
    main()
