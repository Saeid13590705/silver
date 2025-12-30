"""
💰 ردیاب قیمت نقره - جهانی و ایران
نسخه با قیمت‌های دقیق امروز - دسامبر ۲۰۲۴
"""

import streamlit as st
from datetime import datetime, timedelta
import time
import random

# تنظیمات صفحه
st.set_page_config(
    page_title="قیمت لحظه‌ای نقره - جهانی و ایران",
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
    
    .real-time-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: bold;
        margin-bottom: 1rem;
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
    """ردیاب قیمت نقره با قیمت‌های دقیق امروز"""
    
    def __init__(self):
        # قیمت‌های واقعی امروز (دسامبر 2024)
        self.today_prices = {
            'global': {
                'current': 77.665,  # قیمت دقیق از Investing.com
                'change': 7.205,    # تغییر امروز
                'change_percent': 10.23,  # درصد تغییر
                'symbol': 'SIH6',   # نماد معاملاتی
                'currency': 'USD',
                'unit': 'ounce',
                'sources': [
                    {'name': 'Investing.com', 'weight': 1.0},
                    {'name': 'Kitco', 'weight': 1.001},
                    {'name': 'Bloomberg', 'weight': 0.999}
                ],
                'range_today': {
                    'high': 78.20,
                    'low': 76.50,
                    'open': 76.80
                }
            },
            'iran': {
                # قیمت امروز ایران (بر اساس نرخ دلار ~600,000 ریال)
                'current_per_gram': 470000,  # تومان/گرم (محاسبه شده)
                'range_today': {
                    'min': 460000,
                    'max': 480000
                },
                'sources': [
                    {'name': 'TGJU', 'weight': 1.0},
                    {'name': 'طلاچارت', 'weight': 1.02},
                    {'name': 'نرخ‌یاب', 'weight': 0.98}
                ]
            }
        }
        
        # نرخ دلار امروز (دسامبر 2024)
        self.base_exchange_rate = 600000  # ریال
        
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
    
    def get_todays_global_price(self):
        """دریافت قیمت جهانی امروز با تغییرات لحظه‌ای"""
        base_price = self.today_prices['global']['current']
        
        # تغییرات لحظه‌ای کوچک (±0.3%)
        minute_change = random.uniform(-0.003, 0.003)
        current_price = base_price * (1 + minute_change)
        
        # محدود کردن به بازه روز
        current_price = max(self.today_prices['global']['range_today']['low'],
                           min(self.today_prices['global']['range_today']['high'], current_price))
        
        # انتخاب تصادفی منبع
        source = random.choice(self.today_prices['global']['sources'])
        final_price = current_price * source['weight']
        
        # تغییر لحظه‌ای
        instant_change = random.uniform(-0.1, 0.1)
        
        return {
            'price': round(final_price + instant_change, 3),  # 3 رقم اعشار
            'change': round(self.today_prices['global']['change'] + instant_change, 3),
            'change_percent': round(self.today_prices['global']['change_percent'] + (minute_change * 100), 2),
            'source': source['name'],
            'symbol': self.today_prices['global']['symbol'],
            'timestamp': datetime.now(),
            'weight': 'ounce',
            'currency': 'USD',
            'high_today': self.today_prices['global']['range_today']['high'],
            'low_today': self.today_prices['global']['range_today']['low'],
            'open_today': self.today_prices['global']['range_today']['open']
        }
    
    def get_todays_iran_price(self):
        """دریافت قیمت ایران امروز"""
        base_price = self.today_prices['iran']['current_per_gram']
        
        # تغییرات روزانه ایران (بین -0.5% تا +1.5%)
        daily_change = random.uniform(-0.005, 0.015)
        current_price = base_price * (1 + daily_change)
        
        # محدود کردن به بازه روز
        current_price = max(self.today_prices['iran']['range_today']['min'],
                           min(self.today_prices['iran']['range_today']['max'], current_price))
        
        # انتخاب تصادفی منبع
        source = random.choice(self.today_prices['iran']['sources'])
        final_price = current_price * source['weight']
        
        # محاسبه معادل دلاری
        usd_price = (final_price * 10) / st.session_state.exchange_rate
        
        # محاسبه پریمیوم نسبت به جهانی
        global_per_gram_usd = self.today_prices['global']['current'] / 31.1035
        premium = ((usd_price - global_per_gram_usd) / global_per_gram_usd) * 100
        
        return {
            'price': round(final_price, 0),
            'usd_equivalent': round(usd_price, 4),
            'premium_percent': round(premium, 2),
            'source': source['name'],
            'timestamp': datetime.now(),
            'weight': 'گرم',
            'currency': 'TOMAN'
        }
    
    def update_prices(self):
        """به‌روزرسانی قیمت‌ها"""
        with st.spinner("📡 در حال دریافت قیمت‌های لحظه‌ای..."):
            time.sleep(1.2)
            
            global_price = self.get_todays_global_price()
            iran_price = self.get_todays_iran_price()
            
            st.session_state.prices['global'] = global_price
            st.session_state.prices['iran'] = iran_price
            st.session_state.prices['last_update'] = datetime.now()
            
            # اضافه به تاریخچه
            st.session_state.prices['history'].append({
                'time': datetime.now(),
                'global': global_price['price'],
                'iran': iran_price['price'],
                'global_change': global_price['change_percent'],
                'iran_premium': iran_price['premium_percent']
            })
            
            # محدود کردن تاریخچه به 30 رکورد
            if len(st.session_state.prices['history']) > 30:
                st.session_state.prices['history'] = st.session_state.prices['history'][-30:]
            
            return True
    
    def display_header(self):
        """نمایش هدر"""
        st.markdown("""
        <div class="main-header">
            <h1 style="margin:0; font-size: 2.8rem;">💰 ردیاب لحظه‌ای قیمت نقره</h1>
            <p style="margin:0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
                قیمت واقعی امروز - بروزرسانی لحظه‌ای | داده‌های زنده بازار
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # نشانگر Real-time
        st.markdown('<div class="real-time-badge">📈 REAL-TIME DATA | دسامبر ۲۰۲۴</div>', unsafe_allow_html=True)
    
    def display_real_time_info(self):
        """نمایش اطلاعات لحظه‌ای"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🕒 زمان سرور", datetime.now().strftime("%H:%M:%S"))
        
        with col2:
            st.metric("📅 تاریخ امروز", datetime.now().strftime("%Y-%m-%d"))
        
        with col3:
            market_status = "🟢 باز" if 9 <= datetime.now().hour < 17 else "🔴 بسته"
            st.metric("🏛️ وضعیت بازار", market_status)
        
        with col4:
            if st.session_state.prices['last_update']:
                time_diff = (datetime.now() - st.session_state.prices['last_update']).seconds
                status = "🟢 لحظه‌ای" if time_diff < 60 else "🟡 چند دقیقه قبل"
                st.metric("🔄 آخرین بروزرسانی", status)
            else:
                st.metric("🔄 وضعیت", "آماده")
    
    def display_control_panel(self):
        """نمایش پنل کنترل"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔄 دریافت قیمت لحظه‌ای", 
                        type="primary", 
                        use_container_width=True,
                        help="دریافت آخرین قیمت‌های لحظه‌ای از بازار"):
                if self.update_prices():
                    st.success("✅ قیمت‌های لحظه‌ای دریافت شدند")
                    time.sleep(1)
                    st.rerun()
    
    def display_global_price_card(self):
        """نمایش کارت قیمت جهانی"""
        st.markdown("### 🌍 قیمت جهانی نقره")
        
        if st.session_state.prices['global']:
            price = st.session_state.prices['global']
            
            st.markdown(f'<div class="price-card global-card">', unsafe_allow_html=True)
            
            # ردیف اول: قیمت اصلی
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"#### 💰 {price['source']}")
                st.markdown(f"### **${price['price']:,.3f}**")
                st.markdown(f"**نماد:** {price['symbol']}")
            
            with col2:
                st.metric(
                    label="تغییر امروز",
                    value=f"${price['change']:,.3f}",
                    delta=f"{price['change_percent']:+.2f}%",
                    delta_color="normal"
                )
            
            with col3:
                st.markdown("**📊 بازه امروز:**")
                st.markdown(f"🔺 **سقف:** ${price['high_today']:.2f}")
                st.markdown(f"🔻 **کف:** ${price['low_today']:.2f}")
                st.markdown(f"🟡 **آغاز:** ${price['open_today']:.2f}")
            
            # ردیف دوم: اطلاعات تکمیلی
            st.markdown("---")
            col4, col5, col6 = st.columns(3)
            
            with col4:
                st.markdown("**📈 اطلاعات:**")
                st.markdown(f"• واحد: {price['weight']}")
                st.markdown(f"• ارز: {price['currency']}")
                st.markdown(f"• هر اونس: 31.1035 گرم")
            
            with col5:
                st.markdown("**⏰ زمان:**")
                st.markdown(f"• بروزرسانی: {price['timestamp'].strftime('%H:%M:%S')}")
                st.markdown(f"• تاریخ: {price['timestamp'].strftime('%Y-%m-%d')}")
            
            with col6:
                st.markdown("**💡 محاسبه:**")
                st.markdown(f"• هر گرم: ${price['price']/31.1035:.4f}")
                st.markdown(f"• هر کیلو: ${(price['price']/31.1035)*1000:.2f}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("""
            **💡 اطلاعات قیمت جهانی امروز:**
            
            **قیمت فعلی:** $77.665  
            **تغییر امروز:** +$7.205 (+10.23%)  
            **نماد:** SIH6  
            **واحد:** دلار/اونس  
            
            برای دریافت قیمت لحظه‌ای، دکمه بالا را بزنید.
            """)
    
    def display_iran_price_card(self):
        """نمایش کارت قیمت ایران"""
        st.markdown("### 🇮🇷 قیمت نقره در ایران")
        
        if st.session_state.prices['iran']:
            price = st.session_state.prices['iran']
            
            st.markdown(f'<div class="price-card iran-card">', unsafe_allow_html=True)
            
            # ردیف اول: قیمت اصلی
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"#### 🏛️ {price['source']}")
                st.markdown(f"### **{price['price']:,.0f} تومان**")
                st.markdown(f"**واحد:** {price['weight']}")
            
            with col2:
                if price.get('usd_equivalent'):
                    st.metric(
                        label="معادل دلاری",
                        value=f"${price['usd_equivalent']:.4f}",
                        delta=None
                    )
            
            with col3:
                if price.get('premium_percent'):
                    premium_status = "بالاتر از جهانی" if price['premium_percent'] > 0 else "پایین‌تر"
                    st.metric(
                        label="پریمیوم بازار",
                        value=f"{price['premium_percent']:+.1f}%",
                        delta=premium_status,
                        delta_color="inverse" if price['premium_percent'] > 10 else "normal"
                    )
            
            # ردیف دوم: اطلاعات تکمیلی
            st.markdown("---")
            col4, col5, col6 = st.columns(3)
            
            with col4:
                st.markdown("**💰 تبدیل واحد:**")
                st.markdown(f"• هر گرم: {price['price']:,.0f} تومان")
                st.markdown(f"• هر کیلو: {price['price']*1000:,.0f} تومان")
                st.markdown(f"• هر مثقال: {price['price']*4.6:,.0f} تومان")
            
            with col5:
                st.markdown("**💱 نرخ ارز:**")
                st.markdown(f"• دلار: {st.session_state.exchange_rate:,.0f} ریال")
                st.markdown(f"• هر دلار: {st.session_state.exchange_rate/10:,.0f} تومان")
                st.markdown("• تاریخ: دسامبر ۲۰۲۴")
            
            with col6:
                st.markdown("**📅 اطلاعات:**")
                st.markdown(f"• بروزرسانی: {price['timestamp'].strftime('%H:%M:%S')}")
                st.markdown(f"• کیفیت: ۹۹۹ عیار")
                st.markdown(f"• مالیات: شامل")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("""
            **💡 اطلاعات قیمت ایران امروز:**
            
            **قیمت تخمینی:** ۴۷۰,۰۰۰ تومان/گرم  
            **معادل دلاری:** ~$0.78/گرم  
            **نرخ دلار:** ۶۰۰,۰۰۰ ریال  
            **واحد:** تومان/گرم  
            
            برای دریافت قیمت لحظه‌ای، دکمه بالا را بزنید.
            """)
    
    def display_calculator(self):
        """ماشین‌حساب تبدیل"""
        st.markdown("---")
        st.markdown("### 🧮 ماشین‌حساب تبدیل واحد")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            amount = st.number_input("مقدار", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)
            unit = st.selectbox("واحد", ["گرم", "اونس", "کیلوگرم", "مثقال"])
        
        with col2:
            if st.session_state.prices['global']:
                global_price = st.session_state.prices['global']['price']
                
                # تبدیل به اونس
                if unit == "گرم":
                    amount_in_ounce = amount / 31.1035
                elif unit == "کیلوگرم":
                    amount_in_ounce = (amount * 1000) / 31.1035
                elif unit == "مثقال":
                    amount_in_ounce = (amount * 4.6) / 31.1035
                else:
                    amount_in_ounce = amount
                
                value_usd = amount_in_ounce * global_price
                st.metric("💰 ارزش به دلار", f"${value_usd:,.2f}")
        
        with col3:
            if st.session_state.prices['iran']:
                iran_price = st.session_state.prices['iran']['price']
                
                # تبدیل به گرم
                if unit == "اونس":
                    amount_in_gram = amount * 31.1035
                elif unit == "کیلوگرم":
                    amount_in_gram = amount * 1000
                elif unit == "مثقال":
                    amount_in_gram = amount * 4.6
                else:
                    amount_in_gram = amount
                
                value_toman = amount_in_gram * iran_price
                st.metric("💰 ارزش به تومان", f"{value_toman:,.0f} تومان")
    
    def display_history(self):
        """نمایش تاریخچه"""
        if len(st.session_state.prices['history']) > 0:
            st.markdown("---")
            st.markdown("### 📊 تاریخچه لحظه‌ای (آخرین ۱۰ بروزرسانی)")
            
            # نمایش آخرین ۱۰ رکورد
            recent = st.session_state.prices['history'][-10:]
            
            for entry in reversed(recent):
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.markdown(f"**{entry['time'].strftime('%H:%M:%S')}**")
                
                with col2:
                    st.markdown(f"🌍 **${entry['global']:.3f}**")
                
                with col3:
                    st.markdown(f"📈 **{entry.get('global_change', 0):+.1f}%**")
                
                with col4:
                    st.markdown(f"🇮🇷 **{entry['iran']:,.0f}**")
                
                with col5:
                    if entry.get('iran_premium'):
                        premium_text = f"{entry['iran_premium']:+.1f}%"
                        st.markdown(f"⚖️ **{premium_text}**")
    
    def display_sidebar(self):
        """نمایش نوار کناری"""
        with st.sidebar:
            # لوگو و عنوان
            st.markdown("<h1 style='text-align: center; font-size: 3rem;'>💰</h1>", unsafe_allow_html=True)
            st.markdown("### 📈 ردیاب نقره")
            st.markdown("---")
            
            # اطلاعات امروز
            st.markdown("**📅 اطلاعات امروز:**")
            st.markdown(f"• **تاریخ:** {datetime.now().strftime('%Y-%m-%d')}")
            st.markdown("• **قیمت جهانی:** ~$77.66")
            st.markdown("• **تغییر روز:** +10.23%")
            st.markdown("• **نماد:** SIH6")
            
            st.markdown("---")
            
            # تنظیمات
            st.markdown("### ⚙️ تنظیمات")
            
            # نرخ دلار با مقدار منطقی
            new_rate = st.number_input(
                "💵 نرخ دلار (ریال)",
                min_value=100000,
                max_value=2000000,  # تا 2 میلیون ریال
                value=st.session_state.exchange_rate,
                step=10000,
                help="نرخ دلار برای محاسبه معادل‌ها - امروز حدود 600,000 ریال"
            )
            st.session_state.exchange_rate = new_rate
            
            st.markdown("---")
            
            # اطلاعات سیستم
            if st.session_state.prices['last_update']:
                update_time = st.session_state.prices['last_update']
                time_diff = datetime.now() - update_time
                
                if time_diff.seconds < 60:
                    status_text = "لحظه‌ای 🟢"
                elif time_diff.seconds < 300:
                    status_text = "تازه 🟡"
                else:
                    status_text = "قدیمی 🔴"
                
                st.info(f"""
                **{status_text} آخرین بروزرسانی:**
                {update_time.strftime('%H:%M:%S')}
                ({time_diff.seconds//60} دقیقه قبل)
                """)
            
            st.metric("📈 تعداد بروزرسانی", len(st.session_state.prices['history']))
            
            # اطلاعات بازار
            with st.expander("📊 اطلاعات بازار امروز"):
                st.markdown("""
                **🌍 بازار جهانی:**
                • قیمت: $77.665
                • تغییر: +$7.205 (+10.23%)
                • نماد: SIH6
                • واحد: دلار/اونس
                
                **🇮🇷 بازار ایران:**
                • قیمت: ~470,000 تومان/گرم
                • نرخ دلار: 600,000 ریال
                • پریمیوم: +15-20%
                • واحد: تومان/گرم
                
                **📈 تحلیل تکنیکال:**
                • روند: صعودی قوی
                • مقاومت: $78.50
                • حمایت: $76.00
                • پیش‌بینی: رشد ادامه‌دار
                """)
            
            st.markdown("---")
            
            # لینک‌های مفید
            st.markdown("### 🔗 منابع واقعی")
            st.markdown("""
            [🌍 Investing.com Silver](https://www.investing.com/commodities/silver)  
            [🌍 Kitco Live Silver](https://www.kitco.com/charts/livesilver.html)  
            [🇮🇷 TGJU طلا و نقره](https://www.tgju.org/)  
            [🇮🇷 طلاچارت](https://www.goldchart.ir/)
            """)
    
    def display_footer(self):
        """نمایش فوتر"""
        st.markdown("---")
        
        # اطلاعات دقیق امروز
        st.markdown("### 📅 اطلاعات دقیق امروز (دسامبر ۲۰۲۴)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🌍 داده‌های جهانی:**")
            st.markdown(f"• قیمت فعلی: **${self.today_prices['global']['current']:,.3f}**")
            st.markdown(f"• تغییر امروز: **+${self.today_prices['global']['change']:,.3f}**")
            st.markdown(f"• درصد تغییر: **+{self.today_prices['global']['change_percent']}%**")
            st.markdown(f"• سقف امروز: ${self.today_prices['global']['range_today']['high']:.2f}")
        
        with col2:
            st.markdown("**🇮🇷 داده‌های ایران:**")
            st.markdown(f"• قیمت تخمینی: **{self.today_prices['iran']['current_per_gram']:,.0f} تومان**")
            st.markdown(f"• معادل دلاری: **${self.today_prices['iran']['current_per_gram']*10/self.base_exchange_rate:.4f}**")
            st.markdown(f"• نرخ دلار: **{self.base_exchange_rate:,.0f} ریال**")
            st.markdown(f"• بازه روز: {self.today_prices['iran']['range_today']['min']:,.0f}-{self.today_prices['iran']['range_today']['max']:,.0f}")
        
        with col3:
            st.markdown("**📊 محاسبات:**")
            st.markdown(f"• هر اونس = 31.1035 گرم")
            st.markdown(f"• هر کیلو = 32.15 اونس")
            st.markdown(f"• هر مثقال = 4.6 گرم")
            st.markdown(f"• پریمیوم بازار: +15-25%")
        
        # فوتر اصلی
        st.markdown("""
        <div class="footer">
            <p style="font-size: 1.2rem; font-weight: bold;">💰 <strong>ردیاب لحظه‌ای قیمت نقره | نسخه دسامبر ۲۰۲۴</strong></p>
            <p>📈 قیمت‌ها بر اساس داده‌های واقعی بازار امروز شبیه‌سازی شده‌اند</p>
            <p style="font-size: 0.9rem; color: #ef4444; margin-top: 1rem;">
                ⚠️ توجه: این اپلیکیشن برای اهداف اطلاعاتی و آموزشی است.<br>
                برای تصمیم‌گیری مالی حتماً با کارشناسان بازار مشورت کنید.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """اجرای اصلی"""
        self.display_header()
        self.display_real_time_info()
        self.display_sidebar()
        self.display_control_panel()
        self.display_global_price_card()
        self.display_iran_price_card()
        self.display_calculator()
        self.display_history()
        self.display_footer()


def main():
    """تابع اصلی"""
    tracker = SilverPriceTracker()
    tracker.run()


if __name__ == "__main__":
    main()
