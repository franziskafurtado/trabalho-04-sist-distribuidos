import subprocess

def startMultipleInstances(executables):
    for exec in executables:
        cmd = f'start cmd /k python {exec}'
        print(f"Iniciando: {cmd}")
        subprocess.Popen(cmd, shell=True)

executable_to_run = [
    "estoque.py",
    "pagamento.py",
    "entrega.py",
    "notificacao.py",
    "principal.py"
]

startMultipleInstances(executable_to_run)