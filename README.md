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
uv run cvrp baseline
uv run cvrp tabu-search
```

`baseline` executa o experimento original com inversões dentro de cada rota. `tabu-search` executa a variante com movimentos entre rotas, intensificação e diversificação. Por padrão, ambos usam a instância `A-n32-k5.vrp`, incluída em [`src/cvrp_tabu_search/data/`](src/cvrp_tabu_search/data/).

Cada execução grava seus CSVs e PNGs em uma subpasta com a data e a hora locais, como `results/2026-11-22_18-34-34/`. Se o nome já estiver em uso, a nova subpasta recebe um sufixo numérico.

Use `--output-dir` em qualquer um dos comandos para substituir a pasta base `results/`. O caminho pode ser absoluto ou relativo ao diretório de trabalho. As pastas são criadas automaticamente.

Use `--tabu-tenure-min` e `--tabu-tenure-max` para configurar o intervalo de duração tabu nos dois comandos. A cada movimento, a busca sorteia uma duração em iterações dentro do intervalo inclusivo, que por padrão vai de 3 a 7. Use dois valores iguais para fixar a duração ou dois zeros para desativar o bloqueio tabu.

Use `--max-iterations`, `--stagnation-limit` e `--time-limit` para ajustar os critérios de parada dos dois comandos. O limite de tempo é opcional, aceita segundos fracionários e vale para cada repetição, contando desde o início da construção da solução inicial. A busca confere o tempo antes de iniciar outra avaliação da vizinhança, então uma avaliação em andamento pode ultrapassar o limite. Com `--time-limit 0`, o experimento retorna a solução inicial. O CSV de execuções registra o valor na coluna `time_limit_s`.

Para usar outra instância CVRP com distâncias `EUC_2D`, informe o arquivo e seu custo ótimo de referência, que serve de alvo no relatório *time-to-target*.

```sh
uv run cvrp tabu-search --instance benchmarks/general/A-n33-k5.vrp --target-cost 661 --max-iterations 100 --stagnation-limit 40 --time-limit 2.5 --tabu-tenure-min 4 --tabu-tenure-max 8 --output-dir resultados/a-n33-k5
```

A CLI também pode ser executada com `uv run python -m cvrp_tabu_search`.

Os resultados usam os prefixos `runs_`, `history_`, `convergence_` e `ttt_`. A variante com movimentos entre rotas inclui `tabu_` antes do nome da instância.

## Desenvolvimento

O pacote vive em [`src/cvrp_tabu_search/`](src/cvrp_tabu_search/).

- [`search/`](src/cvrp_tabu_search/search/) contém os algoritmos e as operações de busca compartilhadas.
- [`experiments/`](src/cvrp_tabu_search/experiments/) executa os experimentos. O pacote [`experiments/reports/`](src/cvrp_tabu_search/experiments/reports/) coordena a geração dos relatórios e reúne os módulos de CSV, gráficos e diretórios de saída.
- `cli.py` recebe os argumentos. `instances.py` carrega os dados e `routes.py` reúne as operações de rota.

Os testes acompanham essa organização em `tests/search/`, `tests/experiments/` e `tests/cli/`. Em `tests/cli/`, os testes dos comandos e dos pontos de entrada ficam em arquivos próprios.

Execute os testes com pytest. Use Ruff para lint e formatação e ty para checagem de tipos.

```sh
uv run pytest
uv run ruff check
uv run ruff format --check
uv run ty check
```

## Distribuição

Use `uv build` para gerar o wheel e a distribuição de código-fonte em `dist/`.
