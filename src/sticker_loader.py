class StickerLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def _load_stickers(self):
        stickers = []
        try:
            with open(self.file_path, 'r') as file:
                content = file.read().strip()
                stickers = content.split()
        except FileNotFoundError:
            print(f"Файл {self.file_path} не найден.")
        except Exception as e:
            print(f"Произошла ошибка при загрузке файла: {e}")
        
        return stickers

