from rich import print

# Read file .twinkle/{account}.cfg
# Change account parameters
# Save file .twinkle/{account}.cfg
# 


def main(filename: str) -> dict:
    with open(filename, 'r') as f:
        config = f.readlines()
        try:
            cfg = {x[0]: x[1] if len(x) >= 2 else '' \
                for x in [x.replace('\n', '').split('=') \
                for x in config if not x.startswith('#') and x != '\n']}
        except Exception as e:
            print(e)
            return {}
        return cfg


if __name__ == "__main__":
    
    
    cfg = main('phone_tools/.twinkle/.twinkle/062099137.cfg')
    print(cfg)