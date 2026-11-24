# CVRP com busca tabu

O repositório reúne experimentos de busca tabu para o Problema de Roteamento de Veículos Capacitados (CVRP).

As instâncias adicionais estão em [`benchmarks/general/`](benchmarks/general/) e [`benchmarks/selected/`](benchmarks/selected/). O material de consulta está em [`references/`](references/).

## Instalação

Na raiz do repositório, use o [uv](https://docs.astral.sh/uv/getting-started/installation/) para criar o ambiente com Python 3.12 e instalar o pacote.

```sh
uv sync --locked
```

## Execução

```sh
uv run cvrp --help
uv run cvrp
uv run cvrp benchmarks/general/A-n33-k5.vrp --seed 1
```

`cvrp` executa a busca tabu com inversões, realocações e trocas. Por padrão, usa a instância `A-n32-k5.vrp`, incluída em [`src/cvrp_tabu_search/data/`](src/cvrp_tabu_search/data/). A saída mostra o melhor custo, o total de iterações e os clientes de cada rota utilizada na ordem de visita. O depósito é implícito nas duas extremidades de cada rota.

Use `--max-iterations` e `--stagnation-limit` para ajustar os critérios de parada. Os padrões são 60 iterações e 30 iterações consecutivas sem melhora. Com `--max-iterations 0`, o comando exibe a solução inicial.

Use `--tabu-tenure-min` e `--tabu-tenure-max` para configurar o intervalo inclusivo de duração tabu, que por padrão vai de 1 a 15. Use valores iguais para fixar a duração ou dois zeros para desativar o bloqueio tabu. Use `--seed` para reproduzir os sorteios.

A CLI também pode ser executada com `uv run python -m cvrp_tabu_search`.

## Desenvolvimento

O pacote vive em [`src/cvrp_tabu_search/`](src/cvrp_tabu_search/).

- [`domain/`](src/cvrp_tabu_search/domain/) contém os modelos de cliente, rota e veículo.
- [`search/`](src/cvrp_tabu_search/search/) reúne o carregamento de instâncias, a representação de soluções, os movimentos de vizinhança e a busca tabu.
- [`cli.py`](src/cvrp_tabu_search/cli.py) lê os argumentos, executa a busca e exibe o resultado.

Os testes acompanham a estrutura do pacote em `tests/domain/` e `tests/search/`, com os testes dos movimentos em `tests/search/moves/` e os da CLI em `tests/test_cli.py`.

Execute os testes com pytest. Use Ruff para lint e formatação e ty para checagem de tipos.

```sh
uv run pytest
uv run ruff check
uv run ruff format --check
uv run ty check
```

Ative os hooks em cada clone. O Ruff verifica o lint e a formatação dos arquivos preparados para commit. O ty analisa o projeto inteiro quando há alterações em código Python ou na configuração do ambiente. O pytest executa a suíte completa antes de o Git gravar um commit de merge local automático.

```sh
uv run --locked pre-commit install
uv run --locked pre-commit run --all-files
uv run --locked pre-commit run --all-files --hook-stage pre-merge-commit
```

## Distribuição

Use `uv build` para gerar o wheel e a distribuição de código-fonte em `dist/`.
