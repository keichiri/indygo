import os

from indygo_generator.header_scraping import scrape_header_file, ParsingError


class GeneratorError(Exception):
    pass


class Generator:
    def __init__(self, header_dir_path, output_path):
        self._header_dir_path = header_dir_path
        self._output_path = output_path
        self._c_function_declarations = {}

    def _read_header_files(self):
        header_file_contents = {}

        try:
            for header_file_name in os.listdir(self._header_dir_path):
                header_file_path = os.path.join(self._header_dir_path, header_file_name)
                with open(header_file_path, 'r') as f:
                    file_content = f.read()
                    header_file_contents[header_file_name] = file_content
        except OSError as e:
            raise GeneratorError(f'Error while reading header files at path: {self._header_dir_path}') from e

        return header_file_contents

    def _prepare_c_function_declarations(self):
        header_file_contents = self._read_header_files()
        # Small hack to allow parsing regex to be simpler (no need to match enum)
        full_type_map = {'indy_error_t': 'int32_t'}
        c_function_declarations = {}

        try:
            for file_name, file_content in header_file_contents.items():
                declarations, type_map = scrape_header_file(file_content)
                full_type_map.update(type_map)
                c_function_declarations[file_name] = declarations
        except ParsingError as e:
            raise GeneratorError(f'Failed to parse header files at path: {self._header_dir_path}') from e

        for function_declarations in c_function_declarations.values():
            for declaration in function_declarations:
                declaration.resolve_alias(full_type_map)

        self._c_function_declarations = c_function_declarations
