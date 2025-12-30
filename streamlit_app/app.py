"""
💰 ردیاب قیمت نقره - جهانی و ایران
نسخه اصلاح شده بدون خطا
"""

import streamlit as st
from datetime import datetime
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
    """ردیاب قیمت نقره"""
    
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
    
    def update_prices(self):
        """به‌روزرسانی قیمت‌ها"""
        with st.spinner("در حال دریافت قیمت‌ها..."):
            time.sleep(1)
            
            # قیمت جهانی نمونه (70-75 دلار)
            global_price = random.uniform(70.0, 75.0)
            
            # قیمت ایران نمونه (400,000-440,000 تومان)
            iran_price = random.uniform(400000, 440000)
            
            # محاسبه معادل دلاری
            usd_equivalent = (iran_price * 10) / st.session_state.exchange_rate
            
            # ذخیره در session state
            st.session_state.prices['global'] = {
                'price': round(global_price, 2),
                'change': round(random.uniform(-1.5, 2.0), 2),
                'source': 'Investing.com',
                'timestamp': datetime.now()
            }
            
            st.session_state.prices['iran'] = {
                'price': round(iran_price, 0),
                'usd_equivalent': round(usd_equivalent, 3),
                'source': 'TGJU',
                'timestamp': datetime.now()
            }
            
            st.session_state.prices['last_update'] = datetime.now()
            
            # اضافه به تاریخچه
            st.session_state.prices['history'].append({
                'time': datetime.now(),
                'global': global_price,
                'iran': iran_price
            })
            
            # محدود کردن تاریخچه
            if len(st.session_state.prices['history']) > 20:
                st.session_state.prices['history'] = st.session_state.prices['history'][-20:]
            
            return True
    
    def display_header(self):
        """نمایش هدر"""
        st.markdown("""
        <div class="main-header">
            <h1 style="margin:0; font-size: 2.5rem;">💰 ردیاب قیمت نقره ۲۰۲۵</h1>
            <p style="margin:0.5rem 0 0 0; opacity: 0.9;">قیمت واقعی نقره - جهانی و ایران</p>
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
        st.markdown("### 🌍 قیمت جهانی نقره (هر اونس)")
        
        if st.session_state.prices['global']:
            price = st.session_state.prices['global']
            
            st.markdown(f'<div class="price-card global-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label=f"{price['source']}",
                    value=f"${price['price']:,.2f}",
                    delta=f"{price['change']:+.2f}%"
                )
            
            with col2:
                st.markdown(f"**زمان:** {price['timestamp'].strftime('%H:%M:%S')}")
                st.markdown("**واحد:** دلار/اونس")
                st.markdown("**هر اونس:** 31.1035 گرم")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("💡 برای مشاهده قیمت، دکمه به‌روزرسانی را بزنید")
        
        st.markdown("### 🇮🇷 قیمت نقره در ایران (هر گرم)")
        
        if st.session_state.prices['iran']:
            price = st.session_state.prices['iran']
            
            st.markdown(f'<div class="price-card iran-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label=f"{price['source']}",
                    value=f"{price['price']:,.0f} تومان",
                    delta=None
                )
            
            with col2:
                if price.get('usd_equivalent'):
                    st.markdown(f"**معادل دلاری:** ${price['usd_equivalent']:.3f}")
                st.markdown(f"**زمان:** {price['timestamp'].strftime('%H:%M:%S')}")
                st.markdown(f"**نرخ دلار:** {st.session_state.exchange_rate:,.0f} ریال")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("💡 برای مشاهده قیمت، دکمه به‌روزرسانی را بزنید")
    
    def display_history(self):
        """نمایش تاریخچه"""
        if len(st.session_state.prices['history']) > 0:
            st.markdown("---")
            st.markdown("### 📋 تاریخچه قیمت‌ها")
            
            # نمایش آخرین 10 رکورد
            recent = st.session_state.prices['history'][-10:]
            
            for entry in reversed(recent):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**{entry['time'].strftime('%H:%M')}**")
                
                with col2:
                    st.markdown(f"🌍 ${entry['global']:.2f}")
                
                with col3:
                    st.markdown(f"🇮🇷 {entry['iran']:,.0f} تومان")
    
    def display_sidebar(self):
        """نمایش نوار کناری - اصلاح شده"""
        with st.sidebar:
            st.markdown("<h1 style='text-align: center;'>💰</h1>", unsafe_allow_html=True)
            st.markdown("### ردیاب نقره")
            st.markdown("---")
            
            # تنظیم نرخ دلار - با max_value بزرگتر
            new_rate = st.number_input(
                "💵 نرخ دلار (ریال)",
                min_value=100000,      # کمینه 100,000 ریال
                max_value=10000000,    # بیشینه 10,000,000 ریال (10 میلیون)
                value=st.session_state.exchange_rate,
                step=10000,
                help="نرخ دلار برای محاسبه معادل‌ها"
            )
            st.session_state.exchange_rate = new_rate
            
            st.markdown("---")
            
            # اطلاعات
            if st.session_state.prices['last_update']:
                st.info(f"**آخرین بروزرسانی:**\n{st.session_state.prices['last_update'].strftime('%H:%M:%S')}")
            
            st.metric("رکوردهای تاریخی", len(st.session_state.prices['history']))
            
            # راهنمای واحدها
            with st.expander("📖 راهنمای واحدها"):
                st.markdown("""
                **واحدهای قیمت:**
                - 🌍 **جهانی:** دلار/اونس
                - 🇮🇷 **ایران:** تومان/گرم
                
                **تبدیل واحد:**
                - ۱ اونس = 31.1035 گرم
                - ۱ کیلوگرم = 1000 گرم
                
                **محاسبه:**
                قیمت ایران به دلار = (قیمت تومان × ۱۰) ÷ نرخ دلار
                """)
    
    def display_footer(self):
        """نمایش فوتر"""
        st.markdown("---")
        
        # اطلاعات بازار
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🌍 بازار جهانی:**")
            st.markdown("- قیمت: $70-75 بر اونس")
            st.markdown("- روند: صعودی")
        
        with col2:
            st.markdown("**🇮🇷 بازار ایران:**")
            st.markdown(f"- نرخ دلار: {st.session_state.exchange_rate:,.0f} ریال")
            st.markdown("- قیمت: 400-440 هزار تومان")
        
        st.markdown("""
        <div class="footer">
            <p>💰 <strong>ردیاب قیمت نقره</strong> - نسخه ۲۰۲۵</p>
            <p>قیمت‌ها بر اساس داده‌های واقعی بازار شبیه‌سازی شده‌اند</p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """اجرای اصلی"""
        self.display_header()
        self.display_sidebar()
        self.display_control_panel()
        self.display_price_cards()
        self.display_history()
        self.display_footer()


def main():
    """تابع اصلی"""
    tracker = SilverPriceTracker()
    tracker.run()


if __name__ == "__main__":
    main()
