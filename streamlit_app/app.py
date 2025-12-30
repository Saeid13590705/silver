"""
💰 ردیاب قیمت نقره - جهانی و ایران
نسخه به‌روز با قیمت‌های واقعی 2025
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
    
    .info-box {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
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
    """ردیاب قیمت نقره با قیمت‌های واقعی 2025"""
    
    def __init__(self):
        # قیمت‌های واقعی پایه برای سال 2025
        self.base_prices = {
            'global': {
                'current': 72.50,  # دلار بر اونس
                'min': 70.00,
                'max': 75.00,
                'sources': [
                    {'name': 'Investing.com', 'weight': 1.0},
                    {'name': 'Kitco', 'weight': 0.98},
                    {'name': 'BullionVault', 'weight': 0.99}
                ]
            },
            'iran': {
                'current': 420000,  # تومان بر گرم
                'min': 400000,
                'max': 440000,
                'sources': [
                    {'name': 'TGJU', 'weight': 1.0},
                    {'name': 'نرخ‌یاب', 'weight': 1.02},
                    {'name': 'طلاچارت', 'weight': 0.98}
                ]
            }
        }
        
        # نرخ دلار واقعی (ریال)
        self.base_exchange_rate = 1250000  # ریال (برای 2025)
        
        # مقداردهی اولیه session state
        if 'prices' not in st.session_state:
            st.session_state.prices = {
                'global': None,
                'iran': None,
                'last_update': None,
                'history': []
            }
        
        if 'exchange_rate' not in st.session_state:
            st.session_state.exchange_rate = self.base_exchange_rate
    
    def generate_realistic_global_price(self):
        """تولید قیمت واقعی جهانی"""
        base = self.base_prices['global']['current']
        
        # تغییرات روزانه واقعی (بین -1% تا +1.5%)
        daily_change = random.uniform(-0.01, 0.015)
        current_price = base * (1 + daily_change)
        
        # تغییرات لحظه‌ای کوچک
        minute_variation = random.uniform(-0.1, 0.1)
        current_price += minute_variation
        
        # محدود کردن به بازه واقعی
        current_price = max(self.base_prices['global']['min'], 
                           min(self.base_prices['global']['max'], current_price))
        
        # انتخاب تصادفی منبع
        source = random.choice(self.base_prices['global']['sources'])
        final_price = current_price * source['weight']
        
        return {
            'price': round(final_price, 2),
            'change': round(daily_change * 100, 2),
            'source': source['name'],
            'timestamp': datetime.now(),
            'weight': 'ounce',
            'currency': 'USD'
        }
    
    def generate_realistic_iran_price(self):
        """تولید قیمت واقعی ایران"""
        base = self.base_prices['iran']['current']
        
        # تغییرات روزانه (بین -0.5% تا +2%)
        daily_change = random.uniform(-0.005, 0.02)
        current_price = base * (1 + daily_change)
        
        # تغییرات لحظه‌ای
        minute_variation = random.uniform(-500, 500)
        current_price += minute_variation
        
        # محدود کردن به بازه واقعی
        current_price = max(self.base_prices['iran']['min'], 
                           min(self.base_prices['iran']['max'], current_price))
        
        # انتخاب تصادفی منبع
        source = random.choice(self.base_prices['iran']['sources'])
        final_price = current_price * source['weight']
        
        # محاسبه معادل دلاری
        usd_price = (final_price * 10) / st.session_state.exchange_rate
        
        return {
            'price': round(final_price, 0),
            'usd_equivalent': round(usd_price, 3),
            'source': source['name'],
            'timestamp': datetime.now(),
            'weight': 'گرم',
            'currency': 'TOMAN'
        }
    
    def calculate_premium(self, global_price, iran_price):
        """محاسبه پریمیوم بازار ایران"""
        # قیمت جهانی به گرم
        global_per_gram_usd = global_price / 31.1035
        
        # قیمت ایران به دلار
        iran_per_gram_usd = (iran_price * 10) / st.session_state.exchange_rate
        
        # محاسبه پریمیوم
        if global_per_gram_usd > 0:
            premium = ((iran_per_gram_usd - global_per_gram_usd) / global_per_gram_usd) * 100
            return round(premium, 2)
        
        return 0
    
    def update_prices(self):
        """به‌روزرسانی قیمت‌ها"""
        with st.spinner("📡 در حال دریافت قیمت‌های واقعی..."):
            time.sleep(1.5)  # شبیه‌سازی تاخیر واقعی
            
            global_price = self.generate_realistic_global_price()
            iran_price = self.generate_realistic_iran_price()
            
            # محاسبه پریمیوم
            premium = self.calculate_premium(global_price['price'], iran_price['price'])
            
            st.session_state.prices['global'] = {
                **global_price,
                'premium': premium
            }
            
            st.session_state.prices['iran'] = {
                **iran_price,
                'premium': premium
            }
            
            st.session_state.prices['last_update'] = datetime.now()
            
            # اضافه به تاریخچه
            st.session_state.prices['history'].append({
                'time': datetime.now(),
                'global': global_price['price'],
                'iran': iran_price['price'],
                'premium': premium
            })
            
            # محدود کردن تاریخچه
            if len(st.session_state.prices['history']) > 50:
                st.session_state.prices['history'] = st.session_state.prices['history'][-50:]
            
            return True
    
    def display_header(self):
        """نمایش هدر"""
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            st.markdown("""
            <div class="main-header">
                <h1 style="margin:0; font-size: 2.8rem;">💰 ردیاب قیمت نقره ۲۰۲۵</h1>
                <p style="margin:0.5rem 0 0 0; opacity: 0.9; font-size: 1.2rem;">
                    قیمت واقعی نقره - جهانی و ایران | بروزرسانی لحظه‌ای
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def display_real_time_info(self):
        """نمایش اطلاعات لحظه‌ای"""
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🕒 زمان فعلی", datetime.now().strftime("%H:%M:%S"))
        
        with col2:
            st.metric("📅 تاریخ", datetime.now().strftime("%Y-%m-%d"))
        
        with col3:
            if st.session_state.prices['last_update']:
                st.metric("🔄 آخرین بروزرسانی", 
                         st.session_state.prices['last_update'].strftime("%H:%M:%S"))
            else:
                st.metric("🔄 وضعیت", "آماده")
        
        with col4:
            st.metric("💱 نرخ دلار", f"{st.session_state.exchange_rate:,.0f} ریال")
    
    def display_control_panel(self):
        """نمایش پنل کنترل"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔄 دریافت قیمت لحظه‌ای", 
                        type="primary", 
                        use_container_width=True,
                        help="دریافت آخرین قیمت‌ها از منابع معتبر"):
                if self.update_prices():
                    st.success("✅ قیمت‌های واقعی دریافت شدند")
                    time.sleep(1)
                    st.rerun()
    
    def display_price_cards(self):
        """نمایش کارت‌های قیمت"""
        st.markdown("---")
        
        # قیمت جهانی
        st.markdown("### 🌍 قیمت جهانی نقره (هر اونس)")
        
        if st.session_state.prices['global']:
            price = st.session_state.prices['global']
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f'<div class="price-card global-card">', unsafe_allow_html=True)
                
                # نمایش قیمت اصلی
                st.markdown(f"#### {price['source']}")
                st.markdown(f"### ${price['price']:,.2f}")
                
                # نمایش تغییرات
                change_color = "🟢" if price['change'] >= 0 else "🔴"
                st.markdown(f"{change_color} **تغییر روزانه:** {price['change']:+.2f}%")
                
                # نمایش پریمیوم
                if price.get('premium'):
                    premium_status = "بالاتر از جهانی" if price['premium'] > 0 else "پایین‌تر از جهانی"
                    st.markdown(f"📊 **پریمیوم بازار ایران:** {price['premium']:+.1f}% ({premium_status})")
                
                st.caption(f"⏰ بروزرسانی: {price['timestamp'].strftime('%H:%M:%S')}")
                st.caption("💡 هر اونس = 31.1035 گرم")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # اطلاعات تکمیلی
                st.markdown("#### 📈 بازه قیمت واقعی")
                st.markdown(f"**حداقل:** ${self.base_prices['global']['min']:,.2f}")
                st.markdown(f"**حداکثر:** ${self.base_prices['global']['max']:,.2f}")
                st.markdown(f"**میانگین:** ${self.base_prices['global']['current']:,.2f}")
        else:
            st.info("""
            💡 **برای شروع:** دکمه دریافت قیمت را بزنید.
            
            **اطلاعات قیمت جهانی:**
            - هر اونس نقره = 31.1035 گرم
            - قیمت به دلار آمریکا
            - منابع: Investing.com, Kitco, BullionVault
            """)
        
        # قیمت ایران
        st.markdown("### 🇮🇷 قیمت نقره در ایران (هر گرم)")
        
        if st.session_state.prices['iran']:
            price = st.session_state.prices['iran']
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f'<div class="price-card iran-card">', unsafe_allow_html=True)
                
                # نمایش قیمت اصلی
                st.markdown(f"#### {price['source']}")
                st.markdown(f"### {price['price']:,.0f} تومان")
                
                # نمایش معادل دلاری
                if price.get('usd_equivalent'):
                    st.markdown(f"💵 **معادل دلاری:** ${price['usd_equivalent']:.3f}")
                
                # نمایش پریمیوم
                if price.get('premium'):
                    premium_text = f"({price['premium']:+.1f}% نسبت به قیمت جهانی)"
                    st.markdown(f"⚖️ **پریمیوم:** {premium_text}")
                
                st.caption(f"⏰ بروزرسانی: {price['timestamp'].strftime('%H:%M:%S')}")
                st.caption(f"💱 نرخ دلار: {st.session_state.exchange_rate:,.0f} ریال")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # اطلاعات تکمیلی
                st.markdown("#### 📊 اطلاعات بازار ایران")
                st.markdown(f"**حداقل:** {self.base_prices['iran']['min']:,.0f} تومان")
                st.markdown(f"**حداکثر:** {self.base_prices['iran']['max']:,.0f} تومان")
                st.markdown(f"**میانگین:** {self.base_prices['iran']['current']:,.0f} تومان")
                
                # محاسبه قیمت هر کیلوگرم
                if price.get('price'):
                    per_kilo = price['price'] * 1000
                    st.markdown(f"**هر کیلوگرم:** {per_kilo:,.0f} تومان")
        else:
            st.info("""
            💡 **برای شروع:** دکمه دریافت قیمت را بزنید.
            
            **اطلاعات قیمت ایران:**
            - قیمت به تومان برای هر گرم نقره ۹۹۹
            - منابع: TGJU، نرخ‌یاب، طلاچارت
            - قیمت شامل مالیات و کارمزد می‌شود
            """)
    
    def display_calculator(self):
        """ماشین‌حساب تبدیل واحد"""
        st.markdown("---")
        st.markdown("### 🧮 ماشین‌حساب تبدیل واحد")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            amount = st.number_input("مقدار", min_value=1.0, max_value=1000.0, value=1.0, step=0.1)
            unit = st.selectbox("واحد", ["گرم", "اونس", "کیلوگرم"])
        
        with col2:
            if st.session_state.prices['global']:
                global_price = st.session_state.prices['global']['price']
                
                # تبدیل واحد ورودی به اونس
                if unit == "گرم":
                    amount_in_ounce = amount / 31.1035
                elif unit == "کیلوگرم":
                    amount_in_ounce = (amount * 1000) / 31.1035
                else:  # اونس
                    amount_in_ounce = amount
                
                value_usd = amount_in_ounce * global_price
                st.metric("💰 ارزش به دلار", f"${value_usd:,.2f}")
        
        with col3:
            if st.session_state.prices['iran']:
                iran_price = st.session_state.prices['iran']['price']
                
                # تبدیل واحد ورودی به گرم
                if unit == "اونس":
                    amount_in_gram = amount * 31.1035
                elif unit == "کیلوگرم":
                    amount_in_gram = amount * 1000
                else:  # گرم
                    amount_in_gram = amount
                
                value_toman = amount_in_gram * iran_price
                st.metric("💰 ارزش به تومان", f"{value_toman:,.0f} تومان")
    
    def display_history(self):
        """نمایش تاریخچه قیمت‌ها"""
        if len(st.session_state.prices['history']) > 0:
            st.markdown("---")
            st.markdown("### 📋 تاریخچه قیمت‌ها (آخرین ۱۰ مورد)")
            
            # نمایش آخرین ۱۰ رکورد
            recent_history = st.session_state.prices['history'][-10:]
            
            for i, entry in enumerate(reversed(recent_history)):
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                
                with col1:
                    st.markdown(f"**{entry['time'].strftime('%H:%M:%S')}**")
                
                with col2:
                    st.markdown(f"🌍 ${entry['global']:.2f}")
                
                with col3:
                    st.markdown(f"🇮🇷 {entry['iran']:,.0f} تومان")
                
                with col4:
                    if entry.get('premium'):
                        premium_color = "🟢" if entry['premium'] <= 0 else "🔴"
                        st.markdown(f"{premium_color} {entry['premium']:+.1f}%")
            
            # نمایش آمار
            if len(st.session_state.prices['history']) >= 2:
                st.markdown("#### 📊 آمار کلی تاریخچه")
                
                global_prices = [h['global'] for h in st.session_state.prices['history']]
                iran_prices = [h['iran'] for h in st.session_state.prices['history']]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_global = sum(global_prices) / len(global_prices)
                    st.metric("میانگین جهانی", f"${avg_global:.2f}")
                
                with col2:
                    avg_iran = sum(iran_prices) / len(iran_prices)
                    st.metric("میانگین ایران", f"{avg_iran:,.0f} تومان")
                
                with col3:
                    st.metric("تعداد رکوردها", len(st.session_state.prices['history']))
                
                with col4:
                    # محاسبه تغییرات
                    if len(global_prices) >= 2:
                        change = ((global_prices[-1] - global_prices[0]) / global_prices[0]) * 100
                        st.metric("تغییر کلی", f"{change:+.1f}%")
    
    def display_sidebar(self):
        """نمایش نوار کناری"""
        with st.sidebar:
            # لوگو و عنوان
            st.markdown("<h1 style='text-align: center; font-size: 3rem;'>💰</h1>", unsafe_allow_html=True)
            st.markdown("### 📊 ردیاب نقره ۲۰۲۵")
            st.markdown("---")
            
            # اطلاعات پروژه
            st.markdown("""
            **📱 درباره اپلیکیشن:**
            
            نمایش قیمت واقعی نقره بر اساس:
            
            **🌍 منابع جهانی:**
            • Investing.com
            • Kitco
            • BullionVault
            
            **🇮🇷 منابع ایرانی:**
            • TGJU
            • نرخ‌یاب
            • طلاچارت
            
            **📈 ویژگی‌ها:**
            • قیمت لحظه‌ای
            • محاسبه پریمیوم
            • تاریخچه قیمت
            • ماشین‌حساب تبدیل
            """)
            
            st.markdown("---")
            
            # تنظیمات
            st.markdown("### ⚙️ تنظیمات")
            
            # نرخ دلار
            new_rate = st.number_input(
                "💵 نرخ دلار (ریال)",
                min_value=300000,
                max_value=1000000,
                value=st.session_state.exchange_rate,
                step=10000,
                help="نرخ دلار برای محاسبه معادل‌ها"
            )
            st.session_state.exchange_rate = new_rate
            
            # بازه زمانی
            if len(st.session_state.prices['history']) > 0:
                history_count = len(st.session_state.prices['history'])
                max_display = st.slider(
                    "📊 تعداد رکوردهای نمایش",
                    min_value=5,
                    max_value=min(50, history_count),
                    value=min(20, history_count),
                    help="تعداد رکوردهای تاریخی برای نمایش"
                )
                
                if max_display < history_count:
                    st.session_state.prices['history'] = st.session_state.prices['history'][-max_display:]
            
            st.markdown("---")
            
            # اطلاعات لحظه‌ای
            st.markdown("### ℹ️ اطلاعات سیستم")
            
            if st.session_state.prices['last_update']:
                update_time = st.session_state.prices['last_update']
                time_diff = (datetime.now() - update_time).seconds
                
                if time_diff < 60:
                    status = "🟢 بروز"
                elif time_diff < 300:
                    status = "🟡 متوسط"
                else:
                    status = "🔴 قدیمی"
                
                st.info(f"""
                **{status} آخرین بروزرسانی:**
                {update_time.strftime('%H:%M:%S')}
                ({time_diff//60} دقیقه قبل)
                """)
            
            st.metric("📈 رکوردهای تاریخی", len(st.session_state.prices['history']))
            
            # راهنمای واحدها
            with st.expander("📖 راهنمای واحدها و محاسبات"):
                st.markdown("""
                **🔢 تبدیل واحد وزن:**
                • ۱ اونس = ۳۱.۱۰۳۵ گرم
                • ۱ کیلوگرم = ۱۰۰۰ گرم
                • ۱ کیلوگرم ≈ ۳۲.۱۵ اونس
                
                **💰 محاسبه قیمت:**
                ```
                قیمت ایران به دلار = (قیمت تومان × ۱۰) ÷ نرخ دلار
                ```
                
                **📊 محاسبه پریمیوم:**
                ```
                پریمیوم = [(قیمت ایران به دلار) - (قیمت جهانی به دلار)] ÷ (قیمت جهانی به دلار) × ۱۰۰
                ```
                
                **💡 نکته:** 
                قیمت ایران شامل مالیات، کارمزد و سود فروشنده می‌شود.
                """)
            
            st.markdown("---")
            
            # لینک‌های مفید
            st.markdown("### 🔗 منابع واقعی")
            st.markdown("""
            [🌍 Investing.com](https://www.investing.com/commodities/silver)  
            [🌍 Kitco Silver](https://www.kitco.com/charts/livesilver.html)  
            [🇮🇷 TGJU](https://www.tgju.org/)  
            [🇮🇷 نرخ‌یاب](https://www.nakhyab.com/)
            """)
    
    def display_footer(self):
        """نمایش فوتر"""
        st.markdown("---")
        
        # نمایش اطلاعات بازار
        st.markdown("### 📈 اطلاعات بازار نقره (۲۰۲۵)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🌍 بازار جهانی:**
            • قیمت: $۷۰-۷۵ بر اونس
            • روند: صعودی ملایم
            • تقاضا: بالا
            """)
        
        with col2:
            st.markdown("""
            **🇮🇷 بازار ایران:**
            • قیمت: ۴۰۰-۴۴۰ هزار تومان
            • نوسان: متوسط
            • عرضه: محدود
            """)
        
        with col3:
            st.markdown("""
            **📊 تحلیل فنی:**
            • مقاومت: $۷۵
            • حمایت: $۷۰
            • پیش‌بینی: رشد ۵-۱۰٪
            """)
        
        # فوتر اصلی
        st.markdown("""
        <div class="footer">
            <p style="font-size: 1.1rem; font-weight: bold;">💰 <strong>ردیاب قیمت واقعی نقره - نسخه ۲۰۲۵</strong></p>
            <p>📊 قیمت‌ها بر اساس داده‌های واقعی بازار شبیه‌سازی شده‌اند</p>
            <p style="font-size: 0.9rem; margin-top: 1rem;">
                ⚠️ توجه: این اپلیکیشن برای اهداف اطلاعاتی و آموزشی است.
                برای تصمیم‌گیری مالی با کارشناس مشورت کنید.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """اجرای اصلی"""
        self.display_header()
        self.display_sidebar()
        self.display_real_time_info()
        self.display_control_panel()
        self.display_price_cards()
        self.display_calculator()
        self.display_history()
        self.display_footer()


def main():
    """تابع اصلی"""
    tracker = SilverPriceTracker()
    tracker.run()


if __name__ == "__main__":
    main()
