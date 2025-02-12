import json
import os
import random
from decimal import Decimal


def open_txt_with_line_control(file_txt, strip_spaces: bool = True):
    # Удаление пустых строк и пробелов
    with open(file_txt) as f1:
        lines = f1.readlines()
        non_empty_lines = list(line for line in lines if not line.isspace())

        if strip_spaces:
            non_empty_lines = list(line.strip() for line in non_empty_lines)

        return non_empty_lines

def join_path(path: str | tuple | list) -> str:
    if isinstance(path, str):
        return path
    return str(os.path.join(*path))


def read_json(path: str | tuple | list, encoding: str | None = None) -> list | dict:
    path = join_path(path)
    return json.load(open(path, encoding=encoding))


def touch(path: str | tuple | list, file: bool = False) -> bool:
    """
    Create an object (file or directory) if it doesn't exist.

    :param Union[str, tuple, list] path: path to the object
    :param bool file: is it a file?
    :return bool: True if the object was created
    """
    path = join_path(path)
    if file:
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write('')

            return True

        return False

    if not os.path.isdir(path):
        os.mkdir(path)
        return True

    return False


def write_json(path: str | tuple | list, obj: list | dict, indent: int | None = None,
               encoding: str | None = None) -> None:
    """
    Write Python list or dictionary to a JSON file.

    :param Union[str, tuple, list] path: path to the JSON file
    :param Union[list, dict] obj: the Python list or dictionary
    :param Optional[int] indent: the indent level
    :param Optional[str] encoding: the name of the encoding used to decode or encode the file
    """
    path = join_path(path)
    with open(path, mode='w', encoding=encoding) as f:
        json.dump(obj, f, indent=indent)


def randfloat(from_: int | float | str, to_: int | float | str,
              step: int | float | str | None = None) -> float:
    """
    Return a random float from the range.

    :param Union[int, float, str] from_: the minimum value
    :param Union[int, float, str] to_: the maximum value
    :param Optional[Union[int, float, str]] step: the step size (calculated based on the number of decimal places)
    :return float: the random float
    """
    from_ = Decimal(str(from_))
    to_ = Decimal(str(to_))
    if not step:
        step = 1 / 10 ** (min(from_.as_tuple().exponent, to_.as_tuple().exponent) * -1)

    step = Decimal(str(step))
    rand_int = Decimal(str(random.randint(0, int((to_ - from_) / step))))
    return float(rand_int * step + from_)


def update_dict(modifiable: dict, template: dict, rearrange: bool = True, remove_extra_keys: bool = False) -> dict:
    """
    Update the specified dictionary with any number of dictionary attachments based on the template without changing the values already set.

    :param dict modifiable: a dictionary for template-based modification
    :param dict template: the dictionary-template
    :param bool rearrange: make the order of the keys as in the template, and place the extra keys at the end (True)
    :param bool remove_extra_keys: whether to remove unnecessary keys and their values (False)
    :return dict: the modified dictionary
    """
    for key, value in template.items():
        if key not in modifiable:
            modifiable.update({key: value})

        elif isinstance(value, dict):
            modifiable[key] = update_dict(
                modifiable=modifiable[key], template=value, rearrange=rearrange, remove_extra_keys=remove_extra_keys
            )

    if rearrange:
        new_dict = {}
        for key in template.keys():
            new_dict[key] = modifiable[key]

        for key in tuple(set(modifiable) - set(new_dict)):
            new_dict[key] = modifiable[key]

    else:
        new_dict = modifiable.copy()

    if remove_extra_keys:
        for key in tuple(set(modifiable) - set(template)):
            del new_dict[key]

    return new_dict

def get_file_names(directory_path, files: bool = True):
    """
    Получает список имен всех файлов в указанной папке.

    :param files: Получать имена файлов если True, иначе получать имена папок
    :param directory_path: Путь к папке.
    :return: Список имен файлов.
    """
    try:
        # Проверяем, существует ли папка
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Папка '{directory_path}' не существует.")

        if files:
            # Получаем список файлов
            file_names = [file for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file))]
            for file_name in file_names:
                if file_name.startswith('.~'):
                    file_names.remove(file_name)
        else:
            file_names = [join_path([directory_path, file])  for file in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, file))]
            # for file_name in file_names:
            #     if file_name.startswith('.~'):
            #         file_names.remove(file_name)

        return file_names
    except Exception as e:
        print(f"Ошибка: {e}")
        return []
