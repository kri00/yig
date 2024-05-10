import json

def read_file(name="token_path"):
    try:
        with open(name, "r") as f:
            data = json.load(f)
    except:
        data = {}
    return data

def write_file(data, name="token_path"):
    with open(name, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    
