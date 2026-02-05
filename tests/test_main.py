import pytest
import pytest_mock
from unittest.mock import patch, call, Mock
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from collections import defaultdict
import sys

from src.main import formate_data, parse_file, report, main, RawCL, FormateCL

@pytest.fixture(scope='session')
def setup_test_file():
    test_file = Path('test.csv')
    test_file.touch()
    yield
    test_file.unlink()

@pytest.fixture
def setup_files():
    open_files:list[Path] = []
    def _open(files:tuple[str, ...]):
        for f in files:
            file = Path(f)
            open_files.append(file)
            file.touch()
    yield _open

    for f in open_files:
        f.unlink()

@pytest.fixture(scope='session')
def fill_prepared_data_test_file():
    def _fill_file(filename):
        with open(filename, newline='', mode='w') as test_file:
            with open('economic1.csv', newline='', mode='r') as prep_file:
                test_file.write(prep_file.read())
    return _fill_file

@pytest.fixture
def prep_data()->RawCL:
    data:RawCL = {
        'United States': [25462.0, 23315.0, 22994.0],
        'China': [17963.0, 17734.0, 17734.0],
        'Germany': [4086.0, 4072.0, 4257.0],
        'Japan': [4230.0, 4235.0, 4936.0],
        'India': [3736.0, 3385.0, 3150.0],
        'United Kingdom': [3139.0, 3070.0, 3131.0],
        'France': [2788.0, 2779.0, 2937.0],
        'Brazil': [2173.0, 1920.0, 1609.0],
        'Italy': [2010.0, 2011.0, 2105.0],
        'Canada': [2140.0, 2154.0, 1995.0],
        'South Korea': [1698.0, 1667.0, 1817.0],
        'Russia': [2240.0, 2215.0, 1778.0],
        'Australia': [1693.0, 1675.0, 1543.0],
    }
    return data

@pytest.fixture
def prep_data_format()->FormateCL:
    data = [
        ('United States', 23923.67),
        ('China', 17810.33),
        ('Japan', 4467.0),
        ('Germany', 4138.33),
        ('India', 3423.67),
        ('United Kingdom', 3113.33),
        ('France', 2834.67),
        ('Canada', 2096.33),
        ('Russia', 2077.67),
        ('Italy', 2042.0),
        ('Brazil', 1900.67),
        ('South Korea', 1727.33),
        ('Australia', 1637.0),
    ]
    return data

@pytest.mark.usefixtures('setup_test_file')
class TestParseFile:
    '''
    Тесты функции parser_file
    '''
    @pytest.mark.parametrize(
        'filename, expectation',
        [
            (Path('text.txt'), pytest.raises(ValueError)),
            (Path('text.pro'), pytest.raises(ValueError)),
            (Path('test.csv'), does_not_raise()),
        ]
    )
    def test_raises(self, prep_data, filename:Path, expectation):
        '''
        Тесты исключений
        '''
        with expectation:
            assert parse_file(filename, prep_data) == prep_data

    def test_parsing(self, prep_data, fill_prepared_data_test_file):
        '''
        Тесты чтения файла
        '''
        fill_prepared_data_test_file('test.csv')
        assert parse_file(Path('test.csv'), defaultdict(list)) == prep_data


class TestFormateData:
    '''
    Тесты функции formate_data
    '''
    def test_formatting(self, prep_data, prep_data_format):
        '''
        Тест форматировнаия
        '''
        assert formate_data(prep_data) == prep_data_format


class TestReport:
    '''
    Тесты функции report
    '''
    @pytest.mark.parametrize(
        'filename',
        [
            'test',
            'test.txt',
            'test.csv'
        ],
    )
    def test_creating_csv_file(self, prep_data_format, filename):
        '''
        Тесты создания csv файлов
        '''
        report(prep_data_format, filename)
        file_p = Path(filename).with_suffix('.csv')

        assert file_p.exists()
        assert file_p.is_file()

    @pytest.mark.parametrize(
        'filename',
        [
            '',
            ' ',
            '   ',
        ]
    )
    def test_empty_str_filename(self, prep_data_format, filename):
        '''
        Тест на передаваемую пустую строку
        '''
        with patch('builtins.print') as mock_print:
            report(prep_data_format, filename)
            mock_print.assert_called_once()
        

class TestMain:
    '''
    Тесты основной функции программы
    '''
    @pytest.mark.parametrize(
        'files',
        [
            ('file1.csv', ),
            ('file1.csv', 'file2.csv'),
            ('file1.csv', 'file2.csv', 'file3.csv'),
        ]
    )
    def test_many_files(self, monkeypatch, mocker, setup_files, files):
        '''
        Тесты флага --files
        '''
        mock_parse_file = mocker.patch('src.main.parse_file')
        
        country_list:RawCL = defaultdict(list)

        mock_parse_file.side_effect = lambda file, country_list: country_list

        test_args = ['main.py', '-f', *files]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        setup_files(files)

        main()

        expected_calls = [call(Path(f), country_list) for f in files ]

        assert mock_parse_file.call_args_list == expected_calls

    def test_several_files(self, monkeypatch, mocker, setup_files, fill_prepared_data_test_file, prep_data):
        '''
        Тесты чтения нескольких файлов
        '''
        files = ('test1.csv', 'test2.csv')

        test_args = ['main.py', '-f', *files]
        monkeypatch.setattr(sys, 'argv', test_args)

        setup_files(files)

        for f in files:
            fill_prepared_data_test_file(f)

        mock_formate_data:Mock = mocker.patch('src.main.formate_data')

        main()

        country_list = prep_data
        
        for key, value in country_list.items():
            country_list[key].extend(value)

        mock_formate_data.assert_called_once_with(country_list)
