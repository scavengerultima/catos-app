import os
import json
import random
import webbrowser
from datetime import datetime, timedelta
import math
import joblib 
import threading

# --- إعدادات النظام ---
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatIconButton, MDIconButton, MDFloatingActionButton, MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar
from kivy.uix.screenmanager import FadeTransition
from kivy.uix.image import Image
from kivy.core.text import LabelBase
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Line, InstructionGroup, RoundedRectangle, Triangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.utils import get_color_from_hex, platform
from kivy.animation import Animation

# --- مكتبات الذكاء الاصطناعي ---
import arabic_reshaper
from bidi.algorithm import get_display
import numpy as np
import sounddevice as sd
import librosa
import tensorflow as tf

# --- Plyer للإشعارات والمشاركة ---
try:
    from plyer import notification, vibrator
    from plyer.facades import Share
    from plyer import share
except ImportError:
    notification = None; vibrator = None; share = None

# ================= إعدادات التطبيق =================
Window.size = (360, 800)
SAMPLE_RATE = 22050
DURATION = 1.5 
PAYMENT_LINK = "https://paypal.me/DrAliKhalid"
AI_MODEL_PATH = "cat_brain.pkl"

# ================= 🔧 الخطوط =================
font_path = "font.ttf" 
if not os.path.exists(font_path):
    font_path = "C:/Windows/Fonts/arial.ttf"
LabelBase.register(name="GlobalFont", fn_regular=font_path, fn_bold=font_path)

# ================= 1. محرك التعريب =================
def fix_text(text):
    if not text: return ""
    try: return get_display(arabic_reshaper.reshape(text))
    except: return text

# ================= 2. البيانات الثابتة =================
VACCINE_SCHEDULE = [
    {"id": "v1", "week": 8, "name_en": "FVRCP (1)", "name_ar": "لقاح الثلاثي - جرعة 1"},
    {"id": "v2", "week": 12, "name_en": "FVRCP (2)", "name_ar": "لقاح الثلاثي - جرعة 2"},
    {"id": "v3", "week": 12, "name_en": "Rabies", "name_ar": "لقاح السعار"},
    {"id": "v4", "week": 16, "name_en": "FVRCP (3)", "name_ar": "لقاح الثلاثي - جرعة 3"},
    {"id": "v5", "week": 52, "name_en": "Booster", "name_ar": "الجرعة السنوية الشاملة"}
]

TRANS = {
    "EN": {
        "welcome": "WELCOME TO CAT OS", "select_lang": "Select Language", "ready": "SYSTEM READY",
        "tip_title": "TIP OF THE DAY", "cal_title": "Daily Calories", "edit_cal": "Edit",
        "vac_title": "VACCINE SCHEDULE", "profile": "Bio-Profile", "translator": "Translator",
        "care": "Care", "store": "Store", "name": "Cat Name", "age": "Age (Years)",
        "weight": "Weight (kg)", "save": "SAVE CHANGES", "growth": "Growth Phase",
        "over": "Overweight", "healthy": "Healthy", "premium_title": "PREMIUM SOUNDS",
        "buy": "UNLOCK ALL ($4.99)", "due": "Due:", "taken": "Status: Taken",
        "pending": "Status: Pending", 
        "s_mate": "Mating Call", "s_mom": "Mother Trill", "s_sleep": "Sleepy Purr",
        "s_repel": "Anti-Scratch", "s_angry": "Alpha Warning",
        "s_bird": "Bird Chirp", "s_mouse": "Mouse Squeak", "s_heart": "Mom's Heartbeat",
        "come": "Come", "love": "Love", "stop": "Stop", "saved_msg": "Saved Successfully!",
        "choose_avatar": "Choose Avatar",
        "hungry": "I am hungry! Feed me 🍖",
        "angry": "I am angry! Back off 😡",
        "happy": "I am happy and purring 😻",
        "pain": "I am in pain 😿",
        "hunting": "I see a prey! 🐦",
        "history_title": "Translation History",
        "clear_hist": "Clear All",
        "no_hist": "No records yet.",
        "test_notif": "Test Notification",
        "notif_sent": "Notification Sent!",
        "img_saved": "Image Saved! Opening folder..."
    },
    "AR": {
        "welcome": "أهلاً بك في نظام القطط", "select_lang": "اختر اللغة", "ready": "النظام جاهز",
        "tip_title": "نصيحة اليوم", "cal_title": "السعرات اليومية", "edit_cal": "تعديل",
        "vac_title": "جدول اللقاحات", "profile": "الملف الشخصي", "translator": "المترجم",
        "care": "العناية", "store": "المتجر", "name": "اسم القط", "age": "العمر (سنوات)",
        "weight": "الوزن (كجم)", "save": "حفظ التغييرات", "growth": "مرحلة نمو",
        "over": "وزن زائد", "healthy": "وزن صحي", "premium_title": "أصوات احترافية (مدفوعة)",
        "buy": "فتح الكل (4.99$)", "due": "التاريخ:", "taken": "الحالة: تم التطعيم",
        "pending": "الحالة: لم يؤخذ", 
        "s_mate": "نداء التزاوج", "s_mom": "نداء الأم", "s_sleep": "خرخرة النوم",
        "s_repel": "الرادع (فوق صوتي)", "s_angry": "تحذير الألفا",
        "s_bird": "زقزقة العصافير", "s_mouse": "صوت الفأر",
        "s_heart": "نبضات قلب الأم",
        "come": "تعال", "love": "أحبك", "stop": "توقف", "saved_msg": "تم الحفظ بنجاح!",
        "choose_avatar": "اختر صورة شخصية",
        "hungry": "أنا جائع! أطعمني 🍖",
        "angry": "أنا غاضب! ابتعد 😡",
        "happy": "أنا سعيد وأخرخر 😻",
        "pain": "أشعر بالألم 😿",
        "hunting": "رأيت فريسة! 🐦",
        "history_title": "سجل الترجمات",
        "clear_hist": "مسح الكل",
        "no_hist": "لا يوجد سجل بعد.",
        "test_notif": "تجربة الإشعار",
        "notif_sent": "تم إرسال الإشعار!",
        "img_saved": "تم حفظ الصورة! جاري فتح المجلد..."
    }
}

# ================= 3. العقل المدبر =================
class DataManager:
    def __init__(self):
        self.file = "cat_master_db.json"
        self.lang = "EN" 
        self.data = {
            "name": "Cat", "age": 0.2, "weight": 1.5, "manual_cals": 0, "premium": False,
            "vaccine_status": {},
            "profile_pic": "cat_avatar_1.png",
            "history": [] 
        }
        # --- القائمة الكاملة للنصائح (50 نصيحة) ---
        self.tips_db = {
            "EN": [
                "Cats need Taurine for heart health.", "Clean litter box daily.", "Brush long-haired cats weekly.",
                "Chocolate is toxic to cats.", "Lilies are deadly to cats.", "Keep cats indoors for safety.",
                "Spaying prevents health issues.", "Microchip your cat.", "Check teeth for tartar.",
                "Cats sleep 12-16 hours a day.", "Don't give cow milk (Lactose).", "Use ceramic or metal bowls.",
                "Provide a scratching post.", "Play 15 mins daily.", "Cats hide pain well.",
                "Vaccinate annually.", "Treat for fleas monthly.", "Wet food provides hydration.",
                "Clean water bowl daily.", "Cats prefer running water.", "Don't declaw, trim nails instead.",
                "Rotate toys to prevent boredom.", "Cats need vertical space.", "Avoid essential oils.",
                "Monitor weight changes.", "Senior cats need checkups.", "Hairballs are normal occasionally.",
                "Use enzymatic cleaner for accidents.", "Slow blinks mean love.", "Never punish, use redirection.",
                "Grapes and raisins are toxic.", "Onions and garlic cause anemia.", "Kittens need specific food.",
                "Adult cats eat 2 times a day.", "Check ears for mites.", "Keep chemicals away.",
                "Cats can get sunburned.", "Socialize kittens early.", "Respect their personal space.",
                "Tail up means happy.", "Hissing means fear.", "Purring heals bones.",
                "Kneading is a comfort behavior.", "Cats are crepuscular (active at dawn).", "Avoid string toys unsupervised.",
                "Check paw pads for cuts.", "Deworming is essential.", "Rabies vaccine is mandatory.",
                "FVRCP protects against flu.", "Love your cat unconditionally."
            ],
            "AR": [
                "تحتاج القطط للتورين لصحة القلب.", "نظف صندوق الرمل يومياً.", "مشط شعر القطة أسبوعياً.",
                "الشوكولاتة سامة جداً للقطط.", "زهرة الزنبق قاتلة للقطط.", "ابقِ القطة بالمنزل لسلامتها.",
                "التعقيم يمنع أمراضاً خطيرة.", "الشريحة الإلكترونية ضرورية.", "افحص الأسنان بحثاً عن الجير.",
                "تنام القطط 12-16 ساعة يومياً.", "تجنب الحليب البقري (عسر هضم).", "استخدم أطباق سيراميك أو معدن.",
                "وفر عمود خدش لحماية الأثاث.", "العب معها 15 دقيقة يومياً.", "القطط تخفي ألمها ببراعة.",
                "التطعيم السنوي ضروري.", "عالج البراغيث شهرياً.", "الطعام الرطب يوفر السوائل.",
                "غير الماء يومياً.", "القطط تفضل الماء الجاري.", "لا تخلع المخالب، قصها فقط.",
                "بدّل الألعاب لمنع الملل.", "القطط تحب الأماكن المرتفعة.", "تجنب الزيوت العطرية القوية.",
                "راقب أي تغير في الوزن.", "القطط المسنة تحتاج فحص دوري.", "كرات الشعر طبيعية أحياناً.",
                "استخدم منظف إنزيمي للفضلات.", "الرمش ببطء يعني الحب.", "لا تعاقب، بل وجه سلوكها.",
                "العنب والزبيب سام للكلى.", "البصل والثوم يسبب فقر دم.", "القطط الصغيرة تحتاج طعاماً خاصاً.",
                "القطط البالغة تأكل مرتين يومياً.", "افحص الأذن من العث.", "أبعد المواد الكيميائية.",
                "القطط قد تصاب بحروق شمس.", "عود القطة على الناس مبكراً.", "احترم مساحتها الخاصة.",
                "الذيل المرفوع يعني السعادة.", "الفحيح يعني الخوف.", "الخرخرة تساعد في التئام العظام.",
                "حركة العجن تدل على الراحة.", "القطط تنشط فجراً وغروباً.", "لا تترك الخيوط دون مراقبة.",
                "افحص باطن الكف للجروح.", "علاج الديدان ضروري.", "لقاح السعار إلزامي.",
                "لقاح الثلاثي يحمي من الإنفلونزا.", "أحب قطتك بلا شروط."
            ]
        }
        self.load()

    def load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, 'r', encoding='utf-8') as f: self.data.update(json.load(f))
            except: pass

    def save(self):
        try:
            with open(self.file, 'w', encoding='utf-8') as f: 
                json.dump(self.data, f)
            if vibrator:
                try: vibrator.vibrate(0.05)
                except: pass
        except: pass
    
    def add_history(self, text, icon="cat"):
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        self.data["history"].insert(0, {"text": text, "time": timestamp, "icon": icon})
        if len(self.data["history"]) > 50:
            self.data["history"] = self.data["history"][:50]
        self.save()

    def clear_history(self):
        self.data["history"] = []
        self.save()

    def get_text(self, key): return fix_text(TRANS[self.lang].get(key, key))
    def get_tip(self): return fix_text(random.choice(self.tips_db[self.lang]))

    def calculate_stats(self):
        if self.data.get('manual_cals', 0) > 0:
            return self.data['manual_cals'], fix_text("هدف يدوي") if self.lang == "AR" else "Manual Goal", "00aaff"
        rer = 70 * (self.data['weight'] ** 0.75)
        factor = 1.2; status = self.get_text("healthy"); color = "00ffaa"
        return int(rer * factor), status, color

    def get_vaccine_timeline(self):
        days_old = self.data['age'] * 365
        birth_date = datetime.now() - timedelta(days=days_old)
        timeline = []
        for vac in VACCINE_SCHEDULE:
            vid = vac['id']; due_date = birth_date + timedelta(weeks=vac['week'])
            formatted_date = due_date.strftime("%Y-%m-%d")
            is_taken = self.data['vaccine_status'].get(vid, False)
            if is_taken: status_text = "taken"; icon = "check-circle"; color = "00e676"
            else: status_text = "pending"; icon = "needle"; color = "ff5252"
            name = vac['name_ar'] if self.lang == "AR" else vac['name_en']
            timeline.append({"id": vid, "name": fix_text(name), "date": formatted_date, "status_text": self.get_text(status_text), "icon": icon, "color": color, "is_taken": is_taken})
        return timeline

    def toggle_vaccine(self, vid):
        self.data['vaccine_status'][vid] = not self.data['vaccine_status'].get(vid, False); self.save()

    def check_and_notify(self):
        if not notification: return 
        timeline = self.get_vaccine_timeline()
        today = datetime.now().strftime("%Y-%m-%d")
        for vac in timeline:
            if vac['date'] == today and not vac['is_taken']:
                msg_title = "تذكير تطعيم!" if self.lang == "AR" else "Vaccine Reminder!"
                msg_body = f"{vac['name']} " + ("موعده اليوم" if self.lang == "AR" else "is due today!")
                try: notification.notify(title=msg_title, message=msg_body, app_name="Cat OS", timeout=10)
                except: pass

db = DataManager()

# ================= 4. المساعدات (تحكم كامل بالصوت) =================
class RealPlayer:
    def __init__(self): self.current = None
    
    def play(self, f):
        # 🛑 إيقاف أي صوت سابق فوراً
        self.stop()
        
        if os.path.exists(f):
            try:
                self.current = SoundLoader.load(f)
                self.current.play()
                return True
            except: pass
        return False

    def stop(self):
        # 🛑 دالة الإيقاف الصارمة
        if self.current:
            try:
                self.current.stop()
                self.current = None
            except: pass

# --- ويدجت الموجات الصوتية ---
class DynamicWaveform(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.waves_config = [("#FF6D00", 2.0, 15), ("#00C853", 1.5, 10), ("#2962FF", 1.0, 20)]
        self.phase = 0; self.current_volume = 0
        self.bind(size=self.update_canvas, pos=self.update_canvas)
        Clock.schedule_interval(self.animate, 1/60)

    def update_volume(self, volume):
        target_volume = volume * 150
        self.current_volume = self.current_volume * 0.8 + target_volume * 0.2

    def animate(self, dt): self.phase += dt; self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear(); ig = InstructionGroup()
        mid_y = self.y + 100 
        points_count = 150; step_x = self.width / points_count
        
        for color_hex, speed, base_amp in self.waves_config:
            c = get_color_from_hex(color_hex); ig.add(Color(c[0], c[1], c[2], 0.6))
            points = []
            for i in range(points_count + 2):
                x = self.x + i * step_x
                normalized_x = (i / points_count) * math.pi * 4
                dynamic_amp = base_amp + self.current_volume * (1 + speed/2)
                y = mid_y + math.sin(normalized_x + self.phase * speed) * dynamic_amp
                points.extend([x, y])
            ig.add(Line(points=points, width=2))
        self.canvas.add(ig)

class ClickableCard(MDCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_behavior = True 

class ModernCard(MDCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = [20]; self.elevation = 3; self.padding = "15dp"
        self.md_bg_color = get_color_from_hex("#2A2A35")

# --- ويدجت الفقاعة البيضاء النقية ---
class SpeechBubbleWidget(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
        self.lbl_text = MDLabel(
            text="",
            halign="center",
            valign="middle",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1), # أسود
            font_name="GlobalFont",
            font_style="H5",
            bold=True,
            pos_hint={"center_x": .5, "center_y": .5}
        )
        self.add_widget(self.lbl_text)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1) # أبيض 100%
            RoundedRectangle(pos=self.pos, size=self.size, radius=[25])
            Triangle(points=[
                self.center_x - 10, self.y, 
                self.center_x + 10, self.y, 
                self.center_x, self.y - 15
            ])

class TranslationResult(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = "300dp" 
        
        self.cat_img = Image(
            source=db.data.get("profile_pic", "cat_avatar_1.png"),
            size_hint=(None, None),
            size=("200dp", "200dp"), 
            pos_hint={"center_x": 0.5, "center_y": 0.4}
        )
        self.add_widget(self.cat_img)

        self.bubble = SpeechBubbleWidget(
            size_hint=(None, None),
            size=("280dp", "90dp"),
            pos_hint={"center_x": 0.5, "top": 1}
        )
        self.add_widget(self.bubble)
    
    def show_result(self, text):
        current_pic = db.data.get("profile_pic", "cat_avatar_1.png")
        if os.path.exists(current_pic): self.cat_img.source = current_pic
        self.bubble.lbl_text.text = text
        self.bubble.opacity = 0
        anim = Animation(opacity=1, d=0.2)
        anim.start(self.bubble)
    
    def hide(self):
        self.bubble.opacity = 0

# ================= 5. الشاشات =================

class LanguageScreen(MDScreen):
    def build_ui(self):
        self.md_bg_color = get_color_from_hex("#121212")
        layout = MDBoxLayout(orientation='vertical', padding=40, spacing=30, pos_hint={"center_x": .5, "center_y": .5})
        logo = Image(source="logo.png", size_hint=(None, None), size=("300dp", "300dp"), pos_hint={"center_x": .5}) if os.path.exists("logo.png") else MDIconButton(icon="cat", icon_size="150sp", theme_text_color="Custom", text_color=get_color_from_hex("#FF9100"), pos_hint={"center_x": .5})
        layout.add_widget(logo)
        layout.add_widget(MDLabel(text="CAT OS X", halign="center", font_style="H3", theme_text_color="Custom", text_color=(1,1,1,1), font_name="GlobalFont", bold=True))
        btn_en = MDFillRoundFlatIconButton(text="ENGLISH", icon="web", size_hint_x=1, md_bg_color=get_color_from_hex("#FF6D00"), font_name="GlobalFont")
        btn_en.bind(on_release=lambda x: self.set_lang("EN"))
        btn_ar = MDFillRoundFlatIconButton(text=fix_text("العربية"), icon="abjad-arabic", size_hint_x=1, md_bg_color=get_color_from_hex("#00C853"), font_name="GlobalFont")
        btn_ar.bind(on_release=lambda x: self.set_lang("AR"))
        layout.add_widget(MDBoxLayout(size_hint_y=0.1)); layout.add_widget(btn_en); layout.add_widget(btn_ar)
        self.add_widget(layout)
    def on_enter(self):
        if not self.children: self.build_ui()
    def set_lang(self, lang): db.lang = lang; self.manager.current = "main_app"

class MainAppScreen(MDScreen):
    def on_enter(self): self.clear_widgets(); self.build_ui()
    def build_ui(self):
        nav = MDBottomNavigation(selected_color_background=get_color_from_hex("#1f1f2e"), text_color_active=get_color_from_hex("#FF9100"))
        s1 = MDBottomNavigationItem(name='trans', text=db.get_text("translator"), icon='waveform'); s1.add_widget(SubScreenTranslator())
        s2 = MDBottomNavigationItem(name='care', text=db.get_text("care"), icon='heart-pulse'); s2.add_widget(SubScreenCare())
        s3 = MDBottomNavigationItem(name='store', text=db.get_text("store"), icon='cart'); s3.add_widget(SubScreenStore())
        s4 = MDBottomNavigationItem(name='profile', text=db.get_text("profile"), icon='account-circle'); s4.add_widget(SubScreenProfile())
        nav.add_widget(s1); nav.add_widget(s2); nav.add_widget(s3); nav.add_widget(s4)
        self.add_widget(nav)

# --- 🔥 شاشة المترجم (كاملة الميزات) 🔥 ---
class SubScreenTranslator(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = RealPlayer()
        self.listening = False
        self.model = None
        self.last_premium_state = db.data.get('premium', False)
        self.grid = None
        
        threading.Thread(target=self.preload_ai).start()
        Clock.schedule_interval(self.check_premium_change, 1)
        
        self.build_ui()
    
    def preload_ai(self):
        if os.path.exists(AI_MODEL_PATH):
            try:
                self.model = joblib.load(AI_MODEL_PATH)
                dummy = np.zeros((1, 40)); self.model.predict(dummy) 
            except: pass

    def check_premium_change(self, dt):
        current_state = db.data.get('premium', False)
        if current_state != self.last_premium_state:
            self.last_premium_state = current_state
            self.refresh_buttons()

    def refresh_buttons(self):
        if not self.grid: return
        self.grid.clear_widgets()
        
        # --- الأزرار ---
        sound_buttons = [(db.get_text("come"), "call.mp3", "#00C853"), (db.get_text("love"), "love.mp3", "#2962FF"), (db.get_text("stop"), "STOP_COMMAND", "#D50000")]
        
        if db.data.get('premium'):
            premium_sounds = [("s_mate", "mating.mp3", "#FF9100"), ("s_mom", "mom.mp3", "#FF9100"), ("s_sleep", "sleep.mp3", "#FF9100"), ("s_repel", "repel.mp3", "#555555"), ("s_angry", "angry.mp3", "#D50000"), ("s_bird", "bird.mp3", "#00B0FF"), ("s_mouse", "mouse.mp3", "#9E9E9E"), ("s_heart", "heartbeat.mp3", "#F50057")]
            for k, f, c in premium_sounds: sound_buttons.append((db.get_text(k), f, c))

        for txt, f, col in sound_buttons:
            b = MDFillRoundFlatIconButton(
                text=txt, 
                icon="play" if f != "STOP_COMMAND" else "stop", 
                md_bg_color=get_color_from_hex(col), 
                font_name="GlobalFont", 
                font_size="13sp", 
                size_hint_x=1 
            )
            # 🛑 ربط الزر بآلية التوقف
            if f == "STOP_COMMAND":
                b.bind(on_release=lambda x: self.player.stop())
            else:
                b.bind(on_release=lambda x, file=f: self.player.play(file))
            
            self.grid.add_widget(b)

    def build_ui(self):
        # 1. الخلفية
        self.waveform = DynamicWaveform()
        self.add_widget(self.waveform)

        # 2. المحتوى الرئيسي
        main_layout = MDBoxLayout(orientation='vertical', padding=[0, 10, 0, 10])
        self.add_widget(main_layout)

        # أ. المنطقة العليا
        self.result_widget = TranslationResult(size_hint_y=0.4)
        main_layout.add_widget(self.result_widget)

        # ب. أزرار الأدوات
        self.btn_history = MDIconButton(
            icon="history",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#FFFFFF"),
            pos_hint={"right": 0.95, "top": 0.95},
            icon_size="32sp"
        )
        self.btn_history.bind(on_release=self.show_history_dialog)
        self.add_widget(self.btn_history) 

        self.btn_share = MDIconButton(
            icon="share-variant",
            theme_text_color="Custom",
            text_color=get_color_from_hex("#FFFFFF"),
            pos_hint={"x": 0.05, "top": 0.95},
            icon_size="32sp"
        )
        self.btn_share.bind(on_release=self.share_result)
        self.add_widget(self.btn_share)

        # ج. المنطقة الوسطى
        middle_box = MDBoxLayout(orientation='vertical', size_hint_y=0.4, padding=[20, 0, 20, 0])
        self.lbl_status = MDLabel(text=db.get_text("ready"), halign="center", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1), font_name="GlobalFont", size_hint_y=None, height="30dp")
        middle_box.add_widget(self.lbl_status)

        scroll_view = MDScrollView(bar_width=0) 
        self.grid = MDGridLayout(cols=3, spacing=10, adaptive_height=True, padding=[0, 10])
        scroll_view.add_widget(self.grid)
        middle_box.add_widget(scroll_view)
        
        main_layout.add_widget(middle_box)
        
        self.refresh_buttons()
        
        # د. المنطقة السفلية
        mic_box = MDFloatLayout(size_hint_y=0.2)
        self.btn_mic = MDFloatingActionButton(icon="microphone", md_bg_color=get_color_from_hex("#FF6D00"), pos_hint={"center_x": .5, "center_y": .5}, elevation=5, type="large")
        self.btn_mic.bind(on_release=self.toggle)
        mic_box.add_widget(self.btn_mic)
        main_layout.add_widget(mic_box)

    def toggle(self, inst):
        # 🛑 إيقاف أي صوت عند ضغط الميكروفون
        self.player.stop()

        if not self.listening:
            self.listening = True; inst.md_bg_color = (1,0,0,1); inst.icon = "stop"; 
            self.result_widget.hide()
            self.lbl_status.text = fix_text("...جاري الاستماع...") if db.lang == "AR" else "LISTENING..."
            threading.Thread(target=self.process_audio_thread).start()
        else:
            self.listening = False; inst.md_bg_color = get_color_from_hex("#FF6D00"); inst.icon = "microphone"; 
            self.lbl_status.text = db.get_text("ready"); self.waveform.update_volume(0)

    def process_audio_thread(self):
        try:
            myrecording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, blocking=True).flatten()
            mfccs = librosa.feature.mfcc(y=myrecording, sr=SAMPLE_RATE, n_mfcc=40)
            mfccs_processed = np.mean(mfccs.T, axis=0).reshape(1, -1)
            
            result_key = "unknown"
            if self.model:
                prediction = self.model.predict(mfccs_processed)
                result_key = prediction[0]
            else:
                rms = np.sqrt(np.mean(myrecording**2))
                Clock.schedule_once(lambda dt: self.waveform.update_volume(rms))
                if rms > 0.03: result_key = "angry"
                elif rms > 0.01: result_key = "hungry"
                else: result_key = "happy"
            
            Clock.schedule_once(lambda dt: self.show_result_on_main_thread(result_key))

        except Exception as e:
            print(f"Analysis Error: {e}")
            Clock.schedule_once(lambda dt: setattr(self.lbl_status, 'text', "Error"))
        
        Clock.schedule_once(lambda dt: self.reset_button_ui())

    def show_result_on_main_thread(self, result_key):
        if result_key in TRANS["EN"]:
            translated_text = db.get_text(result_key)
            self.result_widget.show_result(translated_text)
            db.add_history(translated_text)
        else:
            self.result_widget.show_result(db.get_text("happy")) 

    def reset_button_ui(self):
        self.listening = False
        self.btn_mic.md_bg_color = get_color_from_hex("#FF6D00")
        self.btn_mic.icon = "microphone"
        self.lbl_status.text = db.get_text("ready")

    def share_result(self, inst):
        file_name = f"cat_os_share_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        self.result_widget.export_to_png(file_name)
        if platform == 'android':
            try: share.share(file_path=os.path.abspath(file_name))
            except: App.get_running_app().show_toast("Android Share failed")
        else:
            App.get_running_app().show_toast(f"{db.get_text('img_saved')}")
            try: os.startfile(os.getcwd())
            except: pass

    def show_history_dialog(self, inst):
        content = MDBoxLayout(orientation="vertical", spacing="10dp", size_hint_y=None, height="300dp")
        title_label = MDLabel(text=db.get_text("history_title"), font_name="GlobalFont", font_style="H6", theme_text_color="Custom", text_color=(1, 1, 1, 1), size_hint_y=None, height="40dp", halign="center")
        content.add_widget(title_label)
        history_list = MDList()
        if not db.data.get('history'):
            history_list.add_widget(TwoLineAvatarIconListItem(text=db.get_text("no_hist"), secondary_text="...", _no_ripple_effect=True))
        else:
            for item in db.data['history']:
                li = TwoLineAvatarIconListItem(text=item['text'], secondary_text=item['time'], font_style="Body1")
                li.add_widget(IconLeftWidget(icon="cat"))
                history_list.add_widget(li)
        scroll = MDScrollView(); scroll.add_widget(history_list); content.add_widget(scroll)
        btn_clear = MDFlatButton(text=db.get_text("clear_hist"), theme_text_color="Custom", text_color=(1, 0, 0, 1), font_name="GlobalFont")
        btn_clear.bind(on_release=lambda x: [db.clear_history(), self.dialog.dismiss()])
        self.dialog = MDDialog(title="", type="custom", content_cls=content, buttons=[btn_clear])
        self.dialog.open()

# ... (SubScreenCare, SubScreenStore, SubScreenProfile, CatOSApp are same) ...
class SubScreenCare(MDFloatLayout):
    def __init__(self, **kwargs): super().__init__(**kwargs); self.build_ui()
    def build_ui(self):
        self.clear_widgets()
        scroll = MDScrollView(); layout = MDGridLayout(cols=1, padding=20, spacing=20, size_hint_y=None); layout.bind(minimum_height=layout.setter('height'))
        tip_card = ModernCard(size_hint_y=None, height="160dp", md_bg_color=get_color_from_hex("#37474F"))
        tip_box = MDBoxLayout(orientation='vertical')
        header = MDBoxLayout(size_hint_y=None, height="40dp")
        header.add_widget(MDLabel(text=db.get_text("tip_title"), bold=True, theme_text_color="Custom", text_color=(1,0.7,0,1), font_name="GlobalFont"))
        btn_ref = MDIconButton(icon="refresh", theme_text_color="Custom", text_color=(1,1,1,1)); btn_ref.bind(on_release=lambda x: self.refresh_tip())
        header.add_widget(btn_ref)
        self.lbl_tip = MDLabel(text=db.get_tip(), theme_text_color="Custom", text_color=(1,1,1,0.9), font_style="Body1", font_name="GlobalFont")
        tip_box.add_widget(header); tip_box.add_widget(self.lbl_tip); tip_card.add_widget(tip_box)
        nutri_card = ModernCard(size_hint_y=None, height="160dp", md_bg_color=get_color_from_hex("#263238"))
        cals, status, col = db.calculate_stats()
        n_box = MDBoxLayout(orientation='vertical', spacing=5)
        n_box.add_widget(MDLabel(text=f"{cals} kcal", halign="center", font_style="H3", theme_text_color="Custom", text_color=get_color_from_hex(col), font_name="GlobalFont"))
        n_box.add_widget(MDLabel(text=status, halign="center", theme_text_color="Custom", text_color=(0.7,0.7,0.7,1), font_name="GlobalFont", font_style="Caption"))
        btn_edit_cal = MDRaisedButton(text=db.get_text("edit_cal"), md_bg_color=get_color_from_hex("#455A64"), font_name="GlobalFont", pos_hint={"center_x": .5})
        btn_edit_cal.bind(on_release=self.open_cal_dialog)
        n_box.add_widget(btn_edit_cal)
        nutri_card.add_widget(n_box)
        vac_label = MDLabel(text=db.get_text("vac_title"), size_hint_y=None, height="40dp", font_name="GlobalFont", font_style="H6", theme_text_color="Custom", text_color=(1,1,1,1))
        
        # --- زر اختبار الإشعارات ---
        btn_test_notif = MDIconButton(icon="bell-ring", theme_text_color="Custom", text_color=(1, 0.7, 0, 1), pos_hint={"right": 1})
        btn_test_notif.bind(on_release=self.trigger_test_notification)
        
        vac_header_box = MDBoxLayout(size_hint_y=None, height="40dp")
        vac_header_box.add_widget(vac_label)
        vac_header_box.add_widget(btn_test_notif)

        layout.add_widget(tip_card); layout.add_widget(nutri_card); layout.add_widget(vac_header_box)
        timeline = db.get_vaccine_timeline()
        for vac in timeline:
            item = ThreeLineAvatarIconListItem(text=vac['name'], secondary_text=f"{db.get_text('due')} {vac['date']}", tertiary_text=vac['status_text'], font_style="Body1", _no_ripple_effect=True)
            item.add_widget(IconLeftWidget(icon="calendar-clock", theme_text_color="Custom", text_color=(1,1,1,0.5)))
            action_btn = IconRightWidget(icon=vac['icon'], theme_text_color="Custom", text_color=get_color_from_hex(vac['color']))
            action_btn.bind(on_release=lambda x, vid=vac['id']: self.toggle_vaccine(vid))
            item.add_widget(action_btn); layout.add_widget(item)
        scroll.add_widget(layout); self.add_widget(scroll)
    
    def trigger_test_notification(self, inst):
        if notification:
            try:
                notification.notify(
                    title=fix_text(db.get_text("test_notif")),
                    message=fix_text(db.get_text("notif_sent")),
                    app_name="Cat OS",
                    timeout=5
                )
                App.get_running_app().show_toast("Check your notifications!")
            except Exception as e:
                App.get_running_app().show_toast(f"Error: {e}")
        else:
            App.get_running_app().show_toast("Plyer not supported/installed.")

    def refresh_tip(self): self.lbl_tip.text = db.get_tip()
    def toggle_vaccine(self, vid): db.toggle_vaccine(vid); self.build_ui(); App.get_running_app().show_toast(db.get_text("saved_msg"))
    def open_cal_dialog(self, x):
        self.tf_custom_cal = MDTextField(hint_text="Enter Calories")
        self.dialog = MDDialog(title=fix_text("Set Manual Goal"), type="custom", content_cls=self.tf_custom_cal, buttons=[MDFlatButton(text="AUTO", on_release=self.reset_cal), MDFlatButton(text="SAVE", on_release=self.save_cal)])
        self.dialog.open()
    def save_cal(self, x):
        try: db.data['manual_cals'] = int(self.tf_custom_cal.text); db.save(); self.dialog.dismiss(); self.build_ui()
        except: pass
    def reset_cal(self, x): db.data['manual_cals'] = 0; db.save(); self.dialog.dismiss(); self.build_ui()

class SubScreenStore(MDFloatLayout):
    def __init__(self, **kwargs): super().__init__(**kwargs); self.player = RealPlayer(); self.build_ui()
    def build_ui(self):
        scroll = MDScrollView(); layout = MDGridLayout(cols=1, padding=20, spacing=20, size_hint_y=None); layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(MDLabel(text=db.get_text("premium_title"), font_style="H5", theme_text_color="Custom", text_color=(1,0.8,0,1), font_name="GlobalFont"))
        products = [("s_mate", "mating.mp3", "cat"), ("s_mom", "mom.mp3", "heart"), ("s_sleep", "sleep.mp3", "sleep"), ("s_repel", "repel.mp3", "access-point-network-off"), ("s_angry", "angry.mp3", "alert-decagram"), ("s_bird", "bird.mp3", "twitter"), ("s_mouse", "mouse.mp3", "rodent"), ("s_heart", "heartbeat.mp3", "heart-pulse")]
        for key, file, icon in products:
            card = ModernCard(size_hint_y=None, height="80dp", padding="10dp")
            row = MDBoxLayout(orientation='horizontal', spacing=10)
            row.add_widget(MDIconButton(icon=icon, theme_text_color="Custom", text_color=(1,1,1,1)))
            row.add_widget(MDLabel(text=db.get_text(key), theme_text_color="Custom", text_color=(1,1,1,1), font_name="GlobalFont", size_hint_x=0.5))
            if db.data.get('premium'):
                btn = MDIconButton(icon="play-circle", theme_text_color="Custom", text_color=(0,1,0,1)); btn.bind(on_release=lambda x, f=file: self.player.play(f))
            else:
                btn = MDRaisedButton(text=db.get_text("buy"), md_bg_color=get_color_from_hex("#FF9100"), font_name="GlobalFont"); btn.bind(on_release=self.buy_dialog)
            row.add_widget(btn); card.add_widget(row); layout.add_widget(card)
        scroll.add_widget(layout); self.add_widget(scroll)
    def buy_dialog(self, x):
        self.dialog = MDDialog(title=fix_text("Unlock Premium?"), text=fix_text("Open PayPal?"), buttons=[MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()), MDFlatButton(text="PAY NOW", on_release=self.go_pay)])
        self.dialog.open()
    def go_pay(self, x): webbrowser.open(PAYMENT_LINK); db.data['premium'] = True; db.save(); self.dialog.dismiss(); self.build_ui(); App.get_running_app().show_toast("Thanks! Unlocked 🔓")

class SubScreenProfile(MDFloatLayout):
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        self.avatar_list = [f"cat_avatar_{i}.png" for i in range(1, 7)] 
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=30, spacing=15)
        profile_header = MDFloatLayout(size_hint=(None, None), size=("180dp", "180dp"), pos_hint={"center_x": .5})
        image_card = ClickableCard(size_hint=(None, None), size=("160dp", "160dp"), radius=[80], pos_hint={"center_x": .5, "center_y": .5}, md_bg_color=get_color_from_hex("#424242"), elevation=4)
        image_card.bind(on_release=self.open_avatar_dialog) 
        current_pic = db.data.get("profile_pic", self.avatar_list[0])
        if not os.path.exists(current_pic): current_pic = self.avatar_list[0]
        self.profile_image_widget = Image(source=current_pic, fit_mode="cover")
        image_card.add_widget(self.profile_image_widget)
        profile_header.add_widget(image_card)
        layout.add_widget(profile_header)
        layout.add_widget(MDLabel(text=db.get_text("name"), theme_text_color="Custom", text_color=(0.7,0.7,0.7,1), font_name="GlobalFont", size_hint_y=None, height="20dp"))
        self.tf_name = MDTextField(text=db.data['name'], font_name="GlobalFont", line_color_focus=get_color_from_hex("#FF9100"))
        layout.add_widget(self.tf_name)
        layout.add_widget(MDLabel(text=db.get_text("age"), theme_text_color="Custom", text_color=(0.7,0.7,0.7,1), font_name="GlobalFont", size_hint_y=None, height="20dp"))
        self.tf_age = MDTextField(text=str(db.data['age']), font_name="GlobalFont", line_color_focus=get_color_from_hex("#FF9100"))
        layout.add_widget(self.tf_age)
        layout.add_widget(MDLabel(text=db.get_text("weight"), theme_text_color="Custom", text_color=(0.7,0.7,0.7,1), font_name="GlobalFont", size_hint_y=None, height="20dp"))
        self.tf_weight = MDTextField(text=str(db.data['weight']), font_name="GlobalFont", line_color_focus=get_color_from_hex("#FF9100"))
        layout.add_widget(self.tf_weight)
        btn = MDFillRoundFlatIconButton(text=db.get_text("save"), icon="content-save", pos_hint={"center_x": .5}, font_name="GlobalFont", md_bg_color=get_color_from_hex("#FF6D00"))
        btn.bind(on_release=self.save)
        layout.add_widget(MDBoxLayout(size_hint_y=0.1)); layout.add_widget(btn); layout.add_widget(MDBoxLayout(size_hint_y=0.2))
        self.add_widget(layout)
    def open_avatar_dialog(self, inst):
        grid = MDGridLayout(cols=3, spacing="15dp", padding="10dp", size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        for filename in self.avatar_list:
            if os.path.exists(filename):
                card = ClickableCard(size_hint=(None, None), size=("80dp", "80dp"), radius=[40], md_bg_color=get_color_from_hex("#424242"))
                img = Image(source=filename, fit_mode="cover")
                card.add_widget(img)
                card.bind(on_release=lambda x, f=filename: self.set_avatar(f))
                grid.add_widget(card)
        scroll = MDScrollView(size_hint_y=None, height="300dp")
        scroll.add_widget(grid)
        self.dialog = MDDialog(title=db.get_text("choose_avatar"), type="custom", content_cls=scroll)
        self.dialog.open()
    def set_avatar(self, new_filename):
        db.data["profile_pic"] = new_filename; db.save(); self.profile_image_widget.source = new_filename; self.dialog.dismiss(); App.get_running_app().show_toast(db.get_text("saved_msg"))
    def save(self, x):
        try: db.data['name'] = self.tf_name.text; db.data['age'] = float(self.tf_age.text); db.data['weight'] = float(self.tf_weight.text); db.save(); App.get_running_app().show_toast(db.get_text("saved_msg"))
        except: pass

class CatOSApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange" 
        self.theme_cls.accent_palette = "Teal"    
        styles = ["H1", "H2", "H3", "H4", "H5", "H6", "Subtitle1", "Subtitle2", "Body1", "Body2", "Button", "Caption", "Overline"]
        for style in styles: self.theme_cls.font_styles[style] = ["GlobalFont", 16, False, 0.15]
        sm = MDScreenManager(transition=FadeTransition())
        sm.add_widget(LanguageScreen(name="lang_select"))
        sm.add_widget(MainAppScreen(name="main_app"))
        return sm
    
    def on_start(self):
        # 🔥🔥🔥 إضافة طلب الأذونات للأندرويد 🔥🔥🔥
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.RECORD_AUDIO, 
                Permission.WRITE_EXTERNAL_STORAGE, 
                Permission.READ_EXTERNAL_STORAGE
            ])
        
        # التحقق من التنبيهات
        db.check_and_notify()

    def show_toast(self, msg):
        snackbar = MDSnackbar(MDLabel(text=msg, font_name="GlobalFont", theme_text_color="Custom", text_color=(1, 1, 1, 1)), duration=1.5, md_bg_color=get_color_from_hex("#323232"), pos_hint={"center_x": .5, "y": .1}, size_hint_x=.8).open()

if __name__ == '__main__':
    from kivy.app import App
    CatOSApp().run()