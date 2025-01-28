"""
arquivo usado para gerar o relatório de trabalho
"""
from bs4 import BeautifulSoup as bs

__version__ = 'v1.0.7'
__author__ = 'Guto Hertzog'

ARQ = 'pagina.html'
REL = 'relatorio.txt'

class Tarefa:
    """classe para gerenciar as tarefas"""
    def __init__(self):
        self.titulo: str = ''
        self.data:str = ''
        self.projeto:str = ''
        self.horas:float = 0.0
        self.link_tarefa:str = ''
        self.link_projeto:str = ''
        self.code:str = ''
        self.contador:int = 0
        self.redmine:str = ''

    def __str__(self):
        """mostra a classe e seus dados"""
        texto = f'Titulo : {self.titulo}\n'
        texto += f'Data : {self.data}\n'
        texto += f'Projeto : {self.projeto}\n'
        texto += f'Horas : {self.horas}\n'
        texto += f'Link tarefa : {self.link_tarefa}\n'
        texto += f'Link projeto : {self.link_projeto}\n'
        texto += f'Code : {self.code}\n'
        texto += f'Contador : {self.contador}\n'
        return texto

    def gera_redmine(self):
        """gera o texto para o formato do redmine"""
        self.redmine = f'| {self.code} | "{self.titulo}":{self.link_tarefa} | '
        self.redmine += f'x{str(self.contador)} | h{self.horas:.2f} |\n'


def bubble_sort(lista):
    """função para realizar o ordenamento das tarefas usando o Bubble Sort"""
    tamanho: int = len(lista)

    while tamanho > 0:
        inicio: int = 0
        while inicio < tamanho - 1:
            atual: Tarefa = lista[inicio]
            proximo: Tarefa = lista[inicio + 1]

            if int(atual.code) > int(proximo.code):
                lista[inicio], lista[inicio+1] = lista[inicio+1], lista[inicio]

            inicio += 1
        tamanho -= 1

def recupera_tarefas(projetos, datas, problemas, horas):
    """funcao para separar as tarefas em objetos"""
    tarefas: list[Tarefa] = []

    for projeto, data, problema, hora in zip(projetos, datas, problemas, horas):
        # descarta a minha tarefa de relatório
        if 'Augusto - Plano de trabalho' in problema.get_text(strip=True):
            continue

        tarefa: Tarefa = Tarefa()

        ancora = problema.find('a')
        tarefa.link_tarefa = 'https://projetos.cpd.ufrgs.br' + ancora.get('href')
        tarefa.code = tarefa.link_tarefa.split('/')[-1]
        tarefa.contador = 0

        # busca por duplicados
        for item in tarefas:
            if item.link_tarefa == tarefa.link_tarefa:
                item.contador += 1
                tempo = float(hora.get_text(strip=True))
                item.horas += tempo
                break
        else:
            tarefa.titulo = problema.get_text(strip=True)

            # arruma o título das tarefas
            tarefa.projeto = projeto.get_text(strip=True)
            ancora = projeto.find('a')
            tarefa.link_projeto = 'https://projetos.cpd.ufrgs.br' + ancora.get('href')
            tarefa.data = data.get_text(strip=True)
            tarefa.titulo = tarefa.titulo.split(':')
            tarefa.titulo = ''.join(tarefa.titulo[1:]).strip()
            tarefa.contador += 1
            tarefa.horas = float(hora.get_text(strip=True))

            tarefas.append(tarefa)

    return tarefas

def salva(grupos):
    """funcao para salvar em arquivo o relatorio"""
    total: float = 0
    with open(REL, 'w', encoding='utf-8') as arq:
        contador: int = 0
        for projeto, tarefas in grupos.items():
            arq.write(f'|\\2=."{projeto}":{tarefas[0].link_projeto} |\\2=. ')
            arq.write(f'x{len(tarefas)} |\n')
            for tarefa in tarefas:
                arq.write(tarefa.redmine)
                total += tarefa.horas
                contador += 1
            arq.write('|\\4=.|\n')

        texto: str = f'|\\2>. Total | x{contador} | h{total:.2f} |'
        arq.write(texto)

def agrupa(tarefas: list[Tarefa]) -> dict[str, list[Tarefa]]:
    """ fucao para agrupas as tarefas por projeto """
    grupos: dict[str, list[Tarefa]] = {}

    for tarefa in tarefas:
        if tarefa.projeto not in grupos:
            grupos[tarefa.projeto] = []
        grupos[tarefa.projeto].append(tarefa)

    return grupos


def dados() -> None:
    """ só uma função besta para mostrar meus dados """
    print(f'versão : {__version__}')
    print(f'autor : {__author__}')


def start():
    """ inicia o programa """
    dados()

    with open(ARQ, 'r', encoding='utf-8') as arq:
        html = arq.read()

    soup = bs(html, 'html.parser')
    projetos = soup.find_all('td', {'class': 'project'})
    datas = soup.find_all('td', {'class': 'spent_on'})
    problemas = soup.find_all('td', {'class': 'issue'})
    horas = soup.find_all('td', {'class': 'hours'})

    tarefas = recupera_tarefas(projetos, datas, problemas, horas)

    for tarefa in tarefas:
        tarefa.gera_redmine()

    bubble_sort(tarefas)

    grupos = agrupa(tarefas)
    grupos = dict(sorted(grupos.items()))

    salva(grupos)

    print('terminado')

if __name__ == "__main__":
    start()

