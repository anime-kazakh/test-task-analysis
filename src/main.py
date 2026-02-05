import csv
from collections import defaultdict
from tabulate import tabulate
import argparse
from pathlib import Path

# CL - Country List
type RawCL = dict[str, list[float]]
type FormateCL = list[tuple[str, float]]

def parse_file(file:Path, country_list:RawCL)->RawCL:
    '''
    Парсит csv таблицу и выдаёт уже подготовленные данные

    param:
        file (Path): csv файл.
        country_list (RawCL): словарь где ключ название страны, а значение список с ВВП.

    return:
        RawCL: словарь где ключ название страны, а значение список с ВВП.
    '''
    if file.suffix != '.csv':
        raise ValueError(f"Файл {file} должен иметь расширение .csv")

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            country_list[row['country']].append(float(row['gdp']))

    return country_list

def formate_data(county_list:RawCL)->FormateCL:
    '''
    Форматирует данные

    param:
        country_list (RawCL): словарь где ключ название страны, а значение список с ВВП.

    return:
        list[tuple]: список кортежей типа (название страны, среднее ВВП).
    '''
    from statistics import mean
    # Теперь из словаря создаём список картежей где (country, average_gdp) и сортируем по убыванию
    return sorted(
        [ (country, round(mean(gdps), 2)) for country, gdps in county_list.items() ],
        key=lambda x: x[1],
        reverse=True
        )

def report(data: FormateCL, filename:str|None=None)->None:
    '''
    Формирование отчета

    param:
        data (FormateCL): данные которые необходимо либо вывести в консоль, либо в файл.
        filename (str|None): имя файла. По умолчанию None - выводит в консоль.
    '''
    if filename and filename.strip():
        output_path = Path(filename).with_suffix('.csv')

        with open(output_path, newline='', mode='w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(('country', 'average_gdp'))
            writer.writerows(data)
    else:
        print(tabulate(
            data,
            headers=['country', 'gdp'],
            showindex='always',
            tablefmt='github')
            )

def main():
    try:
        # Инициализируем аргументы коммандной строки
        cmd_parser = argparse.ArgumentParser(
            prog='analyzer',
            description='Анализирует макроэкономические данные'
            )
        
        cmd_parser.add_argument(
            '-f', '--files', 
            nargs='+',
            required=True,
            type=Path,
            help='Файл или несколько csv файлов.'
            )
        cmd_parser.add_argument(
            '-r', '--report',
            help='Название файла выходного отчета.'
            )

        # Парсим аргументы
        arguments = cmd_parser.parse_args()

        # Инициализируем словарь где ключ это название страны а значение фабрика списков
        country_list = defaultdict(list)

        # Парсим файлы
        for file in arguments.files:
            country_list = parse_file(file, country_list)

        # Форматируем данные
        country_list = formate_data(country_list)

        # Формируем отчет
        report(country_list, filename=arguments.report)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    main()