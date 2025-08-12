from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from datetime import datetime
import calendar

KV = """
#:import rgba kivy.utils.get_color_from_hex
ScreenManager:
    transition: FadeTransition(duration=0.5)
    SplashScreen:
    MainScreen:

<SplashScreen@Screen>:
    name: 'splash'
    Image:
        source: 'splash.png'
        allow_stretch: True
        keep_ratio: False
        size_hint: 1,1
        pos: 0,0

<MainScreen@Screen>:
    name: 'main'
    canvas.before:
        Color:
            rgba: rgba('#E6F7FF')
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(10)
        BoxLayout:
            size_hint_y: None
            height: dp(64)
            padding: dp(8)
            canvas.before:
                Color:
                    rgba: rgba('#7EC8E3')
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "₹ Salary Calculator"
                bold: True
                color: rgba('#ffffff')
                font_size: '20sp'
        GridLayout:
            cols: 2
            size_hint_y: None
            row_default_height: dp(56)
            height: self.minimum_height
            spacing: dp(8)
            Label:
                text: "Monthly Salary (₹):"
                halign: 'left'
            TextInput:
                id: base_salary
                multiline: False
                input_filter: 'float'
                font_size: '18sp'
            Label:
                text: "Tax Amount (₹):"
                halign: 'left'
            TextInput:
                id: tax_amount
                multiline: False
                input_filter: 'float'
                font_size: '18sp'
            Label:
                text: "Medical Deduction (₹):"
                halign: 'left'
            TextInput:
                id: medical_amount
                multiline: False
                input_filter: 'float'
                font_size: '18sp'
            Label:
                text: "Leave Days:"
                halign: 'left'
            TextInput:
                id: leave_days
                multiline: False
                input_filter: 'int'
                font_size: '18sp'
            Label:
                text: "Dabba Kada Units:"
                halign: 'left'
            TextInput:
                id: dabba_units
                multiline: False
                input_filter: 'int'
                font_size: '18sp'
        Button:
            id: calc_btn
            text: "Calculate Salary"
            size_hint_y: None
            height: dp(52)
            background_normal: ''
            background_color: rgba('#34d399')
            color: rgba('#ffffff')
            font_size: '18sp'
            on_release: app.calculate()
        ScrollView:
            do_scroll_x: False
            GridLayout:
                id: results_box
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)
                padding: dp(4)
"""

def format_inr(amount):
    amount = float(amount)
    amount_str = f"{amount:,.2f}"
    parts = amount_str.split(".")
    integer_part = parts[0]
    decimal_part = parts[1]
    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        rest = integer_part[:-3].replace(",", "")
        rest_grouped = ",".join([rest[max(i-2,0):i] for i in range(len(rest),0,-2)][::-1])
        integer_part = rest_grouped + "," + last_three
    return f"₹{integer_part}.{decimal_part}"

def has_fifth_monday(year, month):
    month_calendar = calendar.monthcalendar(year, month)
    monday_count = sum(1 for week in month_calendar if week[calendar.MONDAY] != 0)
    return monday_count >= 5

class SalaryApp(App):
    def build(self):
        self.sm = Builder.load_string(KV)
        Clock.schedule_once(self.switch_to_main, 2.0)
        return self.sm

    def switch_to_main(self, dt):
        self.sm.current = 'main'

    def calculate(self):
        try:
            base_salary = float(self.sm.ids.base_salary.text or 0)
            tax_amount = float(self.sm.ids.tax_amount.text or 0)
            medical_amount = float(self.sm.ids.medical_amount.text or 0)
            leave_days = int(self.sm.ids.leave_days.text or 0)
            dabba_units = int(self.sm.ids.dabba_units.text or 0)
        except Exception:
            self.show_result("Please enter valid numbers.")
            return

        today = datetime.today()
        per_day_salary = base_salary / 30.0
        fifth_monday_bonus = per_day_salary if has_fifth_monday(today.year, today.month) else 0.0
        salary_with_bonus = base_salary + fifth_monday_bonus
        pf_deduction = base_salary * 0.10
        dabba_deduction = dabba_units * 30
        leave_deduction = per_day_salary * leave_days
        total_deductions = tax_amount + medical_amount + pf_deduction + dabba_deduction + leave_deduction
        net_monthly = salary_with_bonus - total_deductions

        results = [
            ("Salary for", f"{today.strftime('%B %Y')}"),
            ("Base Monthly Salary", format_inr(base_salary)),
            ("Per Day Salary (Base/30)", format_inr(per_day_salary)),
            ("Leave Days Taken", str(leave_days)),
            ("Leave Deduction", format_inr(leave_deduction)),
            ("5th Monday Bonus", format_inr(fifth_monday_bonus)),
            ("Salary with Bonus", format_inr(salary_with_bonus)),
            ("Tax Deduction", format_inr(tax_amount)),
            ("Medical Deduction", format_inr(medical_amount)),
            ("PF Deduction (10%)", format_inr(pf_deduction)),
            ("Dabba Kada Deduction", format_inr(dabba_deduction)),
            ("Total Deductions", format_inr(total_deductions)),
            ("Net Monthly Salary", format_inr(net_monthly)),
        ]

        box = self.sm.ids.results_box
        box.clear_widgets()
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        for title, value in results:
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=68, padding=(8,8))
            lbl_title = Label(text=str(title), size_hint_y=None, height=22, color=(0.15,0.15,0.15,1), halign='left', text_size=(self.sm.width-40, None), font_size='16sp')
            lbl_value = Label(text=str(value), size_hint_y=None, height=36, color=(0.06,0.47,0.55,1), halign='left', text_size=(self.sm.width-40, None), font_size='18sp')
            card.add_widget(lbl_title)
            card.add_widget(lbl_value)
            box.add_widget(card)

    def show_result(self, text):
        box = self.sm.ids.results_box
        box.clear_widgets()
        from kivy.uix.label import Label
        box.add_widget(Label(text=text))

if __name__ == '__main__':
    SalaryApp().run()
