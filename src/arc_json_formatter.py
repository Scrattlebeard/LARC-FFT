import json

class ArcJsonEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent_level = 0
        self.current_indent = ''

    def encode(self, obj):
        if isinstance(obj, dict):
            return self.encode_dict(obj)
        elif isinstance(obj, list):
            return self.encode_list(obj)
        else:
            return json.JSONEncoder.encode(self, obj)

    def encode_dict(self, d):
        self.indent_level += 1
        self.current_indent = '  ' * self.indent_level
        items = []
        for k, v in d.items():
            if k == 'input' or k == 'output':
                items.append(f'{self.current_indent}"{k}": {self.encode(v)}')
            else:
                items.append(f'{self.current_indent}"{k}": {self.encode(v)}')
        self.indent_level -= 1
        self.current_indent = '  ' * self.indent_level
        return '{\n' + ',\n'.join(items) + f'\n{self.current_indent}}}'

    def encode_list(self, lst):
        if all(isinstance(item, (int, float)) for item in lst):
            return json.JSONEncoder.encode(self, lst)
        else:
            self.indent_level += 1
            self.current_indent = '  ' * self.indent_level
            items = [f'{self.current_indent}{self.encode(item)}' for item in lst]
            self.indent_level -= 1
            self.current_indent = '  ' * self.indent_level
            return '[\n' + ',\n'.join(items) + f'\n{self.current_indent}]'

    def encode_output(self, output):
        return '[\n' + ',\n'.join(json.JSONEncoder.encode(self, item) for item in output) + '\n' + self.current_indent + ']'

def format_json(data):
    return json.dumps(data, cls=ArcJsonEncoder)

if __name__ == "__main__":
    # Example usage
    data = {
        "train": [
            {
                "input": [[1, 0, 7, 0, 0]],
                "output": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1],[0, 0, 0, 0, 0, 0, 0, 0, 1, 0],[0, 0, 0, 0, 0, 0, 0, 1, 0, 7]
                ]
            }
        ]
    }

    formatted_json = format_json(data)
    print(formatted_json)