"""
Simulador de Pipeline PipeLang - Semana 03
Executa pipelines a partir da representação intermediária (IR) em JSON
Autor: Sistema de Compiladores - Grupo 3
"""

import json
import sys
import time
import random
from datetime import datetime
from typing import Dict, List, Set


class Colors:
    """Códigos ANSI para cores no terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ArtifactManager:
    """
    Gerencia o rastreamento de artefatos (dados intermediários) durante a execução.
    Cada tarefa produz e consome artefatos.
    """

    def __init__(self):
        self.available_artifacts: Set[str] = set()
        self.artifact_producers: Dict[str, str] = {}  # artefato -> tarefa que o produziu

    def register_artifact(self, artifact_name: str, producer_task: str):
        """Registra que um artefato foi produzido por uma tarefa"""
        self.available_artifacts.add(artifact_name)
        self.artifact_producers[artifact_name] = producer_task

    def is_available(self, artifact_name: str) -> bool:
        """Verifica se um artefato está disponível para uso"""
        return artifact_name in self.available_artifacts

    def check_inputs(self, inputs: List[str]) -> tuple[bool, List[str]]:
        """
        Verifica se todos os inputs necessários estão disponíveis.
        Retorna (sucesso, lista_de_faltantes)
        """
        missing = [inp for inp in inputs if not self.is_available(inp)]
        return (len(missing) == 0, missing)

    def get_producer(self, artifact_name: str) -> str:
        """Retorna o nome da tarefa que produziu o artefato"""
        return self.artifact_producers.get(artifact_name, "UNKNOWN")


class TaskExecutor:
    """
    Executa a simulação de uma tarefa individual.
    Simula operações EXTRACT, TRANSFORM e LOAD com delays e logs.
    """

    def __init__(self, artifact_manager: ArtifactManager):
        self.artifact_manager = artifact_manager

    def execute(self, task: Dict) -> bool:
        """
        Executa a simulação de uma tarefa.
        Retorna True se sucesso, False se falha.
        """
        task_id = task['id']
        task_type = task['type']
        inputs = task.get('inputs', [])
        outputs = task.get('outputs', [])

        # Simula diferentes operações baseadas no tipo
        if task_type == 'EXTRACT':
            return self._simulate_extract(task_id, outputs)
        elif task_type == 'TRANSFORM':
            return self._simulate_transform(task_id, inputs, outputs)
        elif task_type == 'LOAD':
            return self._simulate_load(task_id, inputs)
        else:
            print(f"{Colors.RED}  -> Tipo de tarefa desconhecido: {task_type}{Colors.ENDC}")
            return False

    def _simulate_extract(self, task_id: str, outputs: List[str]) -> bool:
        """Simula uma operação de EXTRACT (extração de dados)"""
        print(f"{Colors.CYAN}  -> Extraindo dados da fonte...{Colors.ENDC}")
        time.sleep(random.uniform(0.3, 0.8))  # Simula tempo de extração

        # Registra os artefatos produzidos
        for output in outputs:
            self.artifact_manager.register_artifact(output, task_id)
            print(f"{Colors.GREEN}  -> Artefato gerado: '{output}' OK{Colors.ENDC}")

        return True

    def _simulate_transform(self, task_id: str, inputs: List[str], outputs: List[str]) -> bool:
        """Simula uma operação de TRANSFORM (transformação de dados)"""
        # Verifica se todos os inputs estão disponíveis
        for inp in inputs:
            if not self.artifact_manager.is_available(inp):
                print(f"{Colors.RED}  -> Erro: Artefato '{inp}' não disponível X{Colors.ENDC}")
                return False
            producer = self.artifact_manager.get_producer(inp)
            print(f"{Colors.CYAN}  -> Lendo artefato: '{inp}' (de {producer}) OK{Colors.ENDC}")

        print(f"{Colors.CYAN}  -> Transformando dados...{Colors.ENDC}")
        time.sleep(random.uniform(0.4, 1.0))  # Simula tempo de transformação

        # Registra os artefatos produzidos
        for output in outputs:
            self.artifact_manager.register_artifact(output, task_id)
            print(f"{Colors.GREEN}  -> Artefato gerado: '{output}' OK{Colors.ENDC}")

        return True

    def _simulate_load(self, task_id: str, inputs: List[str]) -> bool:
        """Simula uma operação de LOAD (carregamento de dados)"""
        # Verifica se todos os inputs estão disponíveis
        for inp in inputs:
            if not self.artifact_manager.is_available(inp):
                print(f"{Colors.RED}  -> Erro: Artefato '{inp}' não disponível X{Colors.ENDC}")
                return False
            producer = self.artifact_manager.get_producer(inp)
            print(f"{Colors.CYAN}  -> Lendo artefato: '{inp}' (de {producer}) OK{Colors.ENDC}")

        print(f"{Colors.CYAN}  -> Carregando dados no destino final...{Colors.ENDC}")
        time.sleep(random.uniform(0.2, 0.6))  # Simula tempo de carregamento

        print(f"{Colors.GREEN}  -> Dados carregados com sucesso OK{Colors.ENDC}")
        return True


class PipelineSimulator:
    """
    Orquestrador principal da simulação.
    Carrega a IR, valida e executa as tarefas na ordem correta.
    """

    def __init__(self, ir_file_path: str):
        self.ir_file_path = ir_file_path
        self.ir: Dict = {}
        self.artifact_manager = ArtifactManager()
        self.task_executor = TaskExecutor(self.artifact_manager)
        self.task_states: Dict[str, str] = {}  # task_id -> estado (pending, running, completed, failed)
        self.task_times: Dict[str, float] = {}  # task_id -> tempo de execução
        self.start_time = None
        self.end_time = None

    def load_ir(self) -> bool:
        """Carrega e valida o arquivo IR JSON"""
        try:
            with open(self.ir_file_path, 'r', encoding='utf-8') as f:
                self.ir = json.load(f)

            # Valida estrutura básica
            required_keys = ['metadata', 'tasks', 'execution_order']
            for key in required_keys:
                if key not in self.ir:
                    print(f"{Colors.RED}Erro: IR inválida - faltando chave '{key}'{Colors.ENDC}")
                    return False

            # Inicializa estados das tarefas
            for task in self.ir['tasks']:
                self.task_states[task['id']] = 'pending'

            return True

        except FileNotFoundError:
            print(f"{Colors.RED}Erro: Arquivo não encontrado: {self.ir_file_path}{Colors.ENDC}")
            return False
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}Erro: JSON inválido - {str(e)}{Colors.ENDC}")
            return False

    def print_header(self):
        """Exibe o cabeçalho do simulador"""
        print()
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}SIMULADOR DE PIPELINE - PipeLang v1.0{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print()

        # Informações do pipeline
        metadata = self.ir.get('metadata', {})
        print(f"{Colors.BOLD}Pipeline:{Colors.ENDC} {metadata.get('source_file', 'N/A')}")
        print(f"{Colors.BOLD}Total de tarefas:{Colors.ENDC} {metadata.get('total_tasks', len(self.ir['tasks']))}")
        print(f"{Colors.BOLD}Compilado em:{Colors.ENDC} {metadata.get('generated_at', 'N/A')}")
        print()

    def verify_dependencies(self, task: Dict) -> bool:
        """Verifica se todas as dependências de uma tarefa foram completadas"""
        depends_on = task.get('depends_on', [])

        for dep in depends_on:
            if self.task_states.get(dep) != 'completed':
                print(f"{Colors.YELLOW}  -> Aguardando dependência: {dep} (estado: {self.task_states.get(dep)}){Colors.ENDC}")
                return False

        # Se há dependências, mostra que foram satisfeitas
        if depends_on:
            for dep in depends_on:
                print(f"{Colors.GREEN}  -> Dependência satisfeita: {dep} OK{Colors.ENDC}")

        return True

    def execute_task(self, task: Dict, task_number: int, total_tasks: int) -> bool:
        """Executa uma tarefa individual"""
        task_id = task['id']
        task_type = task['type']

        # Cabeçalho da tarefa
        print(f"{Colors.BOLD}{Colors.BLUE}[{task_number}/{total_tasks}] Executando: {task_id} ({task_type}){Colors.ENDC}")

        # Verifica dependências
        if not self.verify_dependencies(task):
            print(f"{Colors.RED}  -> Erro: Dependências não satisfeitas X{Colors.ENDC}")
            return False

        # Marca como em execução
        self.task_states[task_id] = 'running'

        # Executa a tarefa
        start = time.time()
        success = self.task_executor.execute(task)
        end = time.time()

        execution_time = end - start
        self.task_times[task_id] = execution_time

        # Atualiza estado
        if success:
            self.task_states[task_id] = 'completed'
            print(f"{Colors.GREEN}  -> Tempo: {execution_time:.2f}s{Colors.ENDC}")
            print(f"{Colors.GREEN}  -> Status: COMPLETO OK{Colors.ENDC}")
        else:
            self.task_states[task_id] = 'failed'
            print(f"{Colors.RED}  -> Status: FALHOU X{Colors.ENDC}")

        print()
        return success

    def run(self) -> bool:
        """Executa a simulação completa do pipeline"""
        # Carrega a IR
        if not self.load_ir():
            return False

        # Exibe cabeçalho
        self.print_header()

        # Inicia cronômetro
        self.start_time = time.time()

        # Executa tarefas na ordem definida
        execution_order = self.ir['execution_order']
        total_tasks = len(execution_order)
        tasks_by_id = {task['id']: task for task in self.ir['tasks']}

        for i, task_id in enumerate(execution_order, 1):
            task = tasks_by_id[task_id]
            success = self.execute_task(task, i, total_tasks)

            if not success:
                self.end_time = time.time()
                self.print_summary(success=False)
                return False

        # Finaliza cronômetro
        self.end_time = time.time()

        # Exibe resumo
        self.print_summary(success=True)
        return True

    def print_summary(self, success: bool):
        """Exibe o resumo final da execução"""
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")

        if success:
            print(f"{Colors.BOLD}{Colors.GREEN}EXECUÇÃO CONCLUÍDA COM SUCESSO! OK{Colors.ENDC}")
        else:
            print(f"{Colors.BOLD}{Colors.RED}EXECUÇÃO FALHOU! X{Colors.ENDC}")

        print()

        # Estatísticas
        completed = sum(1 for state in self.task_states.values() if state == 'completed')
        total = len(self.task_states)
        print(f"{Colors.BOLD}Tarefas executadas:{Colors.ENDC} {completed}/{total}")

        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time
            print(f"{Colors.BOLD}Tempo total:{Colors.ENDC} {total_time:.2f}s")

        # Detalhamento por tarefa
        if self.task_times:
            print()
            print(f"{Colors.BOLD}Tempo por tarefa:{Colors.ENDC}")
            for task_id, exec_time in self.task_times.items():
                state = self.task_states[task_id]
                color = Colors.GREEN if state == 'completed' else Colors.RED
                print(f"  {color}• {task_id}: {exec_time:.2f}s ({state}){Colors.ENDC}")

        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print()


def main():
    """Função principal - CLI do simulador"""
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Uso: python simulator.py <arquivo_ir.json>{Colors.ENDC}")
        print(f"{Colors.YELLOW}Exemplo: python simulator.py demo/pipeline_simples.json{Colors.ENDC}")
        sys.exit(1)

    ir_file = sys.argv[1]

    # Cria e executa o simulador
    simulator = PipelineSimulator(ir_file)
    success = simulator.run()

    # Retorna código de saída apropriado
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
