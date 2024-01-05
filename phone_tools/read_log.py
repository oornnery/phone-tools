import logging
import time

logging.basicConfig(level=logging.INFO)

def read_file(filename, debug=False):
    with open(filename, 'r') as file:
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)  # Aguarde um curto período antes de tentar novamente
            else:
                if debug:
                    logging.info(f"Read line: {line.strip()}")
                yield line.strip()

def main():
    import os
    
    filename = os.path.expanduser('~/.twinkle/twinkle.log')

    # Iniciar a leitura
    read_task = read_file(filename, debug=True)

    # Aguardar até que a tarefa de leitura seja concluída
    for line in read_task:
        print(f"Processed line: {line}")

if __name__ == "__main__":
    main()
