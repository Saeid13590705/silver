"""
💰 ردیاب قیمت نقره - جهانی و ایران
نسخه فوق‌ساده بدون dependency اضافه
"""

import streamlit as st
from datetime import datetime, timedelta
import time
import random

# تنظیمات صفحه
st.set_page_config(
    page_title="قیمت نقره - جهانی و ایران",
    page_icon="💰",
    layout="wide"
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
    }
    
    .price-card {
        padding: 1.5rem;
        border-radius: 12px;
        background: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    .global-card {
        border-top: 4px solid #3b82f6;
    }
    
    .iran-card {
        border-top: 4px solid #10b981;
    }
    
    .footer {
        margin-top: 3rem;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 10px;
        text-align: center;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)


class SilverPriceTracker:
    """ردیاب قیمت نقره بدون نیاز به dependency"""
    
    def __init__(self):
        # مقداردهی اولیه session state
        if 'prices' not in st.session_state:
            st.session_state.prices = {
                'global': None,
                'iran': None,
                'last_update': None,
                'history': []
            }
        
        if 'exchange_rate' not in st.session_state:
            st.session_state.exchange_rate = 500000  # ریال
    
    def generate_sample_global_price(self):
        """تولید قیمت نمونه جهانی"""
        base_price = 23.50
        # تغییر کوچک تصادفی
        variation = random.uniform(-0.2, 0.2)
        current_price = base_price + variation
        
        return {
            'price': round(current_price, 2),
            'change': round((variation / base_price) * 100, 2),
            'source': 'Investing.com',
            'timestamp': datetime.now()
        }
    
    def generate_sample_iran_price(self):
        """تولید قیمت نمونه ایران"""
        base_price = 35000  # تومان
        variation = random.uniform(-100, 100)
        current_price = base_price + variation
        
        # محاسبه معادل دلاری
        usd_price = (current_price * 10) / st.session_state.exchange_rate
        
        return {
            'price': round(current_price, 0),
            'usd_equivalent': round(usd_price, 3),
            'source': 'TGJU',
            'timestamp': datetime.now()
        }
    
    def update_prices(self):
        """به‌روزرسانی قیمت‌ها"""
        with st.spinner("در حال دریافت قیمت‌ها..."):
            time.sleep(1)  # شبیه‌سازی تاخیر
            
            global_price = self.generate_sample_global_price()
            iran_price = self.generate_sample_iran_price()
            
            st.session_state.prices['global'] = global_price
            st.session_state.prices['iran'] = iran_price
            st.session_state.prices['last_update'] = datetime.now()
            
            # اضافه به تاریخچه
            st.session_state.prices['history'].append({
                'time': datetime.now(),
                'global': global_price['price'],
                'iran': iran_price['price']
            })
            
            # محدود کردن تاریخچه
            if len(st.session_state.prices['history']) > 20:
                st.session_state.prices['history'] = st.session_state.prices['history'][-20:]
            
            return True
    
    def display_header(self):
        """نمایش هدر"""
        st.markdown("""
        <div class="main-header">
            <h1 style="margin:0; font-size: 2.5rem;">💰 ردیاب قیمت نقره</h1>
            <p style="margin:0.5rem 0 0 0; opacity: 0.9;">قیمت لحظه‌ای نقره - جهانی و ایران</p>
        </div>
        """, unsafe_allow_html=True)
    
    def display_control_panel(self):
        """نمایش پنل کنترل"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔄 به‌روزرسانی قیمت‌ها", 
                        type="primary", 
                        use_container_width=True):
                if self.update_prices():
                    st.success("✅ قیمت‌ها به‌روز شدند")
                    time.sleep(1)
                    st.rerun()
    
    def display_price_cards(self):
        """نمایش کارت‌های قیمت"""
        st.markdown("### 🌍 قیمت جهانی نقره")
        
        if st.session_state.prices['global']:
            price = st.session_state.prices['global']
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f'<div class="price-card global-card">', unsafe_allow_html=True)
                st.metric(
                    label=f"{price['source']}",
                    value=f"${price['price']:,.2f}",
                    delta=f"{price['change']:+.2f}%"
                )
                st.caption(f"هر اونس - {price['timestamp'].strftime('%H:%M:%S')}")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("💡 برای مشاهده قیمت، دکمه به‌روزرسانی را بزنید")
        
        st.markdown("### 🇮🇷 قیمت نقره در ایران")
        
        if st.session_state.prices['iran']:
            price = st.session_state.prices['iran']
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f'<div class="price-card iran-card">', unsafe_allow_html=True)
                st.metric(
                    label=f"{price['source']}",
                    value=f"{price['price']:,.0f} تومان",
                    delta=None
                )
                if price.get('usd_equivalent'):
                    st.caption(f"≈ ${price['usd_equivalent']:.3f} دلار/گرم")
                st.caption(f"هر گرم - {price['timestamp'].strftime('%H:%M:%S')}")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("💡 برای مشاهده قیمت، دکمه به‌روزرسانی را بزنید")
    
    def display_history_table(self):
        """نمایش تاریخچه در جدول"""
        if len(st.session_state.prices['history']) > 0:
            st.markdown("---")
            st.markdown("### 📋 تاریخچه قیمت‌ها")
            
            # ایجاد جدول ساده
            history_data = []
            for i, entry in enumerate(reversed(st.session_state.prices['history'])):
                history_data.append({
                    'ردیف': i + 1,
                    'زمان': entry['time'].strftime('%H:%M:%S'),
                    'قیمت جهانی': f"${entry['global']:.2f}",
                    'قیمت ایران': f"{entry['iran']:,.0f} تومان"
                })
            
            # نمایش به صورت markdown table
            table_header = "| ردیف | زمان | قیمت جهانی | قیمت ایران |\n"
            table_separator = "|------|------|-------------|-------------|\n"
            table_rows = ""
            
            for row in history_data:
                table_rows += f"| {row['ردیف']} | {row['زمان']} | {row['قیمت جهانی']} | {row['قیمت ایران']} |\n"
            
            st.markdown(table_header + table_separator + table_rows)
    
    def display_statistics(self):
        """نمایش آمار ساده"""
        if len(st.session_state.prices['history']) > 0:
            st.markdown("---")
            st.markdown("### 📊 آمار")
            
            global_prices = [h['global'] for h in st.session_state.prices['history']]
            iran_prices = [h['iran'] for h in st.session_state.prices['history']]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("میانگین جهانی", f"${sum(global_prices)/len(global_prices):.2f}")
            
            with col2:
                st.metric("میانگین ایران", f"{sum(iran_prices)/len(iran_prices):,.0f} تومان")
            
            with col3:
                st.metric("تعداد رکوردها", len(st.session_state.prices['history']))
            
            with col4:
                if st.session_state.prices['last_update']:
                    st.metric("آخرین بروزرسانی", 
                             st.session_state.prices['last_update'].strftime("%H:%M"))
    
    def display_sidebar(self):
        """نمایش نوار کناری"""
        with st.sidebar:
            st.markdown("<h1 style='text-align: center;'>💰</h1>", unsafe_allow_html=True)
            st.markdown("### درباره اپ")
            st.markdown("""
            نمایش قیمت نمونه نقره.
            
            **منابع:**
            - 🌍 جهانی: Investing.com
            - 🇮🇷 ایران: TGJU
            
            **واحدها:**
            - جهانی: دلار/اونس
            - ایران: تومان/گرم
            """)
            
            st.markdown("---")
            
            # تنظیم نرخ دلار
            new_rate = st.number_input(
                "نرخ دلار (ریال)",
                min_value=100000,
                max_value=2000000,
                value=st.session_state.exchange_rate,
                step=10000
            )
            st.session_state.exchange_rate = new_rate
            
            st.markdown("---")
            
            # اطلاعات
            if st.session_state.prices['last_update']:
                st.info(f"آخرین بروزرسانی:\n{st.session_state.prices['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    def display_footer(self):
        """نمایش فوتر"""
        st.markdown("---")
        st.markdown("""
        <div class="footer">
            <p>💰 <strong>ردیاب قیمت نقره</strong> - نسخه نمایشی</p>
            <p>قیمت‌ها نمونه‌ای هستند و واقعی نیستند.</p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """اجرای اصلی"""
        self.display_header()
        self.display_sidebar()
        self.display_control_panel()
        self.display_price_cards()
        self.display_statistics()
        self.display_history_table()
        self.display_footer()


def main():
    """تابع اصلی"""
    tracker = SilverPriceTracker()
    tracker.run()


if __name__ == "__main__":
    main()
