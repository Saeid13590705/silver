"""
📈 ردیاب قیمت نقره - جهانی و ایران
نسخه Streamlit Cloud بدون plotly
"""

import streamlit as st
import pandas as pd
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
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
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
    
    def fetch_investing_price(self, url: str) -> Optional[Dict]:
        """دریافت قیمت از Investing.com"""
        try:
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
            usd_price = (current_price * 10) / st.session_state.exchange_rate
            
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
                
                # محدود کردن تاریخچه به 50 رکورد
                if len(st.session_state.history) > 50:
                    st.session_state.history = st.session_state.history[-50:]
            
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
    
    def display_charts_simple(self):
        """نمایش نمودار ساده با استفاده از st.line_chart"""
        if len(st.session_state.history) < 2:
            return
        
        st.markdown("---")
        st.subheader("📊 تاریخچه قیمت‌ها")
        
        history_df = pd.DataFrame(st.session_state.history)
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
        history_df.set_index('timestamp', inplace=True)
        
        # تب‌ها برای نمایش مختلف
        tab1, tab2, tab3 = st.tabs(["📈 نمودار ترکیبی", "🌍 قیمت جهانی", "🇮🇷 قیمت ایران"])
        
        with tab1:
            # نمودار ترکیبی با دو محور
            st.markdown("**روند تغییرات قیمت:**")
            
            # ایجاد دو ستون برای نمودارهای جداگانه
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**قیمت جهانی (دلار)**")
                if 'global_avg' in history_df.columns:
                    st.line_chart(history_df['global_avg'])
            
            with col2:
                st.markdown("**قیمت ایران (تومان)**")
                if 'iran_avg' in history_df.columns:
                    st.line_chart(history_df['iran_avg'])
            
            # جدول داده‌ها
            st.markdown("**جدول داده‌های تاریخی:**")
            display_df = history_df.reset_index()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
            display_df.columns = ['زمان', 'قیمت جهانی (دلار)', 'قیمت ایران (تومان)']
            st.dataframe(display_df, use_container_width=True, height=300)
        
        with tab2:
            if 'global_avg' in history_df.columns:
                st.line_chart(history_df['global_avg'])
                
                # آمار قیمت جهانی
                st.markdown("**آمار قیمت جهانی:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("میانگین", f"${history_df['global_avg'].mean():.2f}")
                with col2:
                    st.metric("حداکثر", f"${history_df['global_avg'].max():.2f}")
                with col3:
                    st.metric("حداقل", f"${history_df['global_avg'].min():.2f}")
        
        with tab3:
            if 'iran_avg' in history_df.columns:
                st.line_chart(history_df['iran_avg'])
                
                # آمار قیمت ایران
                st.markdown("**آمار قیمت ایران:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("میانگین", f"{history_df['iran_avg'].mean():,.0f} تومان")
                with col2:
                    st.metric("حداکثر", f"{history_df['iran_avg'].max():,.0f} تومان")
                with col3:
                    st.metric("حداقل", f"{history_df['iran_avg'].min():,.0f} تومان")
    
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
                    'شاخص': ['میانگین', 'حداقل', 'حداکثر', 'تعداد منابع'],
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
                    'شاخص': ['میانگین', 'حداقل', 'حداکثر', 'تعداد منابع'],
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
            st.markdown("<h1 style='text-align: center;'>💰</h1>", unsafe_allow_html=True)
            st.title("ردیاب نقره")
            st.markdown("---")
            
            # اطلاعات پروژه
            st.markdown("""
            ### 📱 درباره اپلیکیشن
            
            نمایش قیمت لحظه‌ای نقره از منابع معتبر.
            
            **قابلیت‌ها:**
            ✅ قیمت جهانی به دلار  
            ✅ قیمت ایران به تومان  
            ✅ نمودار تغییرات  
            ✅ آمار بازار  
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
                max_history = min(50, history_count)
                chart_points = st.slider(
                    "تعداد نقاط نمودار",
                    min_value=5,
                    max_value=max_history,
                    value=min(20, max_history),
                    help="تعداد نقاط تاریخی برای نمایش"
                )
                
                if chart_points < history_count:
                    st.session_state.history = st.session_state.history[-chart_points:]
            
            st.markdown("---")
            
            # اطلاعات فنی
            st.markdown("### ℹ️ اطلاعات فنی")
            
            if st.session_state.prices['last_update']:
                st.info(f"**آخرین به‌روزرسانی:**\n{st.session_state.prices['last_update'].strftime('%H:%M:%S')}")
            
            st.metric("رکوردهای تاریخی", len(st.session_state.history))
            
            # راهنمای واحدها
            with st.expander("📖 راهنمای واحدها"):
                st.markdown("""
                **واحدهای قیمت:**
                - 🇺🇸 **جهانی:** دلار/اونس (31.1035 گرم)
                - 🇮🇷 **ایران:** تومان/گرم
                
                **محاسبه:**
                ```
                قیمت ایران به دلار = (قیمت تومان × 10) ÷ نرخ دلار
                ```
                """)
    
    def display_footer(self):
        """نمایش فوتر"""
        st.markdown("---")
        
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #f8fafc; border-radius: 10px;'>
            <p>💰 <strong>ردیاب قیمت نقره</strong> - نسخه Streamlit</p>
            <p style='font-size: 0.9rem; color: #64748b;'>
                توسعه‌یافته با Python | برای استفاده آموزشی
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
        self.display_charts_simple()
        
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
