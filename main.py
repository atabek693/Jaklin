# main.py

import json
from difflib import get_close_matches
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window

class ChatBotApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.knowledge_base_file = 'knowledge_base.json'
        self.knowledge_base = self.load_knowledge_base()

    def build(self):
        Window.clearcolor = (0.8, 0.8, 0.8, 1)  # Установка цвета фона

        layout = BoxLayout(orientation='vertical', padding=dp(20))

        chat_history_label = Label(text="История Чата:", size_hint=(1, 0.1), color=(0, 0.5, 1, 1))  # Синий цвет
        layout.add_widget(chat_history_label)

        self.chat_history = TextInput(readonly=True, size_hint=(1, 0.5), background_color=(1, 1, 1, 1))  # Белый фон
        layout.add_widget(self.chat_history)

        self.user_input_field = TextInput(hint_text="Напиши письмо...", multiline=False, size_hint=(1, 0.1),
                                          background_color=(1, 1, 1, 1))  # Белый фон
        layout.add_widget(self.user_input_field)

        send_button = Button(text="Отправить", size_hint=(1, 0.1), background_color=(0, 0.7, 0.3, 1))  # Зеленый цвет
        send_button.bind(on_press=self.on_send_button_press)
        layout.add_widget(send_button)

        return layout

    def load_knowledge_base(self):
        try:
            with open(self.knowledge_base_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"questions": []}
        return data

    def save_knowledge_base(self):
        try:
            with open(self.knowledge_base_file, 'w') as file:
                json.dump(self.knowledge_base, file, indent=2)
        except Exception as e:
            self.show_error_popup(f"Error saving knowledge base: {e}")

    def find_best_match(self, user_question):
        questions = [q.get("question", "") for q in self.knowledge_base.get("questions", [])]
        matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
        return matches[0] if matches else None

    def get_answer_for_question(self, question):
        for q in self.knowledge_base.get("questions", []):
            if q.get("question") == question:
                return q.get("answer")
        return None

    def add_message(self, message):
        self.chat_history.text += message + "\n"

    def on_send_button_press(self, instance):
        user_input = self.user_input_field.text.strip()

        if not user_input:
            return

        self.add_message('Вы: ' + user_input)

        best_match = self.find_best_match(user_input)

        if best_match:
            answer = self.get_answer_for_question(best_match)
            if answer:
                self.add_message('Джаклин: ' + answer)
            else:
                self.add_message("Джаклин: Я не знаю ответа на этот вопрос.")
        else:
            self.add_message("Джаклин: Я не знаю ответа. Вы можете мне помочь?")
            self.show_new_answer_popup(user_input)

        self.user_input_field.text = ''

    def show_new_answer_popup(self, question):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(20))
        popup_label = Label(text="Пишите ответа:", size_hint=(1, 0.7), color=(0, 0.5, 1, 1))  # Синий цвет
        popup_layout.add_widget(popup_label)
        answer_input = TextInput(multiline=True, size_hint=(1, 0.3), background_color=(1, 1, 1, 1))  # Белый фон
        popup_layout.add_widget(answer_input)

        def on_submit(instance):
            answer = answer_input.text.strip()
            if answer:
                self.knowledge_base["questions"].append({"question": question, "answer": answer})
                self.save_knowledge_base()
                self.add_message('Джаклин: Спасибо я научился новым ответам!')
                popup.dismiss()
            else:
                self.show_error_popup("Answer cannot be empty!")

        submit_button = Button(text="Submit", size_hint=(1, 0.1), background_color=(0, 0.7, 0.3, 1))  # Зеленый цвет
        submit_button.bind(on_press=on_submit)
        popup_layout.add_widget(submit_button)

        popup = Popup(title='New Answer', content=popup_layout, size_hint=(None, None), size=(600, 400),
                      auto_dismiss=False)
        popup.open()

    def show_error_popup(self, message):
        popup = Popup(title='Error', content=Label(text=message), size_hint=(None, None), size=(400, 200),
                      background_color=(1, 0, 0, 1))  # Красный цвет
        popup.open()

if __name__ == '__main__':
    ChatBotApp().run()