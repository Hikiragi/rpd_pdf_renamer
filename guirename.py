import datetime
import os
import dearpygui.dearpygui as dpg
from config import Config
import main
import locale



class MainWindow:
    def __init__(self, config: Config, main_process: main):
        self.config = config
        self.main_process = main_process
        self.status_themes = None
        self.find_files = None
        self.complete_files = None
        self.error_files = None

    def setup_font_theme(self):
        font_path = self.config.PATH_FONT
        with dpg.font_registry():
            with dpg.font(font_path, 20) as default_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

            dpg.bind_font(default_font)

    @staticmethod
    def _selector_callback(sender, app_data):
        print('/' * 75)
        print('OK was clicked')
        print(f'sender: {sender}')
        print(f'AppData: {app_data}')
        dpg.set_value('input_path', app_data['file_path_name'])

    # @staticmethod
    # def _cancel_selector_callback(sender, app_data):
    #     print('/' * 75)
    #     print('Cancel was clicked')
    #     print(f'sender: {sender}')
    #     print(f'AppData: {app_data}')

    def start_renaming(self):
        directory = 'Путь не выбран' if dpg.get_value('input_path') == '' else dpg.get_value('input_path')
        if directory == 'Путь не выбран':
            self.add_table_row('Путь не выбран', 'ошибка', datetime.datetime.now().strftime('%H:%M:%S'),
                               'Необходимо вписать путь')
            return
        elif not os.path.isdir(directory):
            self.add_table_row('Ошибка', 'ошибка', datetime.datetime.now().strftime('%H:%M:%S'),
                               f'Папка не существует: {directory}')

        if dpg.does_item_exist('output_table'):
            rows = dpg.get_item_children('output_table', 1)
            for row in rows:
                dpg.delete_item(row)

        self.complete_files, self.error_files, self.find_files = self.rename_files(directory)
        dpg.set_value('all_files_text_id', f'Найдено файлов: {self.find_files}')
        dpg.set_value('completed_files_text_id', f'Завершено: {self.complete_files}')
        dpg.set_value('error_files_text_id', f'Ошибок: {self.error_files}')

    def rename_files(self, directory):
        """Основная функция переименования файлов"""
        find_files = 0
        renamed_count = 0
        error_count = 0

        for filename in os.listdir(directory):
            if not filename.lower().endswith('.pdf'):
                continue

            file_path = os.path.join(directory, filename)
            current_time = datetime.datetime.now().strftime("%H:%M:%S")

            try:
                # Извлекаем код из PDF
                code = self.main_process.extract_code_from_pdf(file_path)
                if not code:
                    self.add_table_row(filename, "ошибка", current_time, "Не найден код")
                    find_files += 1
                    error_count += 1
                    continue

                # Формируем новое имя
                new_name = self.main_process.process_filename(filename, code, file_path)
                if not new_name:
                    self.add_table_row(filename, "ошибка", current_time, "Не удалось извлечь название")
                    find_files += 1
                    error_count += 1
                    continue

                new_path = os.path.join(directory, new_name)

                # Обработка дубликатов
                counter = 1
                while os.path.exists(new_path):
                    base, ext = os.path.splitext(new_name)
                    new_name = f"{base} ({counter}){ext}"
                    new_path = os.path.join(directory, new_name)
                    counter += 1

                os.rename(file_path, new_path)
                self.add_table_row(filename, "готово", current_time, f"Изменено")
                find_files += 1
                renamed_count += 1

            except Exception as e:
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                self.add_table_row(filename, "ошибка", current_time, str(e))
                find_files += 1
                error_count += 1

        return renamed_count, error_count, find_files

    def create_main(self):
        try:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        except Exception as e:
            print(f'Не удалось установить локаль: {e}')

        dpg.create_context()
        self.setup_font_theme()

        with dpg.theme() as status_ready_theme:
            with dpg.theme_component(dpg.mvText):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 255, 0, 255))


        with dpg.theme() as status_error_theme:
            with dpg.theme_component(dpg.mvText):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0, 255))

        self.status_themes = {
            'готово': status_ready_theme,
            'ошибка': status_error_theme
        }

        with dpg.file_dialog(directory_selector=True,
                             show=False,
                             tag='file_dialog_id',
                             callback=self._selector_callback,
                             # cancel_callback=self._cancel_selector_callback,
                             width=self.config.MAX_SIZE_WIDTH / 2,
                             height=self.config.MAX_SIZE_HEIGHT / 1.75,
                             ):
            dpg.add_file_extension(".*")
            dpg.add_file_extension('', color=(255, 155, 78, 255))
            dpg.add_file_extension('.pdf', color=(0, 255, 0))

        dpg.create_viewport(title='GUI for renaming v3.0.0',
                            width=self.config.MAX_SIZE_WIDTH,
                            height=self.config.MAX_SIZE_HEIGHT)

        with dpg.window(label='Главное окно',
                        no_close=True,
                        no_title_bar=True,
                        width=self.config.MAX_SIZE_WIDTH - 15,
                        height=self.config.MAX_SIZE_HEIGHT - 15,
                        no_move=True,
                        no_collapse=True,
                        tag='main_window'):
            dpg.add_text('Интерфейс переименования документов')

            dpg.add_input_text(width=self.config.MAX_SIZE_WIDTH - 200,
                               height=self.config.MAX_SIZE_HEIGHT - 100,
                               tag='input_path')

            dpg.add_button(label='Выбрать путь',
                           callback=lambda: dpg.show_item('file_dialog_id'),
                           pos=[self.config.MAX_SIZE_WIDTH - 175, self.config.MAX_SIZE_HEIGHT - 140],
                           width=self.config.MAX_SIZE_BTN_WIDTH,
                           height=self.config.MAX_SIZE_BTN_HEIGHT)

            dpg.add_button(label='Начать',
                           callback=self.start_renaming,
                           pos=[self.config.MAX_SIZE_WIDTH - 175, self.config.MAX_SIZE_HEIGHT - 380],
                           width=self.config.MAX_SIZE_BTN_WIDTH,
                           height=self.config.MAX_SIZE_BTN_HEIGHT)

            with dpg.table(label='Таблица вывода результатов',
                           tag='output_table',
                           width=self.config.MAX_SIZE_WIDTH - 200,
                           height=self.config.MAX_SIZE_HEIGHT - 250,
                           pos=[10, self.config.MAX_SIZE_HEIGHT - 350],
                           header_row=True,
                           borders_innerH=True,
                           borders_outerH=True,
                           borders_innerV=True,
                           borders_outerV=True,
                           reorderable=True,
                           resizable=True,
                           hideable=True,
                           scrollY=True,
                           scrollX=True):
                dpg.add_table_column(label='Название', width_stretch=True)
                dpg.add_table_column(label='Статус', width_fixed=True, init_width_or_weight=75)
                dpg.add_table_column(label='Время', width_fixed=True, init_width_or_weight=90)
                dpg.add_table_column(label='Описание', width_fixed=True, init_width_or_weight=250)



            dpg.add_text(f'Всего найдено: {0 if self.find_files is None else self.find_files}', tag='all_files_text_id')
            dpg.add_text(f'Завершено: {0 if self.complete_files is None else self.complete_files}',
                         tag='completed_files_text_id')
            dpg.add_text(f'Ошибок: {0 if self.error_files is None else self.error_files}', tag='error_files_text_id')

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def add_table_row(self, name, status, time, note=''):
        with dpg.table_row(parent='output_table'):
            dpg.add_text(name)

            status_item = dpg.add_text(status)

            theme = self.status_themes.get(status.lower())
            if theme:
                dpg.bind_item_theme(status_item, theme)
            dpg.add_text(time)
            dpg.add_text(note)


def mainloop():
    config = Config()
    main_process = main
    main_wind = MainWindow(config, main_process)
    main_wind.create_main()


if __name__ == '__main__':
    mainloop()
